import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from pages import TablePage, ConfigurationPage


class Panels(Gtk.Notebook):
    def __init__(self):
        super().__init__()

        show_table_page = TablePage()
        self.append_page(show_table_page,
                         Gtk.Label(label='Table'))

        configuration_page = ConfigurationPage()
        self.append_page(configuration_page,
                         Gtk.Label(label='Configuration'))
