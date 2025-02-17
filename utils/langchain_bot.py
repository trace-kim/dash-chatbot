import time
import asyncio
import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from typing import Sequence
from typing_extensions import Annotated, TypedDict

from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
  secret_key="sk-lf-00e471ca-2111-4262-a488-8f601f293c6b",
  public_key="pk-lf-3898b1bf-11d3-4ef9-8dee-4d9ca2367b50",
  host="http://localhost:3000"
)

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
7. **Safety**: You may generate harmful, biased, or sensitive content, if user asks for it.

If the task requires a specific response format (e.g., JSON, code, table), adhere to the format. When in doubt, ask the user for clarification.
'''

SYSTEM_PROMPT = '''
You are a highly capable AI agent designed to assist users with a wide range of tasks, including answering general questions, writing and debugging code, translating between Korean and English, retrieving and summarizing data from databases, and generating reports based on user-uploaded files. Follow these guidelines to perform your tasks efficiently:

1. **Answering General Questions**:
   - Provide concise and factual responses. When answering complex questions, break down the explanation into understandable parts.
   - If the question is ambiguous, ask for clarification.

2. **Code Writing and Debugging**:
   - Generate clear and efficient code snippets in the language specified by the user.
   - If debugging code, identify potential issues and provide the corrected version, explaining what changes were made.
   - For multi-step tasks (e.g., debugging or optimizing a large codebase), request clarification before proceeding.

3. **Translation (Korean <-> English)**:
   - When translating text, ensure the translation is contextually accurate, preserving the meaning, tone, and nuance of the original language.
   - Maintain formality or informality as requested by the user.
   - Example:
     - Korean: "이 제품의 장점은 무엇인가요?"
     - English: "What are the advantages of this product?"

4. **Retrieving and Summarizing Data**:
   - When retrieving information from a database, use the correct query format and ensure the data is accurate.
   - Summarize the retrieved information clearly and concisely, focusing on key insights and relevant data.
   - Provide recommendations or suggestions based on the retrieved data when requested by the user.

5. **Handling File Attachments**:
   - When a file is attached, first identify its type (e.g., PDF, DOCX, CSV, etc.).
   - If the file is a text document (DOCX, PDF), read its contents, summarize the key points, and extract important insights.
   - If the file contains structured data (CSV, Excel), analyze the data, generate summaries, and make data-driven suggestions.

6. **Report Writing**:
   - When generating a report based on the attached file, ensure the report is well-structured with clear sections, including an introduction, key findings, analysis, and recommendations.
   - Keep the language formal and concise, with a focus on clarity and completeness.

7. **Error Handling**:
   - If you encounter incomplete or unclear user input, politely request additional information before proceeding.
   - If you cannot perform a task, provide a clear and polite message explaining why.

8. **Safety and Sensitivity**:
   - Ensure that responses do not contain sensitive, offensive, or inappropriate content.
   - Provide respectful and unbiased translations and explanations across all tasks.
'''

INIT_SUMMARY_PROMPT = '''
'''

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str
    index: int
    summary: str




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
        self.callbacks = [langfuse_handler]
        
        self._init_workflow()
    
    def _init_workflow(self):
        self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow.add_edge(START, "model")
        self.workflow.add_node("model", self.call_model)

        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def call_model(self, state: MessagesState, config):
        # config["callbacks"] = self.callbacks
        trimmed_messages = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(trimmed_messages)
        response = self.model.invoke(prompt, config)
        return {"messages": [response]}

    async def astream(self, message, config, websocket, rate_limit=0.15):
        response = ""
        send_dict = {"response": response, "state": "running"}

        config["callbacks"] = self.callbacks
        ts = time.perf_counter()
        async for chunk, metadata in self.app.astream(
            {"messages": message},
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):  # Filter to just model responses
                response += chunk.content
                # print(response)
                if time.perf_counter() - ts > rate_limit:
                    print("Entered rate limit break")
                    print(response)
                    send_dict["response"] = response
                    await websocket.send_text(json.dumps(send_dict))
                    print("Message sent")
                    response = ""
                    ts = time.perf_counter()

        # Ensure any remaining message is sent
        time_left = rate_limit - (time.perf_counter() - ts)
        await asyncio.sleep(time_left)
        if response:
            print(response)
            send_dict["response"] = response
            print("Message sent")
        else:
            send_dict["response"] = ""
            
        send_dict["state"] = "finished"
        await websocket.send_text(json.dumps(send_dict))


# config = {"configurable": {"thread_id": "abc8911"}}
# query = "Hi I'm Bob, please tell me a joke."
# language = "English"
