from quart import websocket, Quart
import re
import asyncio

app = Quart(__name__)

@app.websocket("/ws")
async def ws():
    await websocket.accept()
    while True:
        msg = await websocket.receive()
        # await test_message(msg)
        await process_message(msg)

def split_process_text(msg):
    line_breaks = re.split(r'\n', msg)
    output = []
    for line in line_breaks:
        space_breaks = re.split(r'\s', line)

        output += [word+" " for word in space_breaks]
        output[-1] += "  \n"
    return output[:-1]

async def process_message(msg):
    response_list = split_process_text(msg)
    for word in response_list:
        await websocket.send(word)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    app.run(port=5000)