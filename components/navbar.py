from utils.common_import import *

def DefaultStack():
    return dmc.Stack(
        dmc.NavLink(
            label="New chat",
            leftSection=DashIconify(icon="lucide:plus"),
            active=False,
            variant="light",
            color="violet",
            id="navlink-interactive",
            style={"borderRadius": "1rem"}
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
        )
    ],
    px="calc(1.5625rem* var(--mantine-scale))",
    # style={"paddingInline": "calc(1.5625rem* var(--mantine-scale))"},
    
    )

def ChatNavbar(chat_list):
    return dmc.ScrollArea(
        children=[NavbarMainStack(chat_list)],
        h="100%"
    )