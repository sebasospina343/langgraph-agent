from __future__ import annotations

import pprint
from typing import Any, Dict, Literal, List

from langchain.tools import tool
from langchain.messages import (

    HumanMessage,
    SystemMessage,
    AnyMessage,
)

from src.AnalysisResult import AnalysisResult
from src.model import get_model
from src.AgentState import AgentState
from src.graph import DocumentAnalysisGraph

class DocumentAnalysisAgent():
    def __init__(self):
        self.model, self.tools_by_name = get_model()
        self.structured_model = self.model.with_structured_output(AnalysisResult)
        self.graph = DocumentAnalysisGraph(self.model, self.tools_by_name)
        self.agent = self.graph.build_agent()

    def build_structured_result_from_conversation(
        self,
        final_state: AgentState,
    ) -> AnalysisResult:
        """
        Use `structured_model = model.with_structured_output(AnalysisResult)`
        on a *clean* prompt (no tool_use/tool_result messages) so Anthropic
        doesn't complain about missing tool_result blocks.
        """

        # 2) Extract final AI answer
        final_answer_msg = None
        for msg in reversed(final_state["messages"]):
            if msg.type == "ai":
                final_answer_msg = msg
                break
        final_answer_text = getattr(final_answer_msg, "content", "") if final_answer_msg else ""

        # 3) Ask the model (with_structured_output) to format into AnalysisResult
        system = SystemMessage(
            content=(
                "You are a formatter for a document analyzer agent.\n"
                "You will receive all analysis information for each type of document."
                "You need to return a JSON object that matches the Pydantic model `AnalysisResult`."
            )
        )

        user = HumanMessage(
            content=(
                f"Extract the information from this text extraction:{final_answer_text}"

            )
        )

        # This returns a AnalysisResult instance (already parsed + validated)
        tmp_result: AnalysisResult = self.structured_model.invoke([system, user])

        # 4) Overwrite llm_calls with the real count from the graph
        result = AnalysisResult(
            cedula_de_ciudadania=tmp_result.cedula_de_ciudadania,
            certificado_laboral=tmp_result.certificado_laboral,
            colilla_de_pago_1=tmp_result.colilla_de_pago_1,
            colilla_de_pago_2=tmp_result.colilla_de_pago_2,
            llm_calls=final_state.get("llm_calls", 0),
        )
        return result


# Create the agent instance at module level for LangGraph
agent = DocumentAnalysisAgent().agent


# ---------- 8) Minimal "main" to test it ----------

if __name__ == "__main__":
    # Single turn example
    init_state: AgentState = {
        "messages": [HumanMessage(content="""
                                    Image1 url: https://res.cloudinary.com/harnon-consulting/image/upload/v1763679163/image_tgmghj.jpg
                                    Image2 url: https://res.cloudinary.com/harnon-consulting/image/upload/v1763681824/certificacion_z2lc87.jpg
                                    Image3 url: https://res.cloudinary.com/harnon-consulting/image/upload/v1763739218/colilla_pxrkkl.jpg
                                    Image4 url: https://res.cloudinary.com/harnon-consulting/image/upload/v1763755622/otra-colilla_l0w69y.jpg
                                    """
                        )],
        "llm_calls": 0,
    }

    # Run the agentic loop (tools + LLM)
    agent = DocumentAnalysisAgent()
    final_state = agent.agent.invoke(init_state)

    # print("\n=== Final conversation (raw state messages) ===")
    # for msg in final_state["messages"]:
    #     print(f"{msg.type.upper()}: {msg.content}")

    # print("\nLLM calls:", final_state["llm_calls"])

    # Now ask the LLM (via with_structured_output) to emit AnalysisResult
    structured = agent.build_structured_result_from_conversation(final_state)


    pprint.pprint(structured.model_dump())
