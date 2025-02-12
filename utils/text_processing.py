def process_LLM_response(response_str:str):
    response_str = response_str.replace("<think>", "---  \n**Thought Process**")
    response_str = response_str.replace("</think>", "---  \n**Response**")
    return response_str