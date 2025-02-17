from utils.common_import import *

def FileBadge(fname, id_num, theme_color="gray", x_color="white"):
    badge_id = {"type": CHAT_ATTACHED_FILE_BADGE_ID_PREFIX, "index": id_num}
    delete_id = {"type": CHAT_ATTACHED_FILE_DELETE_ID_PREFIX, "index": id_num}
    return dmc.Badge(
        fname,
        leftSection=dmc.ActionIcon(
            DashIconify(icon="material-symbols:close"),
            variant="transparent",
            color=x_color,
            size="xs",
            id=delete_id,
        ),
        color=theme_color,
        id=badge_id,
    )