from agent.ask_human import AskHumanAgent
from agent.tool_call import ToolCallAgent

ask_human_agent = AskHumanAgent()
tool_call_agent = ToolCallAgent()

agent_mapper = {
    AskHumanAgent.name: ask_human_agent,
    ToolCallAgent.name: tool_call_agent,
}


def get_agent_mapper():
    return agent_mapper
