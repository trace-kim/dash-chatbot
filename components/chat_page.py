from utils.common_import import *
from utils.text_processing import chat_response_parsing
from components.typography import *
from components.chat.filebadge import FileBadge
from components.buttons import SmallDefaultButton
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
    id_loader["type"] += "-loader"
    id_time_taken = copy.deepcopy(chat_id)
    id_time_taken["type"] += "-time"
    if name == "Assistant":
        loader_visible = True
        id_time_taken = copy.deepcopy(chat_id)
        id_time_taken["type"] += "-time"
    else:
        loader_visible = False
    return dmc.Grid([
        dmc.GridCol(_AvatarCreator(name), span=1),
        dmc.GridCol([
            dmc.Stack([
                Title3(name, "dark.4"),
                dmc.Stack(
                    children=[
                        dmc.Stack([
                            dmc.LoadingOverlay(
                                visible=loader_visible,
                                id=id_loader,
                                loaderProps={"type": "dots", "color": "violet", "size": "lg"},
                                style={"align-items":"start", "justify-content": "start"},
                                styles={"overlay": {"background-color": "transparent"}}
                            ),
                            dcc.Markdown(chat_text, id=chat_id),
                        ]),
                        dmc.Space(h=5),
                        dmc.Text("", size="sm", c="gray", id=id_time_taken),
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

def _PromptUploadedFiles():
    return dmc.Group(
        children=[],
        align="flex-start",
        id="uploaded-files-stack"
    )

def _PromptButtons():
    return dmc.Group([
        dmc.Group([
            dcc.Upload(children=[
                dmc.ActionIcon(
                    DashIconify(icon="lucide:upload"),
                    variant="default",
                    color="dark.4",
                    radius="lg",
                    size="lg",
                    id="file-upload-button",
                )
            ],
            multiple=True,
            id="file-upload"),
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
                size="lg",
                id="prompt-submit-button"
            ),
        ],
        justify="flex-end",
        style={"cursor":"text"}
        )],
        justify="space-between",
        id="prompt-submit-area"
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
                        size="lg",
                        id="prompt-text"
                    ),
                    logging=False,
                    id="keyboard-event"

                ),
                ],
                pl="0.5rem",
                grow=True
            ),
            dmc.Space(h=30),
            _PromptButtons(),
            _PromptUploadedFiles(),
        ],
        gap=5,
        w="100%"
        )
    ],
    bg="violet.0",
    style={"border-radius":"1rem"},
    p="0.5rem",
    shadow="sm",
    )

def _PromptSection():
    return dmc.Affix(
        dmc.Stack([
            _Prompt(),

            dmc.Group([
                SmallDefaultButton("코드 및 디버깅", id="coding-button"),
                SmallDefaultButton("텍스트 번역", id="translate-button"),
                SmallDefaultButton("텍스트 요약", id="summarize-button"),
                SmallDefaultButton("파일 분석", id="file-analysis-button"),
            ],
            justify="center"
            ),

            dmc.Space(h="sm")

        ],
        style={"background-color": "white"}
        ),
        position={ "bottom": 0, "right": "calc(50% - 400px)" },
        w=800,
        zIndex=500
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
            dcc.Store(data=[], id="uploaded-file"),
            dcc.Interval(id="response-running-interval", disabled=True, interval=100),
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
                                Title1("How can I help you?", color="dark.4")
                            ),
                            # dmc.Text("", id="results")
                        ]),
                    withBorder=False,
                    w="98%",
                    id="chat-stack"
                    ),        
            ),
            _PromptSection(),
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
    Output("response-running-interval", "disabled"),
    Input("prompt-text", "n_submit"),
    State("prompt-submit-button", "disabled"),
    State("prompt-submit-button", "n_clicks"),
    prevent_initial_call=True
)
def return_pressed_on_prompt_text(n_submit, button_disabled, n_clicks):
    if button_disabled:
        return n_clicks, True
    if n_clicks == None:
        return 1, False
    return n_clicks + 1, False

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
    State('uploaded-file', 'data'),
    prevent_initial_call=True,
)
def prompt_submit_pressed(n_clicks, prompt_text, username, id_list, keyboard_event, model, uploaded_data):
    patch = Patch()
    # If shift key is pressed, just return line break without sending to LLM
    if keyboard_event["shiftKey"]:
        return patch, prompt_text, ""
    # If enter key is pressed with prompt text, render User/Assistant chat UI
    if (not n_clicks is None) and (not {"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks} in id_list):
        user_text = prompt_text.replace("\n", "  \n")
        patch["props"]["children"].append(UserChat(username, user_text, chat_id={"type": CHAT_USER_ID_PREFIX, "index": n_clicks}))
        patch["props"]["children"].append(AssistantChat("", chat_id={"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks}))
    
    send_str = json.dumps({"query": prompt_text, "model": model, "context": uploaded_data})
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
    Output("response-running-interval", "disabled"),
    Output("response-running-interval", "n_intervals"),
    Input("ws", "message"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX, "index": ALL}, "children"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX + "-loader", "index": ALL}, "visible"),
    State("response-running-interval", "n_intervals"),
    prevent_initial_call=True,
)
def update_assistant_response(from_ws, curr_text_list, loader_visibility, n_intervals):
    # Make loader invisible on receiving text response
    loader_visibility[-1] = False
    interval_disabled = False
    
    msg, state = chat_response_parsing(from_ws=from_ws)
    print(msg)
    print(f"Status: {state}")
    # Find the last created chat component (with the highest index)
    if len(curr_text_list) > 0:
        # Update the last AssistantChat component
        # curr_text_list[-1] = curr_text_list[-1] + " " + msg
        curr_text_list[-1] = curr_text_list[-1] + msg
    
    # Set interval disabled if response is finished
    if state == "finished":
        interval_disabled = True
        n_intervals = 0
    return curr_text_list, loader_visibility, interval_disabled, n_intervals

@callback(
    Output({"type": CHAT_ASSISTANT_ID_PREFIX + "-time", "index": ALL}, "children"),
    Input("response-running-interval", "n_intervals"),
    State("response-running-interval", "interval"),
    State({"type": CHAT_ASSISTANT_ID_PREFIX + "-time", "index": ALL}, "children"),
)
def update_response_timer(n_intervals, interval, time_taken_children):
    if not n_intervals:
        return time_taken_children
    time_passed = n_intervals * interval / 1000
    time_taken_children[-1] = "Response time: " + str(time_passed) + " s"
    return time_taken_children

@callback(
    Output('uploaded-file', 'data'),
    Output('uploaded-files-stack', 'children'),
    Input('file-upload', 'contents'),
    State('uploaded-file', 'data'),
    State('file-upload', 'filename'),
    State('uploaded-files-stack', 'children'),
    State({"type": CHAT_ATTACHED_FILE_DELETE_ID_PREFIX, "index": ALL}, 'id'),
    prevent_initial_call=True
)
def update_output(new_file_data, uploaded_data_list, new_file_names, uploaded_file_badges, file_id_list):
    if not file_id_list:
        curr_file_num = 0
    else:
        curr_file_num = file_id_list[-1]["index"] + 1

    uploaded_data_list += new_file_data
    file_badges = [FileBadge(fname, id_num=l+curr_file_num) for l, fname in enumerate(new_file_names)]
    uploaded_file_badges += file_badges
    return uploaded_data_list, uploaded_file_badges

@callback(
    Output('uploaded-files-stack', 'children'),
    Input({"type": CHAT_ATTACHED_FILE_DELETE_ID_PREFIX, "index": ALL}, 'n_clicks'),
    State('uploaded-files-stack', 'children'),
    prevent_initial_call = True,
    allow_duplicate = True,
)
def file_delete_button_clicked(n_clicks, badge_list):
    if all(click is None for click in n_clicks):
        return badge_list
    
    del_badge_id = copy.deepcopy(ctx.triggered_id)
    del_badge_id["type"] = CHAT_ATTACHED_FILE_BADGE_ID_PREFIX
    
    badge_list = [badge for badge in badge_list if del_badge_id != badge["props"]["id"]]
    return badge_list