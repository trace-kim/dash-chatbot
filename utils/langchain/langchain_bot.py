import time
import asyncio
import json

from utils.langchain.common_imports import *


MAX_TOKENS_TRIM = 6000


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
        
        self._init_graph()
    
    def _init_graph(self):
        self.graph_builder = StateGraph(state_schema=MessagesState)
        self.graph_builder.add_edge(START, "model")
        self.graph_builder.add_node("model", self.call_model)

        self.memory = MemorySaver()
        self.graph = self.graph_builder.compile(checkpointer=self.memory)

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
        async for chunk, metadata in self.graph.astream(
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
