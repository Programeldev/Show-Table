import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import globals
from utils import setCssStyleForWidget, popLogs
from table import Table
from mysqlconnect import MySQLConnection


class Switcher(Gtk.StackSwitcher):
    stack = Gtk.Stack()

    def __init__(self):
        super().__init__()

        self.table = Table()
        setCssStyleForWidget(self.table, b'''
                                treeview
                                {
                                    margin: 0px 20px 30px 20px;
                                }
                             ''')

        scrollable_window_for_table = Gtk.ScrolledWindow()
        scrollable_window_for_table.set_child(self.table)

        self.tables_frame = Gtk.Frame()
        self.tables_frame.set_vexpand(True)
        self.tables_frame.set_hexpand(True)
        setCssStyleForWidget(self.tables_frame, b'''
                                frame
                                {
                                    margin: 5px;
                                }
                             ''')

        self.tables_frame.set_child(scrollable_window_for_table)

        self.stack.add_titled(self.tables_frame, None, 'Table')

        log_view = Gtk.TextView()
        log_view.set_editable(False)
        log_view.set_cursor_visible(False)
        log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        setCssStyleForWidget(log_view, b'''
                                textview
                                {
                                    font-size: 12pt;
                                    margin: 8px;
                                }
                             ''')

        self.log_text_buffer = Gtk.TextBuffer()
        log_view.set_buffer(self.log_text_buffer)

        scrollable_window_for_log_view = Gtk.ScrolledWindow()
        scrollable_window_for_log_view.set_child(log_view)

        self.log_view_frame = Gtk.Frame()
        self.log_view_frame.set_vexpand(True)
        self.log_view_frame.set_hexpand(True)
        setCssStyleForWidget(self.log_view_frame, b'''
                                frame
                                {
                                    margin: 5px;
                                }
                             ''')
        self.log_view_frame.set_child(scrollable_window_for_log_view)

        self.stack.add_titled(self.log_view_frame, None, 'Log')

        self.set_stack(self.stack)

    def fillTable(self, query: str) -> bool:
        # global _config_entries

        if not query:
            return False

        mysql_conn = MySQLConnection()
        mysql_conn.connect(**globals.config_entries)

        if not mysql_conn.isConnected():
            return False

        column_names = mysql_conn.executeQuery(query)

        if not column_names:
            return False

        list_store = Gtk.ListStore.new([str] * len(column_names))

        for elem in mysql_conn.data_from_db:
            all_to_str = list()

            for elem_to_str in elem:
                all_to_str.append(str(elem_to_str))

            list_store.append(all_to_str)

        self.table.updateTableData(list_store)
        self.table.updateColumns(column_names)

        return True

    def updateLogTextBuffer(self):
        logs = popLogs()

        if not logs:
            self.stack.set_visible_child(self.tables_frame)
            self.log_text_buffer.set_text('', 0)
            return

        self.log_text_buffer.set_text(logs, len(logs))
        self.stack.set_visible_child(self.log_view_frame)
