from langchain.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from typing import List, Literal
from src.AgentState import AgentState
from loguru import logger
from src.prompts import agent_prompt_system

class DocumentAnalysisGraph():
    def __init__(self, model, tools_by_name):
        self.model = model
        self.tools_by_name = tools_by_name

    def llm_node(self, state: AgentState) -> AgentState:
        """
        LLM decides either:
        - answer directly, OR
        - emit tool_calls (which will send us to the tools node)
        """
        system = SystemMessage(
            content=(agent_prompt_system)
        )

        response = self.model.invoke(
            [system] + state["messages"]
        )

        return {
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    def tools_node(self, state: AgentState) -> AgentState:
        """
        Execute any requested tool calls from the last LLM message and
        return ToolMessage objects as new messages.
        """
        last_msg = state["messages"][-1]
        results: List[ToolMessage] = []

        for tool_call in getattr(last_msg, "tool_calls", []):
            tool_name = tool_call["name"]
            args = tool_call["args"]

            
            logger.info(f"Tool name: {tool_name}")
            logger.info(f"Tool args: {args}")

            tool = self.tools_by_name[tool_name]
            observation = tool.invoke(args)

            results.append(
                ToolMessage(
                    content=str(observation),
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            "messages": results,
            "llm_calls": state.get("llm_calls", 0),
        }

    def should_continue(self, state: AgentState) -> Literal["tools", END]:
        """
        Decide if we:
        - go to tools_node (if there are tool_calls), or
        - end the graph (LLM gave final answer)
        """
        last_msg = state["messages"][-1]

        # If LLM wants to use a tool, go to tools node
        if getattr(last_msg, "tool_calls", None):
            logger.info(f"Calling tool...")
            tool_calls = getattr(last_msg, 'tool_calls', None)
            logger.info(f"Tool name: {tool_calls[0]['name']}")
            logger.info(f"Tool args: {tool_calls[0]['args']}")
            return "tools"

        # Otherwise we are done (agent returns final answer)
        return END

    def build_agent(self):
        graph = StateGraph(AgentState)

        # Nodes
        graph.add_node("llm", self.llm_node)
        graph.add_node("tools", self.tools_node)

        # Edges
        graph.add_edge(START, "llm")
        graph.add_conditional_edges(
            "llm",
            self.should_continue,
            ["tools", END],
        )
        graph.add_edge("tools", "llm")  # tool result -> back to LLM

        return graph.compile()


