import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import globals
from utils import setCssStyleForWidget
from switcher import Switcher


class TablePage(Gtk.Box):
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
                    '<span font-size="12pt">  to execute query</span>')
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
