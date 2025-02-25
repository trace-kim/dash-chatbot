import traceback
import asyncio
import time
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from ollama import AsyncClient
from utils.langchain.langchain_bot import LangChainBot, HumanMessage, AIMessage
from utils.langchain.agents import *
from utils.text_processing import pdf_base64_to_document

app = FastAPI()

supervisor = SupervisorAgent()

# ExaOneBot = LangChainBot(model="exaone3.5")
# DeepSeekBot = LangChainBot(model="deepseek-r1:8b")
# LlamaBot = LangChainBot(model="llama3.2")

# For testing
# config = {"configurable": {"thread_id": "abc1011"}}

# WebSocket manager to track connections by session ID
class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_text(self, session_id: str, message: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message)
            except WebSocketDisconnect:
                self.disconnect(session_id)
    
    async def broadcast(self, message: str):
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(session_id)

websocket_manager = WebSocketManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket_manager.connect(session_id, websocket)

    try:
        while True:
            # Receive a message from the client
            msg = await websocket.receive_text()
            await stream_llm_response(websocket, msg)
            # await websocket_manager.send_text(session_id, f"Echo: {msg}")

    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
        print(f"Client {session_id} disconnected.")

# Simulate prompt processing
async def process_message(session_id: str, prompt: str):
    response = f"Processed response for: {prompt}"
    await websocket_manager.send_text(session_id, response)

@app.post("/send_message/{session_id}")
async def send_message(session_id: str, message: str):
    await process_message(session_id, message)
    return {"message": "Message sent to WebSocket!"}

# Function to stream the LLM model output and send it at a controlled rate
# async def stream_llm_response(websocket: WebSocket, prompt: str, model="llama3.2", rate_limit=0.15):
async def stream_llm_response(websocket: WebSocket, recv: str, rate_limit=0.15):
    try:
        await supervisor.astream(from_user=recv, websocket=websocket, rate_limit=rate_limit)

        # # Load received query and model name
        # recv_dict = process_user_query(recv)

        # user_id = recv_dict["user_id"]
        # query = recv_dict["query"]
        # model = recv_dict["model"]
        # context = recv_dict["context"]
        # agent = recv_dict["agent"]

        # print(f"My thread_id: {user_id}")
        # config = {"configurable": {"thread_id": user_id}}

        # query = query + "  \nContext: " + "  \n\n".join(context)

        # print(f"Prompt: {query}")
        # if not query.strip():
        #     return
        # print("Message received")

        # input_messages = [HumanMessage(query)]

        # # Async stream from the LLM model
        # LLMBot = BOT_DICT[model]

        # await LLMBot.astream(
        #     message=input_messages,
        #     config=config,
        #     websocket=websocket,
        #     rate_limit=rate_limit
        # )

    except Exception as e:
        print(f"Error streaming LLM response: {e}")
        print(traceback.format_exc())
        error_response = {"response": "An error occurred while generating the response.", "state": "finished"}
        await websocket.send_text(json.dumps(error_response))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
