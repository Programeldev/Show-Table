from collections import deque

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Table(Gtk.TreeView):
    cells_renderer = Gtk.CellRendererText()
    columns = deque()

    def __init__(self):
        super().__init__()

        self.props.enable_grid_lines = Gtk.TreeViewGridLines.BOTH

    def updateTableData(self, list_store: Gtk.ListStore):
        self.set_model(list_store)

    def updateColumns(self, new_columns: tuple):
        if not new_columns:
            return

        while len(self.columns):
            self.remove_column(self.columns.popleft())

        for i, column_name in enumerate(new_columns):
            self.columns.append(Gtk.TreeViewColumn(column_name,
                                text=i,
                                cell_renderer=self.cells_renderer))

            self.append_column(self.columns[i])
