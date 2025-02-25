import os
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
from dotenv import load_dotenv

load_dotenv()

langfuse_handler = CallbackHandler(
  secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
  public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
  host="http://localhost:3000"
)