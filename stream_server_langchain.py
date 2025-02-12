import asyncio
import time
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from ollama import AsyncClient
from utils.langchain_bot import LangChainBot, HumanMessage, AIMessage

app = FastAPI()
BOT_DICT = {
    "exaone3.5": LangChainBot(model="exaone3.5"),
    "deepseek-r1": LangChainBot(model="deepseek-r1:8b"),
    "llama3.2": LangChainBot(model="llama3.2"),
    "mistral-nemo": LangChainBot(model="mistral-nemo"),
    "gemma2": LangChainBot(model="gemma2"),
    "aya": LangChainBot(model="aya"),
    "phi4": LangChainBot(model="phi4"),
}
# ExaOneBot = LangChainBot(model="exaone3.5")
# DeepSeekBot = LangChainBot(model="deepseek-r1:8b")
# LlamaBot = LangChainBot(model="llama3.2")

# For testing
config = {"configurable": {"thread_id": "abc1011"}}

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
        # Load received query and model name
        recv_dict = json.loads(recv)
        query = recv_dict["query"]
        model = recv_dict["model"]

        print(f"Prompt: {query}")
        if not query.strip():
            return
        print("Message received")

        input_messages = [HumanMessage(query)]

        # Async stream from the LLM model
        send_message = ""
        LLMBot = BOT_DICT[model]

        ts = time.perf_counter()
        async for chunk, metadata in LLMBot.app.astream(
            {"messages": input_messages},
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):  # Filter to just model responses
                send_message += chunk.content
                if time.perf_counter() - ts > rate_limit:
                    print("Entered rate limit break")
                    print(send_message)
                    await websocket.send_text(send_message)
                    print("Message sent")
                    send_message = ""
                    ts = time.perf_counter()

        # Ensure any remaining message is sent
        if send_message:
            time_left = rate_limit - (time.perf_counter() - ts)
            await asyncio.sleep(time_left)
            print(send_message)
            await websocket.send_text(send_message)
            print("Message sent")

    except Exception as e:
        print(f"Error streaming LLM response: {e}")
        await websocket.send_text("An error occurred while generating the response.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
