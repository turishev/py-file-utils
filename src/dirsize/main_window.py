import gi
from result_list import FileSizeList
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib, GObject


class MainWindow(Gtk.ApplicationWindow):
    app_title = "dirsize"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_dir = None
        self.set_default_size(600, 480)
        self.update_title()

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
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

        self.result_list = FileSizeList()
        sw = Gtk.ScrolledWindow()
        self.center_box.append(sw)
        sw.set_child(self.result_list.list_view)
        self.result_list.list_view.grab_focus()

        self.open_bt = Gtk.Button(label="Select dir")
        self.open_bt.set_action_name("app.open-dir")
        self.bottom_box.append(self.open_bt)

        self.calc_bt = Gtk.Button(label="Calculate")
        self.calc_bt.set_action_name("app.calculate-sizes")
        self.bottom_box.append(self.calc_bt)

        self.abort_bt = Gtk.Button(label="Abort")
        self.abort_bt.set_action_name("app.break-calculation")
        self.bottom_box.append(self.abort_bt)

        self.close_bt = Gtk.Button(label="Close")
        self.close_bt.set_action_name("app.quit")
        self.bottom_box.append(self.close_bt)

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        app = self.get_application()
        sm = app.get_style_manager()
        sm.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT) ## Adw.ColorScheme.PREFER_DARK
        # для стилизации приложения - adwaita
        # https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/styles-and-appearance.html

    def update_title(self):
        if self.root_dir is None:
            self.set_title(self.app_title)
        else:
            self.set_title(self.app_title + ": " + self.root_dir)

    def set_root_dir(self, dir):
        self.root_dir = dir
        self.update_title()

    def set_status(self, text):
        self.status_label.set_text(text)
