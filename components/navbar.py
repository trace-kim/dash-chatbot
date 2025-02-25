from utils.common_import import *

def SingleNavLink(label, chat_id, icon_name="material-symbols:chat-outline-rounded", **kwargs):
    return dmc.NavLink(
        label=label,
        leftSection=DashIconify(icon=icon_name),
        active=False,
        variant="light",
        color="violet",
        id={"type": "chat-history", "index": chat_id},
        style={"borderRadius": "1rem"},
        href="/"
    )

def ChatHistoryStack(chat_list):
    children = [
        SingleNavLink(
            label=chat["title"],
            chat_id=str(chat["id"]),
            icon_name="line-md:chat"
        ) for chat in chat_list
    ]
    return dmc.Stack(
        children=children,      
    )
    

def DefaultStack():
    return dmc.Stack(
        dmc.NavLink(
            label="New chat",
            leftSection=DashIconify(icon="lucide:plus"),
            active=False,
            variant="light",
            color="violet",
            id="navlink-interactive",
            style={"borderRadius": "1rem"},
            href="/"
        ),
        mt="var(--mantine-spacing-md)"        
    )
    
def NavbarMainStack(chat_list):
    return dmc.Stack([
        DefaultStack(),
        dmc.Divider(
            label=dmc.Text("Recent Chats"),
            labelPosition="left",
            mt="calc(2.5rem* var(--mantine-scale))",
            mb="calc(0.625rem* var(--mantine-scale))",
        ),
        ChatHistoryStack(chat_list)
    ],
    px="calc(1.5625rem* var(--mantine-scale))",
    # style={"paddingInline": "calc(1.5625rem* var(--mantine-scale))"},
    
    )

def ChatNavbar(chat_list):
    return dmc.ScrollArea(
        children=[NavbarMainStack(chat_list)],
        h="100%"
    )