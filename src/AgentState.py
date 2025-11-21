from typing import Annotated, List
from typing_extensions import TypedDict
from langchain.messages import AnyMessage
import operator

class AgentState(TypedDict):
    """
    messages: full conversation (LLM, human, tool msgs)
    llm_calls: how many times we've called the model
    """
    messages: Annotated[List[AnyMessage], operator.add]
    llm_calls: int
