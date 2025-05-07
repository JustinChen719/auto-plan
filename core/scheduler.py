import json

from pydantic import BaseModel, Field

from agent.ask_human import AskHumanAgent
from agent.planner import PlannerAgent
from agent.summary import SummaryAgent
from agent.tool_call import ToolCallAgent
from core.llm import LLMResponseContent
from utils import get_logger

logger = get_logger(__name__)


class Plan(BaseModel):
    agent: str = Field(default="")
    task: str = Field(default="")


class Scheduler:
    # 规划者智能体
    planner: PlannerAgent = None
    # 总结者智能体
    summary: SummaryAgent = None
    # 功能性智能体
    agent_mapper: dict[str, ToolCallAgent] = {}

    # 当前执行状态
    current_plan_num: int = 0
    max_plan_num: int = 3
    need_make_plan: bool = True
    plans: list[Plan] = []
    results: list[str] = []

    finished: bool = False
    failed: bool = False

    def __init__(self):
        ask_human_agent = AskHumanAgent()

        self.agent_mapper = {
            ask_human_agent.name: ask_human_agent,
        }

        self.planner = PlannerAgent(self.agent_mapper)
        self.summary = SummaryAgent()

    def reset_state(self):
        self.current_plan_num = 0
        self.need_make_plan = True
        self.plans.clear()
        self.results.clear()
        self.finished = False
        self.failed = False

    async def make_plan(self, query) -> None:
        plan: LLMResponseContent = await self.planner.run(query)
        try:
            json_content = json.loads(plan.content)
            if "steps" in json_content:
                if not json_content["steps"]:
                    logger.info("🟡 计划中没有需要执行的步骤，很遗憾，也许当前任务无法完成...")
                    self.failed = True
                else:
                    for step in json_content["steps"]:
                        if "agent" in step and "task" in step:
                            self.plans.append(Plan(agent=step["agent"], task=step["task"]))
                            logger.info(f"{len(self.plans)}. {step["agent"]}，{step["task"]}")
            else:
                raise ValueError("制定计划的结果中没有steps字段")

        except json.JSONDecodeError as e:
            logger.error(f"🔴 Json解析制定的计划出现错误：{e}\n{plan.content}")
        except ValueError as e:
            logger.error(f"🔴 数据出现错误，{e}")

    async def run(self, query: str) -> None:
        logger.info("🚀 开始执行...")
        self.reset_state()
        self.planner.reset()
        while not self.finished and not self.failed:
            if self.need_make_plan:
                self.current_plan_num += 1
                if self.current_plan_num > self.max_plan_num:
                    self.failed = True
                    logger.error(f"🔴 制定计划次数超过上限[{self.max_plan_num} 次]，已终止")
                    break

                # 开始制定计划
                await self.make_plan(query=query)
                self.need_make_plan = False

            else:
                # 执行当前计划表
                for plan in self.plans:
                    if plan.agent not in self.agent_mapper:
                        logger.error(f"🔴 规划出现了错误，计划中的智能体 {plan.agent} 不存在")
                        self.failed = True
                        break
                    else:
                        agent: ToolCallAgent = self.agent_mapper[plan.agent]
                        result = await agent.run(query=plan.task)
                        self.results.append(f"智能体：{plan.agent}，任务：{plan.task}，结果：{result}")

                # 判断是否可以结束
                can_finish = await self.planner.juger(query=query, results=self.results)
                if can_finish:
                    self.finished = True
                else:
                    self.need_make_plan = True

                self.plans.clear()
                # self.results.clear()

        if self.failed:
            logger.error("🔴 执行失败")
        else:
            # 开始总结
            await self.summary.run(query=query, results=self.results)
            logger.info("🟢 执行成功")
