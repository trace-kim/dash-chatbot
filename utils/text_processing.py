import json

def process_LLM_response(response_str:str):
    response_str = response_str.replace("<think>", "---  \n**Thought Process**")
    response_str = response_str.replace("</think>", "---  \n**Response**")
    return response_str

def chat_response_parsing(from_ws):
    data = json.loads(from_ws["data"])
    msg = data["response"]
    state = data["state"]

    msg = process_LLM_response(msg)

    return msg, state