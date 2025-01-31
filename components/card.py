from utils.common_import import *


def Card1(image, title, category):
    return dmc.Paper(
        [
            html.Div(
                [
                    dmc.Text(category, c="white", opacity=0.7, fw=700),
                    dmc.Title(title, lh=1.2, order=3, mt="xs", fw=900, c="white"),
                ]
            ),
            dmc.Button("Read Article", variant="white", color="dark"),
        ],
        shadow="md",
        p="xl",
        radius="md",
        style={
            "backgroundImage": f"url({image})",
            "height": 440,
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
            "alignItems": "flex-start",
            "backgroundSize": "cover",
            "backgroundPosition": "center",
        },
    )

