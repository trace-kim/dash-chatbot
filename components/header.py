from utils.common_import import *
from components.typography import *

def Brand():
    return dmc.Group(
        dmc.Anchor(
            Title1("TOESA", color="dark.4"),
            href="#",
            underline="never"
            )
        )

def Header():
    return dmc.Stack([
        Brand()
    ],
    justify="center",
    h="100%")
