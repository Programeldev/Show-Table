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


def getLogs() -> str:
    # global globals.logs

    if not globals.logs:
        return ''

    ret_logs = globals.logs
    globals.logs = str()
    return ret_logs


def appendLog(logs=None):
    # global globals.logs

    if logs is None:
        raise ValueError('Empty log was given.')

    if isinstance(logs, dict):
        raise TypeError('Wrong message variable type.'
                        ' Must be other than dictonary.')
    elif isinstance(logs, (list, tuple)):
        concat_logs = str()

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
