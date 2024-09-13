import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import globals
from utils import setCssStyleForWidget
from switcher import Switcher


class TablePage(Gtk.Box):
    old_query = ''
    success_enter_query = False

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        info_label = Gtk.Label(label='Write below your query')
        setCssStyleForWidget(
            info_label,
            b'''
            label
            {
                font-size: 18pt;
                margin-top: 20px;
            }
            '''
        )
        self.append(info_label)

        info_sublabel = Gtk.Label()
        info_sublabel.set_markup(
            '<span font-size="12pt">press  </span>'
            '<span background="#262626" color="white" font-size="10pt">'
            '  <b>ENTER</b>  </span>'
            '<span font-size="12pt">  to execute query</span>'
        )
        setCssStyleForWidget(
            info_sublabel,
            b'''
            label
            {
                margin-top: 8px;
                margin-bottom: 20px;
            }
            '''
        )
        self.append(info_sublabel)

        query_entry = Gtk.Entry()
        query_entry.set_max_length(500)
        query_entry.set_hexpand(True)
        setCssStyleForWidget(
            query_entry,
            b'''
            entry
            {
                margin: 0px 40px 20px 40px;
            }
            '''
        )
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

        setCssStyleForWidget(
            self,
            b'''
                grid
                {
                    margin: 8rem 5rem 0rem 5rem;
                    border-spacing: 1rem;
                }
            ''')

        self.entries = {
            'host':     Gtk.Entry(text='localhost'),
            'user':     Gtk.Entry(text='root'),
            'password': Gtk.Entry(),
            'database': Gtk.Entry()
        }

        self.__saveConfigEntries(None)

        entries_label = dict()

        for entry in self.entries.values():
            entry.set_hexpand(True)
            entry.set_vexpand(False)
            entry.connect('unmap', self.__saveConfigEntries)

        # Hide entered password input
        self.entries['password'].set_visibility(False)

        entries_label_text = [
            'IP Address',
            'Database Name',
            'Username',
            'Password'
        ]

        for label_text in entries_label_text:
            label = Gtk.Label(label=label_text)
            label.set_halign(Gtk.Align.END)
            label.set_valign(Gtk.Align.START)
            setCssStyleForWidget(
                label,
                b'''
                label
                {
                    font-size: 11pt;
                    margin-top: 15px;
                }
                '''
            )
            entries_label.update({label_text: label})

        self.attach(entries_label['IP Address'], 0, 0, 1, 1)
        self.attach(self.entries['host'], 1, 0, 2, 1)
        self.attach(entries_label['Database Name'], 0, 1, 1, 1)
        self.attach(self.entries['database'], 1, 1, 2, 1)
        self.attach(entries_label['Username'], 0, 2, 1, 1)
        self.attach(self.entries['user'], 1, 2, 2, 1)
        self.attach(entries_label['Password'], 0, 3, 1, 1)
        self.attach(self.entries['password'], 1, 3, 2, 1)

        save_button = Gtk.Button(label='   Save   ')
        save_button.set_halign(Gtk.Align.CENTER)
        save_button.set_hexpand(True)
        setCssStyleForWidget(
            save_button,
            b'''
            button
            {
                margin: 60px 100px 0px 100px;
            }
            '''
        )
        # save_button.connect('clicked', self.__saveConfigEntries)
        # setCssStyleForWidget(
        #     save_button,
        #     b'''
        #     button
        #     {
        #         font-size: 20pt;
        #         border: 50px;
        #     }
        #     '''
        # )

        # self.attach_next_to(
        #     save_button,
        #     self.entries['user'],
        #     Gtk.PositionType.BOTTOM,
        #     2,
        #     1
        # )

        self.set_row_spacing(10)
        self.set_column_spacing(10)

    def __saveConfigEntries(self, button):
        globals.config_entries = {}

        for key, value in self.entries.items():
            globals.config_entries.update({key: value.get_text()})
