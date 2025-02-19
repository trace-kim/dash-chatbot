from utils.common_import import *

def Title1(title, color, **kwargs):
    return dmc.Title(title, lh=1.2, order=1, fw=900, c=color, **kwargs)

def Title2(title, color):
    return dmc.Title(title, lh=1.2, order=2, fw=900, c=color)

def Title3(title, color):
    return dmc.Title(title, lh=1.2, order=3, fw=900, c=color)

def TitleChat(title, color, **kwargs):
    return dmc.Title(title, lh=1.2, order=1, fw=900, c=color, fz={"base": 30, "xs":40}, **kwargs)