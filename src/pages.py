import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import globals
from utils import setCssStyleForWidget, reveal
from switcher import Switcher


class TablePage(Gtk.Box):
    old_query = ''
    success_enter_query = False

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.query_entry = Gtk.Entry()
        self.query_entry.set_max_length(500)
        self.query_entry.set_hexpand(True)
        setCssStyleForWidget(
            self.query_entry,
            b'''
            entry
            {
                margin: 3rem 1.5rem 2.5rem 1.5rem;
            }
            '''
        )
        self.query_entry.connect('activate', self.__enterQuery)

        query_entry_revealer = Gtk.Revealer()
        query_entry_revealer.set_child(self.query_entry)
        query_entry_revealer.set_transition_duration(600)
        query_entry_revealer.set_transition_type(Gtk.RevealerTransitionType.SWING_DOWN)
        query_entry_revealer.connect('map', reveal, True)
        query_entry_revealer.connect('unmap', reveal, False)

        search_button = Gtk.Button.new_from_icon_name('system-search-symbolic')
        setCssStyleForWidget(
            search_button,
            b'''
            button
            {
                margin: 2.5rem 0.6rem 2.5rem 0rem;
            }
            '''
        )
        search_button.connect('clicked', self.__enterQuery)

        search_button_revealer = Gtk.Revealer()
        search_button_revealer.set_child(search_button)
        search_button_revealer.set_transition_duration(600)
        search_button_revealer.set_transition_type(Gtk.RevealerTransitionType.SWING_DOWN)
        search_button_revealer.connect('map', reveal, True)
        search_button_revealer.connect('unmap', reveal, False)

        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        horizontal_box.append(query_entry_revealer)
        horizontal_box.append(search_button_revealer)
        self.append(horizontal_box)

        self.switcher = Switcher()
        self.append(self.switcher)
        self.append(self.switcher.stack)

    def __enterQuery(self, obj):
        new_query = self.query_entry.get_text()

        if not new_query:
            return

        if new_query != self.old_query or not self.success_enter_query:
            self.old_query = new_query
            self.success_enter_query = self.switcher.fillTable(new_query)
            self.switcher.updateLogTextBuffer()


class ConfigurationPage(Gtk.Grid):
    entries_revealers: dict[str, Gtk.Entry()]
    entries_label: dict[str, Gtk.Label()]

    def __init__(self):
        super().__init__()

        DURATION = 200
        ANIMATION = Gtk.RevealerTransitionType.SWING_LEFT

        setCssStyleForWidget(
            self,
            b'''
                grid
                {
                    margin: 8rem 5rem 0rem 5rem;
                    border-spacing: 1rem;
                }
            ''')

        self.entries = [
            Gtk.Entry(text='localhost'),
            Gtk.Entry(text='root'),
            Gtk.Entry(),
            Gtk.Entry()
        ]

        revealers = {
            'host':     Gtk.Revealer(),
            'user':     Gtk.Revealer(),
            'password': Gtk.Revealer(),
            'database': Gtk.Revealer()
        }

        # set default input text in entries
        self.__saveConfigEntries(None)

        entries_label = dict()

        for entry, revealer in zip(self.entries, revealers.values()):
            entry.set_hexpand(True)
            entry.set_vexpand(False)
            entry.connect('unmap', self.__saveConfigEntries)
            revealer.set_child(entry)
            revealer.set_transition_duration(DURATION)
            revealer.set_transition_type(ANIMATION)
            revealer.connect('unmap', reveal, False)
            revealer.connect('map', reveal, True)

        # Hide entered input password
        self.entries[2].set_visibility(False)

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
            revealer = Gtk.Revealer()
            revealer.set_child(label)
            revealer.set_transition_duration(DURATION)
            revealer.set_transition_type(ANIMATION)
            revealer.connect('unmap', reveal, False)
            revealer.connect('map', reveal, True)
            entries_label.update({label_text: revealer})

        self.attach(entries_label['IP Address'], 0, 0, 1, 1)
        self.attach(revealers['host'], 1, 0, 2, 1)
        self.attach(entries_label['Database Name'], 0, 1, 1, 1)
        self.attach(revealers['database'], 1, 1, 2, 1)
        self.attach(entries_label['Username'], 0, 2, 1, 1)
        self.attach(revealers['user'], 1, 2, 2, 1)
        self.attach(entries_label['Password'], 0, 3, 1, 1)
        self.attach(revealers['password'], 1, 3, 2, 1)

        self.set_row_spacing(10)
        self.set_column_spacing(10)

    def __saveConfigEntries(self, button):
        globals.config_entries = {}

        for entry, key in zip(self.entries,
                              globals.config_entries_keys):
            globals.config_entries.update({key: entry.get_text()})
