import os
import gi
from result_list import FileSizeList
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib, GObject


class MainWindow(Gtk.ApplicationWindow):
    app_title = "dirsize"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_dir = os.getcwd()

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

        self.open_bt = Gtk.Button(label="Select dir")
        self.open_bt.connect("clicked", self.show_open_dialog)
        self.bottom_box.append(self.open_bt)

        self.clac_bt = Gtk.Button(label="Calculate")
        self.clac_bt.connect('clicked', self.calculate)
        self.bottom_box.append(self.clac_bt)

        self.abort_bt = Gtk.Button(label="Abort")
        self.abort_bt.connect('clicked', self.abort)
        self.bottom_box.append(self.abort_bt)

        self.close_bt = Gtk.Button(label="Close")
        self.close_bt.connect('clicked', self.close_app)
        self.bottom_box.append(self.close_bt)

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        self.open_dialog = Gtk.FileDialog.new()
        self.open_dialog.set_title("Select directory")

        app = self.get_application()
        sm = app.get_style_manager()
        sm.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT) ## Adw.ColorScheme.PREFER_DARK
        # для стилизации приложения - adwaita
        # https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/styles-and-appearance.html

    def show_open_dialog(self, _):
        print("open dialog")
        self.open_dialog.select_folder(parent=self, callback=self.open_dialog_open_callback)

    def open_dialog_open_callback(self, dialog, result):
        print("open_dialog_open_callback")
        try:
            dir = dialog.select_folder_finish(result)
            if dir is not None:
                self.root_dir = dir.get_path()
                print(f"dir is {self.root_dir}")
                self.update_title()
        except GLib.Error as error:
            print(f"Error opening file: {error.message}")

    def update_title(self):
        self.set_title(self.app_title + ":" + self.root_dir)

    def set_status(self, text):
        self.status_label.set_text(text)

    def calculate(self, _):
        print("calculate")
        self.set_status("calculation ...")
        self.result_list.clear()
        res = self.get_application().worker.get_dir_size_list(self.root_dir,
                                                              lambda v: self.result_list.append(v[0], v[1]));
        sum_size = 0
        for v in res:
            sum_size += v[1]

        mb = sum_size / 10e+6
        mbs = ""
        if mb > 1:
            if  mb < 1000:
                mbs = "~" + str(round(mb, 1)) + " Mb"
            else:
                mbs = "~" + str(round(mb / 1000, 1)) + " Gb"

        self.set_status("%d bites   %s" % (sum_size, mbs))

    def abort(self, _):
        self.get_application().worker.stop_calculation()
        print("abort")

    def close_app(self, _):
        self.get_application().worker.stop_calculation()
        self.get_application().quit()



class MyApp(Adw.Application):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present() # показываем это окно
