from utils.common_import import *
from utils.text_processing import process_LLM_response
from components.typography import Title3
import uuid

def _AvatarCreator(username):
    if username == "Assistant":
        icon = DashIconify(icon="lucide:bot")
    else:
        icon = DashIconify(icon="lucide:user")
    
    return dmc.Avatar(
        icon,
        name=username,
        radius="xl",
        color="initials",
        size="lg",
        variant="light"
    )

def _ChatCreator(name, chat_id, chat_text):
    id_loader = copy.deepcopy(chat_id)
    print(id_loader)
    id_loader["type"] += "-loader"
    if name == "Assistant":
        loader_visible = True
    else:
        loader_visible = False
    return dmc.Grid([
        dmc.GridCol(_AvatarCreator(name), span=1),
        dmc.GridCol([
            dmc.Stack([
                Title3(name, "dark.4"),
                dmc.Stack(
                    children=[
                        dmc.LoadingOverlay(
                            visible=loader_visible,
                            id=id_loader,
                            loaderProps={"type": "dots", "color": "violet", "size": "lg"},
                            style={"align-items":"start", "justify-content": "start"}
                        ),
                        dcc.Markdown(chat_text, id=chat_id),
                    ],
                    pos="relative",
                    mih=50
                )
                # dmc.Text(chat_text, id=chat_id),
            ],
            pt=10,
            gap="sm")
        ],
        span=11)
    ],
    )

def _Prompt():
    return dmc.Paper([
        dmc.Stack([
            dmc.Group([
                EventListener(
                    dmc.Textarea(
                        placeholder="Ask something!",
                        autosize=True,
                        variant="unstyled",
                        minRows=1,
                        id="prompt-text"
                    ),
                    logging=False,
                    id="keyboard-event"

                ),
                ],
                pl="0.5rem",
                grow=True
            ),
            dmc.Group([
                dmc.Group([
                    dcc.Upload(children=[
                        dmc.ActionIcon(
                            DashIconify(icon="lucide:upload"),
                            variant="default",
                            color="dark.4",
                            # radius="lg",
                            id="file-upload-button"
                        )
                    ])
                ],
                justify="flex-start"),
                dmc.Group([
                    dmc.Select(
                        # label="Select Model",
                        id="chat-model-select",
                        value="exaone3.5",
                        data=[
                            {"value": "llama3.2", "label": "llama3.2"},
                            {"value": "mistral-nemo", "label": "mistral-nemo"},
                            {"value": "exaone3.5", "label": "exaone3.5"},
                            {"value": "aya", "label": "aya"},
                            {"value": "gemma2", "label": "gemma2"},
                            {"value": "phi4", "label": "phi4"},
                            {"value": "deepseek-r1", "label": "deepseek-r1"}
                        ],
                        radius="xl",
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="lucide:send"),
                        variant="default",
                        color="dark.4",
                        radius="lg",
                        id="prompt-submit-button"
                    ),
                ],
                justify="flex-end",
                style={"cursor":"text"}
                )],
                justify="space-between",
                id="prompt-submit-area"
            ),
        ],
        gap=0,
        w="100%"
        )
    ],
    bg="violet.0",
    style={"border-radius":"1rem"},
    p="0.5rem",
    shadow="sm",
    )

def UserChat(username, chat_text, chat_id):
    return _ChatCreator(username, chat_text=chat_text, chat_id=chat_id)

def AssistantChat(chat_text, chat_id):
    return _ChatCreator("Assistant", chat_text=chat_text, chat_id=chat_id)

def ChatScreen():
    return dmc.Center(
        dmc.Stack([
            # DashSocketIO(id='chat-socket', eventNames=["stream"]),
            dcc.Store(data="Do Hwi", id="username"),
            dcc.Store(data="", id="current-stream-id"),
            WebSocket(url=CHAT_WEBSOCKET_URL + "/" + str(uuid.uuid4()), id="ws"),
            # WebSocket(url=CHAT_WEBSOCKET_URL, id="ws"),
            dmc.Box(
                h="100%",
                w=800,
                children=dmc.Paper(
                    dmc.Stack(
                        children=[
                            # AssistantChat("Hello! How can I help you?"),
                            # UserChat("Do Hwi", "Write me a Python code that makes a cool chatbot."),
                            dmc.Center(
                                Title3("How can I help you?", color="dark.4")
                            ),
                            # dmc.Text("", id="results")
                        ]),
                    withBorder=False,
                    w="98%",
                    id="chat-stack"
                    ),        
            ),
            _Prompt()
        ], w={"base": "100%", "md": 400, "lg": 800}),
        pt="10rem",
    )

@callback(
    Output("prompt-submit-button", "disabled"),
    Input("prompt-text", "value"),
)
def change_submit_button_status(text):
    if not text:
        return True
    return False

@callback(
    Output("prompt-submit-button", "n_clicks"),
    Input("prompt-text", "n_submit"),
    State("prompt-submit-button", "disabled"),
    State("prompt-submit-button", "n_clicks"),
    prevent_initial_call=True
)
def return_pressed_on_prompt_text(n_submit, button_disabled, n_clicks):
    if button_disabled:
        return n_clicks
    if n_clicks == None:
        return 1
    return n_clicks + 1

@callback(
    Output("chat-stack", "children"),
    Output("prompt-text", "value"),
    Output("ws", "send"),
    Input("prompt-submit-button", "n_clicks"),
    State("prompt-text", "value"),
    State("username", "data"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "id"),
    State("keyboard-event", "event"),
    State("chat-model-select", "value"),
    prevent_initial_call=True,
)
def prompt_submit_pressed(n_clicks, prompt_text, username, id_list, keyboard_event, model):
    patch = Patch()
    # If shift key is pressed, just return line break without sending to LLM
    if keyboard_event["shiftKey"]:
        return patch, prompt_text, ""
    # If enter key is pressed with prompt text, render User/Assistant chat UI
    if (not n_clicks is None) and (not {"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks} in id_list):
        user_text = prompt_text.replace("\n", "  \n")
        patch["props"]["children"].append(UserChat(username, user_text, chat_id={"type": CHAT_USER_ID_PREFIX, "index": n_clicks}))
        patch["props"]["children"].append(AssistantChat("", chat_id={"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks}))
    
    send_str = json.dumps({"query": prompt_text, "model": model})
    return patch, "", send_str


# Callback for focusing prompt textarea when clicked
clientside_callback(
    """
        function(n_clicks) {
            dash_clientside.set_props("prompt-text", {disabled: false});
            setTimeout(function() {
            var textarea = document.getElementById("prompt-text");
            if (textarea) {
                textarea.focus();
            }
            }, 0);  // Delay of 0 milliseconds ensures it runs after DOM update.
            return dash_clientside.no_update;
        }
    """,
    Output("prompt-text", "disabled"),
    Input("prompt-submit-area", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "children"),
    Output({"type": CHAT_ASSISTANT_ID_PREFIX + "-loader", "index": ALL}, "visible"),
    Input("ws", "message"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "children"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX + "-loader", "index": ALL}, "visible"),
    prevent_initial_call=True,
)
def update_assistant_response(from_ws, curr_text_list, loader_visibility):
    # Make loader invisible on receiving text response
    loader_visibility[-1] = False

    msg = from_ws["data"]
    msg = process_LLM_response(msg)
    print(msg)
    # Find the last created chat component (with the highest index)
    if len(curr_text_list) > 0:
        # Update the last AssistantChat component
        # curr_text_list[-1] = curr_text_list[-1] + " " + msg
        curr_text_list[-1] = curr_text_list[-1] + msg
    return curr_text_list, loader_visibility

# clientside_callback(
#     """
#     function(from_ws, curr_text_list) {
#         if (!from_ws || curr_text_list.length === 0) {
#             return curr_text_list;
#         }
        
#         // Extract message from WebSocket and update the last component
#         const newMessage = from_ws.data;
#         console.log(newMessage)
#         curr_text_list[curr_text_list.length - 1] += " " + newMessage;

#         return curr_text_list;
#     }
#     """,
#     Output({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "children"),
#     Input("ws", "message"),
#     State({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "children"),
#     prevent_initial_call=True,
# )


# @callback(
#     Output({"type": CHAT_ASSISTANT_ID_PREFIX, "index": MATCH}, "children"),
#     Input("ws", "message"),
#     State({"type": CHAT_ASSISTANT_ID_PREFIX, "index": MATCH}, "children"),
#     prevent_initial_call=True,
# )
# def update_assistant_response(from_ws, curr_text):
#     msg = from_ws["data"]
#     return curr_text + " " + msg


# Callbacks for text streaming
# @callback(
#     Output("results", "children"),
#     # Input("prompt-submit-button", "n_clicks"),
#     Input("ws", "message"),
#     State("chat-socket", "socketId"),
#     running=[[Output("results", "children"), "", None]],
#     prevent_initial_call=True,
# )
# def display_status(n_clicks, socket_id):
#     if not n_clicks or not socket_id:
#         return no_update, []

#     paragraph = n_clicks["data"]
#     for i, word in enumerate(paragraph.replace("\n", " ").split(" ")):
#         time.sleep(0.05)
#         emit("stream", " " * bool(i) + word, namespace="/", to=socket_id)

#     return paragraph

# clientside_callback(
#     """(word, text) => text + word""",
#     Output("results", "children", allow_duplicate=True),
#     Input("chat-socket", "data-stream"),
#     State("results", "children"),
#     prevent_initial_call=True,
# )

paragraph = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Integer augue eros, tincidunt vitae eros eu, faucibus tempus risus.
Donec ullamcorper velit in arcu fermentum faucibus.
Etiam finibus tortor ac vestibulum dictum. Vestibulum ultricies risus eu lacus luctus pretium.
Duis congue et nisl eu fringilla. Mauris lorem metus, varius eget ex eget, ultrices suscipit est.
Integer nunc risus, auctor posuere vehicula id, rutrum et urna.
Pellentesque gravida, orci id pharetra tempus, nulla neque sagittis elit, condimentum tempor mi velit et urna.
Fusce faucibus ac libero facilisis commodo. Quisque condimentum suscipit mi.
Vivamus augue neque, commodo sagittis mollis sed, mollis in sapien.
Integer cursus et magna nec cursus.
Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.
"""