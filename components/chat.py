from utils.common_import import *
from components.typography import Title3

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

def _ChatCreator(name, chat_text, chat_id):
    return dmc.Grid([
        dmc.GridCol(_AvatarCreator(name), span=1),
        dmc.GridCol([
            dmc.Stack([
                Title3(name, "dark.4"),
                # dmc.Text(chat_text, id=chat_id),
                dcc.Markdown(chat_text, id=chat_id),
            ],
            pt=10,
            gap="sm")
        ],
        span=11)
    ],
    )

def _Prompt():
    return dmc.Stack([
        dmc.Group([
            dmc.Textarea(
                placeholder="Ask something!",
                autosize=True,
                variant="unstyled",
                minRows=1,
                id="prompt-text"
            )],
            pl="0.5rem",
            grow=True
        ),
        html.Div(
            dmc.Group([
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
            ),
            id="prompt-submit-area"
        ),
    ],
    bg="violet.0",
    style={"border-radius":"1rem"},
    p="0.5rem",
    gap=0
    
    )

def UserChat(username, chat_text, chat_id):
    return _ChatCreator(username, chat_text, chat_id)

def AssistantChat(chat_text, chat_id):
    return _ChatCreator("Assistant", chat_text, chat_id)

def ChatScreen():
    return dmc.Center(
        dmc.Stack([
            DashSocketIO(id='chat-socket', eventNames=["stream"]),
            dcc.Store(data="Do Hwi", id="username"),
            dcc.Store(data="", id="current-stream-id"),
            WebSocket(url="ws://127.0.0.1:5000/ws", id="ws"),
            dmc.Box(
                h="100%",
                w=800,
                children=dmc.Paper(
                    dmc.Stack(
                        children=[
                            # AssistantChat("Hello! How can I help you?"),
                            # UserChat("Do Hwi", "Write me a Python code that makes a cool chatbot."),
                            dmc.Center(
                                Title3("What can I do for you? :)", color="dark.4")
                            ),
                            # dmc.Text("", id="results")
                        ]),
                    withBorder=False,
                    w="98%",
                    id="chat-stack"
                    ),        
            ),
            _Prompt()
        ]),
        pt="10rem"
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
    prevent_initial_call=True,
)
def prompt_submit_pressed(n_clicks, prompt_text, username):
    user_text = prompt_text.replace("\n", "  \n")
    patch = Patch()
    patch["props"]["children"].append(UserChat(username, user_text, chat_id={"type": CHAT_USER_ID_PREFIX, "index": n_clicks}))
    patch["props"]["children"].append(AssistantChat("", chat_id={"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks}))
    
    return patch, "", prompt_text


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
    Input("ws", "message"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "children"),
    prevent_initial_call=True,
)
def update_assistant_response(from_ws, curr_text_list):
    msg = from_ws["data"]
    # Find the last created chat component (with the highest index)
    if len(curr_text_list) > 0:
        # Update the last AssistantChat component
        curr_text_list[-1] = curr_text_list[-1] + " " + msg
    return curr_text_list

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