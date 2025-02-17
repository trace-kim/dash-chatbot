from utils.common_import import *

def SmallDefaultButton(text, id):
    return dmc.Button(
        text,
        size="sm",
        radius="xl",
        variant="default",
        # color="violet",
        style={"color": "#696969"},
        id=id
    )