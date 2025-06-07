import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from shortcuts import shortcuts
from result_list import ResultList

class MainWindow(Gtk.ApplicationWindow):
    app_title = "dircmp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_dir = None
        self.set_default_size(600, 480)
        self.set_title(self.app_title)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.dir_a_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dir_a_box.set_spacing(8)
        self.dir_a_box.set_margin_top(8)
        # self.dir_a_box.set_margin_bottom(8)
        self.dir_a_box.set_margin_start(8)
        self.dir_a_box.set_margin_end(8)

        self.dir_b_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dir_b_box.set_spacing(8)
        self.dir_b_box.set_margin_top(8)
        # self.dir_b_box.set_margin_bottom(8)
        self.dir_b_box.set_margin_start(8)
        self.dir_b_box.set_margin_end(8)
        self.dir_b_box.set_spacing(8)

        self.main_box.append(self.dir_a_box)
        self.main_box.append(self.dir_b_box)
        self.dir_a_bt = self.make_button("A", "select-dir-a")

        self.dir_b_bt = self.make_button("B", "select-dir-b")
        self.dir_a_box.append(self.dir_a_bt);
        self.dir_b_box.append(self.dir_b_bt);
        self.dir_a_entry = Gtk.Entry()
        self.dir_a_entry.set_hexpand(True)
        self.dir_a_box.append(self.dir_a_entry);
        self.dir_b_entry = Gtk.Entry()
        self.dir_b_entry.set_hexpand(True)
        self.dir_b_box.append(self.dir_b_entry);
        
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box.set_margin_start(8)
        self.center_box.set_margin_end(8)
        self.main_box.append(self.center_box)

        self.status_label = Gtk.Label()
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.status_box.set_margin_top(8)
        self.status_box.set_margin_start(8)
        self.status_box.append(self.status_label)
        self.main_box.append(self.status_box)

        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.bottom_box.set_spacing(10)
        self.bottom_box.set_margin_top(10)
        self.bottom_box.set_margin_bottom(10)
        self.bottom_box.set_margin_start(10)
        self.bottom_box.set_margin_end(10)
        self.bottom_box.set_homogeneous(True)
        self.main_box.append(self.bottom_box)

        self.result_list = ResultList()
        sw = Gtk.ScrolledWindow()
        self.center_box.append(sw)
        sw.set_child(self.result_list.list_view)
        self.result_list.list_view.grab_focus()

        self.compare_bt = self.make_button("Compare", "compare-dirs")
        self.bottom_box.append(self.compare_bt)

        self.execute_bt = self.make_button("Execute", "exec-operations")
        self.execute_bt.set_sensitive(False);
        self.bottom_box.append(self.execute_bt)

        self.close_bt = self.make_button("Close", "quit")
        self.bottom_box.append(self.close_bt)

    #     self.header = Gtk.HeaderBar()
    #     self.set_titlebar(self.header)

    #     app = self.get_application()
    #     sm = app.get_style_manager()
    #     sm.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT) ## Adw.ColorScheme.PREFER_DARK
    #     # для стилизации приложения - adwaita
    #     # https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/styles-and-appearance.html


    # def after_init(self):
    #     print('after_init')
    #     self.abort_bt.set_sensitive(False); # this one doesn't work in __init__

    def make_button(self, label, action):
        shortcut = f"({shortcuts[action]})" if action in shortcuts else ""
        bt = Gtk.Button(label=f"{label} {shortcut}")
        bt.set_action_name('app.' + action)
        return bt

    def set_status(self, text):
        self.status_label.set_text(text)

    # def start_calculation(self):
    #     self.calc_bt.set_sensitive(False);
    #     self.abort_bt.set_sensitive(True);
    #     self.open_bt.set_sensitive(False);
    #     self.result_list.clear()

    # def stop_calculation(self):
    #     self.calc_bt.set_sensitive(True);
    #     self.abort_bt.set_sensitive(False);
    #     self.open_bt.set_sensitive(True);
