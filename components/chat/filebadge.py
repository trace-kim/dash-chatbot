from utils.common_import import *

def FileBadge(fname, id_num, theme_color="gray", x_color="white"):
    if id_num is None:
        return NoCloseFileBadge(fname, theme_color=theme_color)
    else:
        badge_id = {"type": CHAT_ATTACHED_FILE_BADGE_ID_PREFIX, "fname": fname, "index": id_num}
        delete_id = {"type": CHAT_ATTACHED_FILE_DELETE_ID_PREFIX, "fname": fname, "index": id_num}
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

def NoCloseFileBadge(fname, theme_color="gray"):
    return dmc.Badge(
        fname,
        color=theme_color,
    )