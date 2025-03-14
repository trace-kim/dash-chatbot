import random
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

def _ChatCreator(name, chat_id, chat_text, AdditionalComponent=html.Div("")):
    id_loader = copy.deepcopy(chat_id)
    id_loader["type"] += "-loader"

    markdown_style = {
        'fontSize': '1.125rem',
    }

    # Add loader and response time display for assistant
    if name == "Assistant":
        loader_visible = True
        id_time_taken = copy.deepcopy(chat_id)
        id_time_taken["type"] += "-time"
        StackChildren = [
            dmc.Stack([
                dmc.LoadingOverlay(
                    visible=loader_visible,
                    id=id_loader,
                    loaderProps={"type": "dots", "color": "violet", "size": "lg"},
                    style={"alignItems":"start", "justifyContent": "start"},
                    styles={"overlay": {"backgroundColor": "transparent"}}
                ),
                dcc.Markdown(
                    chat_text,
                    id=chat_id,
                    style=markdown_style
                ),
            ]),
            dmc.Space(h=5),
            dmc.Text("", size="sm", c="gray", id=id_time_taken)
        ]
    # Skip loader and response time display for user chat
    else:
        loader_visible = False
        StackChildren = [
            dmc.Stack([
                dmc.LoadingOverlay(
                    visible=loader_visible,
                    id=id_loader,
                    loaderProps={"type": "dots", "color": "violet", "size": "lg"},
                    style={"alignItems":"start", "justifyContent": "start"},
                    styles={"overlay": {"backgroundColor": "transparent"}}
                ),
                dcc.Markdown(
                    chat_text,
                    id=chat_id,
                    style=markdown_style
                ),
                AdditionalComponent
            ])
        ]
    # return dmc.Grid([
    #     dmc.GridCol(_AvatarCreator(name), span={"base": 2, "xs": 1}),
    #     dmc.GridCol([
    #         dmc.Stack([
    #             Title3(name, "dark.4"),
    #             dmc.Stack(
    #                 children=StackChildren,
    #                 pos="relative",
    #                 mih=50
    #             )
    #             # dmc.Text(chat_text, id=chat_id),
    #         ],
    #         pt=10,
    #         gap="sm")
    #     ],
    #     span={"base": 10, "xs": 11})
    # ],
    # )
    return dmc.Group([
        _AvatarCreator(name),
        dmc.Stack([
                Title3(name, "dark.4"),
                dmc.Stack(
                    children=StackChildren,
                    pos="relative",
                    mih=50
                )
                # dmc.Text(chat_text, id=chat_id),
            ],
            pt=10,
            gap="sm")
    ],
    align="flex-start",
    wrap="nowrap")

def _PromptUploadedFiles():
    return dmc.Group(
        children=[],
        align="flex-start",
        id="uploaded-files-group"
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
                    {"value": "qwen2.5", "label": "qwen2.5"},
                    {"value": "deepseek-r1", "label": "deepseek-r1"}
                ],
                radius="xl",
                comboboxProps={"zIndex": 1000}
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
        justify="space-between"
    )

def _Prompt():
    return dmc.Paper([
        EventListener(
            dmc.Stack([
                dmc.Group([
                    EventListener(
                        dmc.Textarea(
                            "",
                            placeholder="Ask something!",
                            autosize=True,
                            variant="unstyled",
                            minRows=1,
                            maxRows=10,
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
            # w="100%"
            ),
            events=[{"event": "click", "props": ["srcElement.className", "srcElement.innerText"]}],
            logging=False,
            id="prompt-submit-area"
        )
    ],
    bg="violet.0",
    style={"borderRadius":"1rem", "cursor":"text"},
    p="0.5rem",
    shadow="sm",
    w="100%"
    )

def _PromptSection():
    return dmc.Stack([
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
    style={"backgroundColor": "white"}
    )

def UserChat(username, chat_text, chat_id, AdditionalComponent=html.Div("")):
    return _ChatCreator(username, chat_text=chat_text, chat_id=chat_id, AdditionalComponent=AdditionalComponent)

def AssistantChat(chat_text, chat_id):
    return _ChatCreator("Assistant", chat_text=chat_text, chat_id=chat_id)

def ChatScreen():
    return dmc.Stack(
        dmc.Stack([
            # DashSocketIO(id='chat-socket', eventNames=["stream"]),
            dcc.Store(data="Do Hwi", id="username"),
            dcc.Store(data=str(uuid.uuid4()), id="user-id"),
            dcc.Store(data="", id="current-stream-id"),
            dcc.Store(data=[], id="uploaded-file"),
            dcc.Interval(id="response-running-interval", disabled=True, interval=100),
            WebSocket(url=CHAT_WEBSOCKET_URL + "/" + str(uuid.uuid4()), id="ws"),
            # WebSocket(url=CHAT_WEBSOCKET_URL, id="ws"),
            dmc.ScrollArea(
                h="100%",
                maw={"base": "100vw","md": CHAT_MAX_WIDTH},
                w="100%",
                id="chat-scroll-area",
                children=dmc.Paper(
                    dmc.Stack(
                        children=[
                            dmc.Space(h=300),
                            dmc.Center(
                                TitleChat(
                                    "무엇을 도와드릴까요?",
                                    color="dark.4",
                                    style={
                                        "fontFamily": "AppleSDGothic",
                                    },
                                    id="chat-title"
                                )
                            )
                        ],
                        align="stretch",
                        justify="flex-end",
                        id="chat-stack",
                        w="100%"),
                    withBorder=False,
                    w="98%",
                    ),        
            ),
            _PromptSection(),
        ],
        justify="flex-end",
        h="100%",
        maw=CHAT_MAX_WIDTH,
        w="100%",
        ),
        align="center",
        # pt="20vh",
        h="90vh",
        w="100%",
    )

@callback(
    Output("appshell", "navbar"),
    Input("burger-button", "n_clicks"),
    State("appshell", "navbar"),
    prevent_initial_call=True,
)
def toggle_navbar(_, navbar):
    curr_state = navbar["collapsed"]["mobile"]
    navbar["collapsed"] = {"mobile": not curr_state}
    return navbar

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
    State("user-id", "data"),
    prevent_initial_call=True,
)
def prompt_submit_pressed(n_clicks, prompt_text, username, id_list, keyboard_event, model, uploaded_data, user_id):
    patch = Patch()
    # If shift key is pressed, just return line break without sending to LLM
    if keyboard_event["shiftKey"]:
        return patch, prompt_text, ""
    # If enter key is pressed with prompt text, render User/Assistant chat UI
    if (not n_clicks is None) and (not {"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks} in id_list):
        user_text = prompt_text.replace("\n", "  \n")
        
        # Create UI for attached files
        fnames = [data["fname"] for data in uploaded_data]
        AdditionalComp = dmc.Group([FileBadge(fname, id_num=None) for fname in fnames])
        # attached_files_comp = dmc.Group(children=uploaded_files_comp)

        patch.append(UserChat(username, user_text, chat_id={"type": CHAT_USER_ID_PREFIX, "index": n_clicks}, AdditionalComponent=AdditionalComp))
        patch.append(AssistantChat("", chat_id={"type": CHAT_ASSISTANT_ID_PREFIX, "index": n_clicks}))
    
    send_str = json.dumps({"user_id": user_id,"query": prompt_text, "model": model, "context": uploaded_data})
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
    Input("prompt-submit-area", "n_events"),
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
    Output('uploaded-files-group', 'children'),
    Input('file-upload', 'contents'),
    State('uploaded-file', 'data'),
    State('file-upload', 'filename'),
    State('uploaded-files-group', 'children'),
    State({"type": CHAT_ATTACHED_FILE_DELETE_ID_PREFIX, "fname": ALL, "index": ALL}, 'id'),
    prevent_initial_call=True
)
def update_output(new_file_data, uploaded_data_list, new_file_names, uploaded_file_badges, file_id_list):
    if not file_id_list:
        curr_file_num = 0
    else:
        curr_file_num = file_id_list[-1]["index"] + 1

    # Append uploaded files to data store
    new_file_dict_list = [{"fname": new_file_names[l], "fdata": fdata} for l, fdata in enumerate(new_file_data)]
    uploaded_data_list += new_file_dict_list

    # Add file badges for display
    file_badges = [FileBadge(fname, id_num=l+curr_file_num) for l, fname in enumerate(new_file_names)]
    uploaded_file_badges += file_badges
    return uploaded_data_list, uploaded_file_badges

@callback(
    Output('uploaded-files-group', 'children'),
    Output('uploaded-file', 'data'),
    Input({"type": CHAT_ATTACHED_FILE_DELETE_ID_PREFIX, "fname": ALL, "index": ALL}, 'n_clicks'),
    State('uploaded-files-group', 'children'),
    State('uploaded-file', 'data'),
    prevent_initial_call = True,
    allow_duplicate = True,
)
def file_delete_button_clicked(n_clicks, badge_list, uploaded_file_data):
    if all(click is None for click in n_clicks):
        return badge_list, uploaded_file_data
    
    # Delete file badge
    del_badge_id = copy.deepcopy(ctx.triggered_id)
    del_badge_id["type"] = CHAT_ATTACHED_FILE_BADGE_ID_PREFIX
    badge_list = [badge for badge in badge_list if del_badge_id != badge["props"]["id"]]

    # Delete data store
    del_fname = del_badge_id["fname"]
    uploaded_file_data = [fdata for fdata in uploaded_file_data if fdata["fname"] != del_fname]

    return badge_list, uploaded_file_data

@callback(
    Output("prompt-text", "value"),
    Input("coding-button", "n_clicks"),
    Input("translate-button", "n_clicks"),
    Input("summarize-button", "n_clicks"),
    Input("file-analysis-button", "n_clicks"),
    State("prompt-text", "value"),
    prevent_initial_call=True,
)
def prompt_template_button_clicked(n1, n2, n3, n4, prompt_text):
    # Remove already existing prefix
    for _, prefix in CHAT_PROMPT_TEMPLATE_NAMES.items():
        prompt_text = prompt_text.removeprefix(prefix)
    
    # Add new prefix according to button clicked
    if ctx.triggered_id == "coding-button":
        prompt_text = CHAT_PROMPT_TEMPLATE_NAMES["coding"] + prompt_text
    elif ctx.triggered_id == "translate-button":
        prompt_text = CHAT_PROMPT_TEMPLATE_NAMES["translate"] + prompt_text
    elif ctx.triggered_id == "summarize-button":
        prompt_text = CHAT_PROMPT_TEMPLATE_NAMES["summarize"] + prompt_text
    elif ctx.triggered_id == "file-analysis-button":
        prompt_text = CHAT_PROMPT_TEMPLATE_NAMES["file"] + prompt_text
        
    return prompt_text