from utils.common_import import *
from components.main_shell import MainShell

from dash import _dash_renderer

_dash_renderer._set_react_version("18.2.0")

app = Dash(external_stylesheets=dmc.styles.ALL)

socketio = SocketIO(app.server)

app.layout = dmc.MantineProvider([
    dcc.Location(id='url', refresh=False),
    MainShell(),
    ],
    theme= {
        "fontFamily": 'Inter, ',
        "headings": { "fontFamily": 'Inter' },
        "fontFamilyMonospace": 'Monaco, Consolas, Menlo, monospace',
    }
)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=2743)