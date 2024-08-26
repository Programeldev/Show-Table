import sys

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from main_window import MainWindow


class App(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_active)

    def on_active(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


if __name__ == '__main__':
    app = App()
    app.run(sys.argv)
