# Dash extensions version
import time
import uuid
import dash_mantine_components as dmc
from dash_extensions.enrich import Dash, html, callback, clientside_callback, Input, Output, State, dcc, MATCH, ALL
from dash_extensions import WebSocket
from dash import Patch
from dash_iconify import DashIconify
from dash_socketio import DashSocketIO
from flask_socketio import SocketIO, emit

from utils.config import *

# Dash version
# import time
# import uuid
# import dash_mantine_components as dmc
# from dash import Dash, html, callback, clientside_callback, Input, Output, State, dcc, Patch, MATCH
# from dash_iconify import DashIconify
# from dash_socketio import DashSocketIO
# from flask_socketio import SocketIO, emit

# from utils.config import *