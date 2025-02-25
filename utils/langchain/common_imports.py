from langchain_ollama import ChatOllama

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send

from langgraph.graph import START, MessagesState, StateGraph, END
from langgraph.graph.message import add_messages

from typing import Sequence, List, Literal, TypedDict
from typing_extensions import Annotated, TypedDict

from langfuse.callback import CallbackHandler

from utils.langchain.prompts import *

langfuse_handler = CallbackHandler(
  secret_key="sk-lf-00e471ca-2111-4262-a488-8f601f293c6b",
  public_key="pk-lf-3898b1bf-11d3-4ef9-8dee-4d9ca2367b50",
  host="http://localhost:3000"
)