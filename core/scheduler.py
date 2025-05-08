import json

from pydantic import BaseModel, Field

from agent import get_agent_mapper
from agent.planner import PlannerAgent
from agent.summary import SummaryAgent
from agent.react import ReActAgent
from core.llm import LLMResponseContent
from tools import FinishTool
from utils import get_logger

logger = get_logger(__name__)


class Plan(BaseModel):
    id: str = Field(default="")
    agent: str = Field(default="")
    task: str = Field(default="")


class Scheduler:
    # 当前执行状态
    current_plan_num: int = 0
    max_plan_num: int = 3
    need_make_plan: bool = True
    plans: list[Plan] = []
    results: list[str] = []

    finished: bool = False
    failed: bool = False

    def __init__(self):
        # 功能性智能体
        self.agent_mapper: dict[str, ReActAgent] = get_agent_mapper()
        # 规划者智能体
        self.planner = PlannerAgent(self.agent_mapper)
        # 总结者智能体
        self.summary = SummaryAgent()

    def reset_state(self):
        self.current_plan_num = 0
        self.need_make_plan = True
        self.plans.clear()
        self.results.clear()
        self.finished = False
        self.failed = False

    async def make_plan(self, query) -> None:
        response: LLMResponseContent = await self.planner.run(query, self.results)

        # 没有可执行计划，表示当前任务已经完成
        if len(response.tool_calls) == 0:
            logger.warn(f"🟡 计划中没有需要执行的步骤，很遗憾，也许当前任务无法完成...")
            self.failed = True

        # 解析计划列表
        self.plans.clear()
        for plan in response.tool_calls:
            # 判断结束
            if plan.name == FinishTool.name:
                logger.info(f"🟢 当前任务顺利完成")
                self.finished = True
                self.plans.clear()
                return None

            self.plans.append(
                    Plan(
                            id=plan.id,
                            agent=plan.name,
                            task=plan.arguments["task"]
                    )
            )

        # 展示计划列表
        for index, plan in enumerate(self.plans):
            logger.info(f"{index + 1}. {plan.agent}，{plan.task}")
        self.current_plan_num += 1

    async def run(self, query: str) -> None:
        logger.info("🚀 开始执行...")
        self.reset_state()
        self.planner.reset()
        while not self.finished and not self.failed:
            # 判断当前计划是否超出上限
            if self.current_plan_num > self.max_plan_num:
                self.failed = True
                logger.error(f"🔴 制定计划次数超过上限[{self.max_plan_num} 次]，已终止")
                break

            # 开始制定计划
            await self.make_plan(query=query)

            # 执行当前计划表
            for plan in self.plans:
                if plan.agent not in self.agent_mapper:
                    logger.error(f"🔴 规划出现了错误，计划中的智能体 {plan.agent} 不存在")
                    self.failed = True
                    break
                else:
                    agent: ReActAgent = self.agent_mapper[plan.agent]
                    result = await agent.run(query=plan.task)
                    self.planner.add_agent_result(call_id=plan.id, result=result)
                    self.results.append(f"智能体：{plan.agent}，任务：{plan.task}，结果：{result}")

        if self.failed:
            logger.error("🔴 执行失败\n\n")
        else:
            # 开始总结
            await self.summary.run(query=query, results=self.results)
            logger.info("☑️ 执行结束\n\n")
