from utils.common_import import *
from components.header import Header
from components.card import Card1
from components.chat import ChatScreen



data = [
    {
        "image": "https://images.unsplash.com/photo-1508193638397-1c4234db14d8?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=400&q=80",
        "title": "Best forests to visit in North America",
        "category": "NATURE",
    },
    {
        "image": "https://images.unsplash.com/photo-1559494007-9f5847c49d94?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=400&q=80",
        "title": "Hawaii beaches review: better than you think",
        "category": "BEACH",
    },
    {
        "image": "https://images.unsplash.com/photo-1608481337062-4093bf3ed404?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=400&q=80",
        "title": "Mountains at night: 12 best locations to enjoy the view",
        "category": "NATURE",
    },
    {
        "image": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=400&q=80",
        "title": "Best places to visit this winter",
        "category": "TOURISM",
    },
    {
        "image": "https://images.unsplash.com/photo-1582721478779-0ae163c05a60?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=400&q=80",
        "title": "Active volcanos reviews: travel at your own risk",
        "category": "NATURE",
    },
]



def MainShell():
    return dmc.AppShell([
        dmc.AppShellHeader(
            Header(),
            pl="1.5625rem"
            ),
        dmc.AppShellMain([
            
            dmc.Alert(
            "Hi from Dash Mantine Components. You can create some great looking dashboards using me!",
            title="Welcome!",
            color="violet",
            ),

            dmc.Carousel(
                [dmc.CarouselSlide(Card1(d["image"], d["title"], d["category"])) for d in data],
                id="carousel-cards",
                align="center",
                slideSize="50%",
                slideGap="md",
                loop=True,
                nextControlIcon=DashIconify(icon="grommet-icons:form-next", width=30),
                previousControlIcon=DashIconify(icon="grommet-icons:form-previous", width=30),
                autoplay={"delay":2000},
                styles={"control":
                        {
                            "backgroundColor":"transparent",
                            "color":"white",
                            "borderWidth":"0px",
                            "opacity":"0.7"
                        }}

            ),
            ChatScreen(),
            dmc.Container(h=500),
        ])
    ],
    header={"height": 80},
    id="appshell",)