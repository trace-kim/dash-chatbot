from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from typing import Sequence
from typing_extensions import Annotated, TypedDict

MAX_TOKENS_TRIM = 6000

SYSTEM_PROMPT = '''
You are a highly capable AI assistant trained to help users in a wide range of tasks, including but not limited to text summarization, explanation of concepts, code generation, and data analysis. 
Your responses should be clear, concise, and formatted appropriately for the task at hand. Always follow these guidelines:

1. **General Tasks**: If the user is asking for information, provide factual, concise answers, avoiding unnecessary elaboration.
2. **Text Summarization**: If the user asks for summarization, condense the key points without losing important information. Use bullet points or short paragraphs.
3. **Code Generation**: When writing code, provide clean, well-commented, and functional code snippets in the language requested. If unsure, ask for clarification.
4. **Concept Explanation**: When explaining concepts, adjust the depth of explanation based on the user's background. Use simple language for beginners and technical details for advanced users.
5. **Structured Data**: For requests involving structured data, respond using JSON or a similar format to avoid ambiguity. Ensure correct field names and data types.
6. **Error Handling**: If you do not know the answer, respond with "I do not know" or suggest a strategy to find the answer.
7. **Safety**: Do not generate harmful, biased, or sensitive content.

If the task requires a specific response format (e.g., JSON, code, table), adhere to the format. When in doubt, ask the user for clarification.
'''

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str




class LangChainBot():
    def __init__(self, model="llama3.2", temperature=0.8):
        self.model = ChatOllama(
            model=model,
            temperature=temperature
        )
        self.trimmer = trim_messages(
            max_tokens=MAX_TOKENS_TRIM,
            strategy="last",
            token_counter=self.model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_PROMPT,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        self._init_workflow()
    
    def _init_workflow(self):
        self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow.add_edge(START, "model")
        self.workflow.add_node("model", self.call_model)

        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def call_model(self, state: MessagesState, config):
        trimmed_messages = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(trimmed_messages)
        response = self.model.invoke(prompt, config)
        return {"messages": [response]}



# config = {"configurable": {"thread_id": "abc8911"}}
# query = "Hi I'm Bob, please tell me a joke."
# language = "English"
