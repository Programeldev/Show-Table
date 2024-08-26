import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from panels import Panels


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title('Show Table')
        self.set_default_size(800, 600)
        self.set_size_request(800, 600)

        headerbar = Gtk.HeaderBar()
        self.set_titlebar(headerbar)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box)

        self.box.append(Panels())
