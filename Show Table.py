import sys
import logging
from collections import deque

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk
    
    import mysql.connector
    from mysql.connector import errorcode

except ImportError as ex:
    print('Missing dependencies!\n', ex)
    print('Check my Github for more informations: ')
    sys.exit(-1)


_config_entries: dict[str, str] = dict()
_logs: str = str()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title('GTK4 App')
        self.set_default_size(800, 600)
        self.set_size_request(800, 600)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box)

        self.box.append(Panels())


class App(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_active)

    def on_active(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


class Panels(Gtk.Notebook):
    def __init__(self):
        super().__init__()

        show_table_page = ShowTablePage()
        self.append_page(show_table_page, 
                         Gtk.Label(label='Table'))

        configuration_page = ConfigurationPage()
        self.append_page(configuration_page,
                         Gtk.Label(label='Configuration'))


class ShowTablePage(Gtk.Box):
    old_query: str = None
    success_enter_query = False

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        info_label = Gtk.Label(label='Write below your query')
        setCssStyleForWidget(info_label, b'''
                                label
                                {
                                    font-size: 18pt;
                                    margin-top: 20px;
                                }
                             ''')
        self.append(info_label)

        info_sublabel = Gtk.Label()
        info_sublabel.set_markup(
                    '<span font-size="12pt">press  </span>'
                    '<span background="#262626" color="white" font-size="10pt">'
                        '  <b>ENTER</b>  </span>'
                    '<span font-size="12pt" overline="single">  to execute query</span>')
        setCssStyleForWidget(info_sublabel, b'''
                                label
                                {
                                    margin-top: 8px;
                                    margin-bottom: 20px;
                                }
                             ''')
        self.append(info_sublabel)

        query_entry = Gtk.Entry()
        query_entry.set_max_length(500)
        query_entry.set_hexpand(True)
        setCssStyleForWidget(query_entry, b'''
                                entry
                                {
                                    margin: 0px 40px 20px 40px;
                                }
                             ''')
        query_entry.connect('activate', self.enterQuery)
        self.append(query_entry)

        self.switcher = Switcher()
        
        self.append(self.switcher)
        self.append(self.switcher.stack)


    def enterQuery(self, entry):
        new_query = entry.get_text()

        if not new_query:
            return

        if new_query != self.old_query or not self.success_enter_query:
            self.old_query = new_query
            self.success_enter_query = self.switcher.fillTable(new_query)
            self.switcher.updateLogTextBuffer()


class ConfigurationPage(Gtk.Grid):
    entries: dict[str, Gtk.Entry()]
    entries_label: dict[str, Gtk.Label()]

    def __init__(self):
        super().__init__()

        info_label = Gtk.Label()
        info_label.set_margin_top(30)
        info_label.set_markup(
                '<span font_size="14pt">Click \'Save\' button'
                    ' or press  </span>'
                '<span background="#262626" color="white" font-size="10pt">'
                    '  <b>ENTER</b>  </span>'
                '<span font_size="14pt">  to save configuration</span>')
        self.attach(info_label, 3, 9, 3, 1)

        self.entries = {'host':     Gtk.Entry(text='localhost'),
                        'user':     Gtk.Entry(text='root'),
                        'password': Gtk.Entry(),
                        'database': Gtk.Entry()}
        
        self.__saveConfigEntries(None)

        entries_label = dict()

        for entry in self.entries.values():
            entry.set_hexpand(True)
            setCssStyleForWidget(entry, b'''
                                    entry
                                    {
                                        margin-right: 40px;
                                        margin-left: 40px;
                                    }
                                 ''')
            entry.connect('activate', self.__saveConfigEntries)

        self.entries['password'].set_visibility(False)        

        entries_label_text = ['IP Address',
                              'Database Name',
                              'Username',
                              'Password']

        for label_text in entries_label_text:
            entries_label.update({label_text: Gtk.Label(label=label_text)})
            setCssStyleForWidget(entries_label[next(reversed(entries_label))],
                                b'''
                                    label
                                    {
                                        font-size: 16pt;
                                        margin-top: 50px;
                                    }
                                 ''')

        self.attach_next_to(entries_label['IP Address'],
                            info_label,
                            Gtk.PositionType.BOTTOM,
                            1, 1)

        self.attach_next_to(entries_label['Database Name'],
                            entries_label['IP Address'],
                            Gtk.PositionType.RIGHT,
                            1, 1)

        self.attach_next_to(self.entries['host'],
                            entries_label['IP Address'],
                            Gtk.PositionType.BOTTOM,
                            1, 1)

        self.attach_next_to(self.entries['database'],
                            entries_label['Database Name'],
                            Gtk.PositionType.BOTTOM,
                            1, 1)

        self.attach_next_to(entries_label['Username'],
                            self.entries['host'],
                            Gtk.PositionType.BOTTOM,
                            1, 1)

        self.attach_next_to(entries_label['Password'],
                            entries_label['Username'],
                            Gtk.PositionType.RIGHT,
                            1, 1)

        self.attach_next_to(self.entries['user'],
                            entries_label['Username'],
                            Gtk.PositionType.BOTTOM,
                            1, 1)

        self.attach_next_to(self.entries['password'],
                            entries_label['Password'],
                            Gtk.PositionType.BOTTOM,
                            1, 1)
        
        save_button = Gtk.Button(label='   Save   ')
        save_button.set_halign(Gtk.Align.CENTER)
        save_button.set_hexpand(True)
        setCssStyleForWidget(save_button, b'''
                                button
                                {
                                    margin: 60px 100px 0px 100px;
                                }
                             ''')
        save_button.connect('clicked', self.__saveConfigEntries)
        setCssStyleForWidget(save_button, b'''
                                button
                                {
                                    font-size: 20pt;
                                    border: 50px;
                                }
                             ''')

        self.attach_next_to(save_button,
                            self.entries['user'],
                            Gtk.PositionType.BOTTOM,
                            2, 1)

        self.set_row_spacing(10)
        self.set_column_spacing(10)


    def __saveConfigEntries(self, button):
        global _config_entries
        _config_entries = dict()

        for key, value in self.entries.items():
            _config_entries.update({key: value.get_text()})


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
        global _config_entries

        if not query:
            return False

        mysql_conn = MySQLConnection()
        mysql_conn.connect(**_config_entries)

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
        logs = getLogs()

        if not logs:
            self.stack.set_visible_child(self.tables_frame)
            self.log_text_buffer.set_text('', 0)
            return

        self.log_text_buffer.set_text(logs, len(logs))
        self.stack.set_visible_child(self.log_view_frame)


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


class MySQLConnection:
    connection: mysql.connector.connection.MySQLConnection
    used_kwargs_for_mysql: dict
    data_from_db: list


    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(MySQLConnection, self).__new__(self)
            self.__clearFields(self)
            
        return self.instance


    def connect(self, **kwargs_for_mysql) -> bool:
        if not kwargs_for_mysql:
            raise ValueError('Keyword parameters for MySQL'
                             ' connection is empty.')

        if kwargs_for_mysql == self.used_kwargs_for_mysql \
           and self.isConnected(): 

            return True

        self.used_kwargs_for_mysql = kwargs_for_mysql

        self.connection = None
        try:
            self.connection = mysql.connector.connect(**kwargs_for_mysql)

        except mysql.connector.Error as err:
            self.__clearFields()

            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                appendLog((err.errno,
                           ': Connection to MySQL server failed, check'
                           ' your username or password.'))

                return False
                    
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                appendLog((err.errno, 
                           ': Connection to database failed, no access'
                           ' or database don\'t exist.'))

                return False
                    
            else:
                appendLog(f'{err.errno}: {err}')
                return False


        if not self.isConnected():
            self.__clearFields()
            appendLog('Connection to MySQL server failed, unknow error.'
                      ' Try again.')

            return False


        return True


    def isConnected(self) -> bool:
        if isinstance(self.connection, 
                      mysql.connector.connection_cext.CMySQLConnection) \
           and self.connection.is_connected():

            return True

        else:
            return False


    def executeQuery(self, query: str, commit: bool = False) -> tuple:
        if not self.isConnected():
            appendLog('Failed to execute query.'
                      ' No connection to MySQL server.')

            return None

        if not query or not isinstance(query, str):
            return None

        cursor: mysql.connector.connection.MySQLCursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.data_from_db = cursor.fetchall()
            column_names = cursor.column_names

            if commit:
                cursor.commit()

        except mysql.connector.Error as err:
            appendLog(err)
            column_names = None

        finally:
            if isinstance(cursor,
                          mysql.connector.connection.MySQLCursor):

                cursor.close()
        

        return column_names


    def close(self):
        if self.isConnected(self):
            self.connection.close()
            self.__clearFields()


    def __clearFields(self):
        self.used_kwargs_for_mysql = dict()
        self.data_from_db = list()


def appendLog(logs = None):
    global _logs

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

        _logs += concat_logs

    else:
        log_str = str(logs)
        
        if log_str[-1] != '\n':
            log_str += '\n'

        _logs += log_str


def getLogs() -> str:
    global _logs

    if not _logs:
        return ''

    ret_logs = _logs
    _logs = str()
    return ret_logs


def setCssStyleForWidget(widget: Gtk.Widget, str_in_bytes: bytes):
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(str_in_bytes)

    style_context = widget.get_style_context()
    style_context.add_provider(css_provider,
                               Gtk.STYLE_PROVIDER_PRIORITY_FALLBACK)


if __name__ == '__main__':
    app = App()
    app.run(sys.argv)
