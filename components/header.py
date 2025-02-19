from utils.common_import import *
from components.typography import *

def Brand():
    return dmc.Group(
        dmc.Anchor(
            Title1("TOESA", color="dark.4"),
            href="#",
            underline="never"
        ),
        justify="flex-start",
        )

def BurgerButton():
    return dmc.Group([
        dmc.ActionIcon(
            DashIconify(icon="lucide:menu", width=50),
            variant="transparent",
            color="dark.4",
            id="burger-button",
            hiddenFrom="md"
        )
    ])

def Header():
    return dmc.Group([
        Brand(),
        BurgerButton(),
    ],
    justify="space-between",
    align="center",
    h="100%"
    )
