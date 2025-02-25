import time
import json
from utils.langchain.common_imports import *
from utils.langchain.langchain_bot import LangChainBot
from utils.text_processing import process_user_query, process_context

from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
  secret_key="sk-lf-00e471ca-2111-4262-a488-8f601f293c6b",
  public_key="pk-lf-3898b1bf-11d3-4ef9-8dee-4d9ca2367b50",
  host="http://localhost:3000"
)


class BaseAgent:
    def __init__(self, model="llama3.2", temperature=0.8):
        self.model = ChatOllama(
            model=model,
            temperature=temperature
        )
        self.callbacks = [langfuse_handler]

    async def ainvoke(self, query_dict: dict, config: dict):
        config["callbacks"] = self.callbacks
        response = await self.app.ainvoke(
            {"context": query_dict["context"], "query": query_dict["query"]},
            config=config
        )

        return response

    async def astream(self, from_user, websocket, rate_limit=0.15):
        agent, recv_dict = self.select_agent(from_user=from_user)

        docs = []
        for context in recv_dict["context"]:
            docs += pdf_base64_to_document(context)
        recv_dict["context"] = docs
        
        config = {"configurable": {"thread_id": recv_dict["user_id"]}}


        # NEEDS FIXING!!!!!
        if recv_dict["agent"] == "general":
            config["callbacks"] = agent.callbacks

            query = recv_dict["query"] + "  \nContext: " + "  \n\n".join(recv_dict["context"])

            print(f"Prompt: {query}")
            if not query.strip():
                return
            print("Message received")

            input_messages = [HumanMessage(query)]

            await self.app.astream(
                message=input_messages,
                config=config,
                websocket=websocket,
                rate_limit=rate_limit
            )



class SummaryState(TypedDict):
    query: str
    response: str
    context: List[str]
    index: int


class SummarizationAgent:
    def __init__(self, model="llama3.2", temperature=0.8):
        self.model = ChatOllama(
            model=model,
            temperature=temperature
        )
        self.callbacks = [langfuse_handler]

        # Initial summary
        summarize_prompt = ChatPromptTemplate(
            [   
                ("system", AGENT_SUMMARY_SYSTEM_PROMPT),
                ("human", AGENT_SUMMARY_INITIAL_PROMPT),
            ]
        )
        refine_prompt = ChatPromptTemplate(
            [
                ("system", AGENT_SUMMARY_SYSTEM_PROMPT),
                ("human", AGENT_SUMMARY_REFINED_PROMPT),
            ]
        )
        final_prompt = ChatPromptTemplate(
            [
                ("system", AGENT_SUMMARY_SYSTEM_PROMPT),
                ("human", AGENT_SUMMARY_FINAL_PROMPT),
            ]
        )

        self.initial_summary_chain = summarize_prompt | self.model | StrOutputParser()
        self.refine_summary_chain = refine_prompt | self.model | StrOutputParser()
        self.final_summary_chain = final_prompt | self.model | StrOutputParser()

        self._init_graph()

    def _init_graph(self):
        graph = StateGraph(SummaryState)
        graph.add_node("generate_initial_summary", self.generate_initial_summary)
        graph.add_node("refine_summary", self.refine_summary)
        graph.add_node("final_summary", self.final_summary)

        graph.add_edge(START, "generate_initial_summary")
        graph.add_conditional_edges("generate_initial_summary", self.should_refine)
        graph.add_conditional_edges("refine_summary", self.should_refine)
        graph.add_edge("final_summary", END)
        self.app = graph.compile()
    
    # We define functions for each node, including a node that generates
    # the initial summary:
    async def generate_initial_summary(self, state: SummaryState, config: RunnableConfig):
        if state["context"]:
            context = state["context"][0]
        else:
            context = ""

        summary = await self.initial_summary_chain.ainvoke(
            {"query": state["query"], "context": context},
            config,
        )
        return {"response": summary, "index": 1}


    # And a node that refines the summary based on the next document
    async def refine_summary(self, state: SummaryState, config: RunnableConfig):
        print("Inside refine")
        content = state["context"][state["index"]]
        summary = await self.refine_summary_chain.ainvoke(
            {"query": state["query"], "existing_answer": state["response"], "context": content},
            config,
        )

        return {"response": summary, "index": state["index"] + 1}

    async def final_summary(self, state: SummaryState, config: RunnableConfig):
        summary = await self.final_summary_chain.ainvoke(
            {"query": state["query"], "existing_answer": state["response"]},
            config,
        )

        return {"response": summary}

    # Here we implement logic to either exit the application or refine
    # the summary.
    def should_refine(self, state: SummaryState) -> Literal["refine_summary", "final_summary"]:
        if state["index"] >= len(state["context"]):
            return "final_summary"
        else:
            return "refine_summary"

    async def ainvoke(self, query_dict: dict, config: dict):
        config["callbacks"] = self.callbacks
        response = await self.app.ainvoke(
            {"context": query_dict["context"], "query": query_dict["query"]},
            config=config
        )

        return response


class CodingState(TypedDict):
    query: str
    response: str
    context: List[str]


class CodingAgent:
    def __init__(self, model="llama3.2", temperature=0.8):
        self.model = ChatOllama(
            model=model,
            temperature=temperature
        )
        self.callbacks = [langfuse_handler]

        self._init_chains()
        self._init_graph()

    def _init_chains(self):
        # Coding prompts
        coding_prompt = ChatPromptTemplate(
            [   
                ("system", AGENT_CODING_SYSTEM_PROMPT),
                ("human", AGENT_CODING_USER_PROMPT),
            ]
        )

        self.coding_chain = coding_prompt | self.model | StrOutputParser()

    def _init_graph(self):
        graph = StateGraph(CodingState)
        graph.add_node("coding", self.coding_tool)
        graph.add_edge(START, "coding")
        graph.add_edge("coding", END)
        self.app = graph.compile()
    
    # We define functions for each node
    async def coding_tool(self, state: CodingState, config: RunnableConfig):
        if state["context"]:
            context = state["context"][0]
        else:
            context = ""

        response = await self.coding_chain.ainvoke(
            {"query": state["query"], "context": context},
            config,
        )
        return {"response": response}

    async def ainvoke(self, query_dict: dict, config: dict):
        config["callbacks"] = self.callbacks
        response = await self.app.ainvoke(
            {"context": query_dict["context"], "query": query_dict["query"]},
            config=config
        )

        return response


BOT_DICT = {
    "exaone3.5": LangChainBot(model="exaone3.5"),
    "deepseek-r1": LangChainBot(model="deepseek-r1:8b"),
    "llama3.2": LangChainBot(model="llama3.2"),
    "mistral-nemo": LangChainBot(model="mistral-nemo"),
    "gemma2": LangChainBot(model="gemma2"),
    "aya": LangChainBot(model="aya"),
    "phi4": LangChainBot(model="phi4"),
    "qwen2.5": LangChainBot(model="qwen2.5-coder:14b")
}

AGENT_DICT = {
    "summarize": SummarizationAgent(model="phi4"),
    "coding": CodingAgent(model="qwen2.5-coder:14b")
}

class SupervisorAgent:
    def __init__(self):
        pass

    def select_agent(self, from_user):
        # Load received query and model name
        recv_dict = process_user_query(from_user)

        if recv_dict["agent"] == "general":
            return BOT_DICT[recv_dict["model"]], recv_dict
        
        return AGENT_DICT[recv_dict["agent"]], recv_dict

    async def astream(self, from_user, websocket, rate_limit=0.15):
        agent, recv_dict = self.select_agent(from_user=from_user)

        docs = []
        for context in recv_dict["context"]:
            docs += process_context(context)
        recv_dict["context"] = docs
        
        config = {"configurable": {"thread_id": recv_dict["user_id"]}}


        # NEEDS FIXING!!!!!
        if recv_dict["agent"] == "general":
            config["callbacks"] = agent.callbacks

            context = [doc.page_content for doc in recv_dict["context"]]
            query = recv_dict["query"] + "  \nContext: " + "  \n\n".join(context)

            print(f"Prompt: {query}")
            if not query.strip():
                return
            print("Message received")

            input_messages = [HumanMessage(query)]

            await agent.astream(
                message=input_messages,
                config=config,
                websocket=websocket,
                rate_limit=rate_limit
            )

        else:
            agent_response = await agent.ainvoke(recv_dict, config=config)
            
            response = agent_response["response"]
            send_dict = {"response": response, "state": "finished"}

            await websocket.send_text(json.dumps(send_dict))

        # config["callbacks"] = self.callbacks
        # ts = time.perf_counter()
        # async for chunk, metadata in self.graph.astream(
        #     {"messages": message},
        #     config,
        #     stream_mode="messages",
        # ):
        #     if isinstance(chunk, AIMessage):  # Filter to just model responses
        #         response += chunk.content
        #         # print(response)
        #         if time.perf_counter() - ts > rate_limit:
        #             print("Entered rate limit break")
        #             print(response)
        #             send_dict["response"] = response
        #             await websocket.send_text(json.dumps(send_dict))
        #             print("Message sent")
        #             response = ""
        #             ts = time.perf_counter()

        # # Ensure any remaining message is sent
        # time_left = rate_limit - (time.perf_counter() - ts)
        # await asyncio.sleep(time_left)
        # if response:
        #     print(response)
        #     send_dict["response"] = response
        #     print("Message sent")
        # else:
        #     send_dict["response"] = ""

        # send_dict["state"] = "finished"
        # await websocket.send_text(json.dumps(send_dict))
