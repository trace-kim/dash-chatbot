# Dash extensions version
import time
import uuid
import json
import copy
import dash_mantine_components as dmc
from dash_extensions.enrich import Dash, html, callback, clientside_callback, Input, Output, State, dcc, MATCH, ALL, ctx
from dash_extensions import WebSocket, Keyboard, EventListener
from dash import Patch, ClientsideFunction
from dash_iconify import DashIconify
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