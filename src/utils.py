import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import globals


def setCssStyleForWidget(widget: Gtk.Widget, str_in_bytes: bytes):
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(str_in_bytes)

    style_context = widget.get_style_context()
    style_context.add_provider(css_provider,
                               Gtk.STYLE_PROVIDER_PRIORITY_FALLBACK)


def popLogs() -> str:
    if not globals.logs:
        return ''

    ret_logs = globals.logs
    globals.logs = ''
    return ret_logs


def appendLog(logs=None):
    if logs is None:
        raise ValueError('Empty log was given.')

    if not isinstance(logs, (str, list, tuple)):
        raise TypeError('Wrong log variable type,\n'
                        ' only str, list or tuple.')
    elif isinstance(logs, (list, tuple)):
        concat_logs = ''

        for log in logs:
            log_str = str(log)

            if log_str[-1] != '\n':
                log_str += '\n'

            concat_logs += log_str

        globals.logs += concat_logs
    else:
        log_str = str(logs)
        if log_str[-1] != '\n':
            log_str += '\n'

        globals.logs += log_str


def reveal(revealer, show):
    revealer.set_reveal_child(show)
