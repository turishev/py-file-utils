#!/bin/env python3

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib

# https://python-gtk-3-tutorial.readthedocs.io/en/latest/application.html

class MainWindow(Gtk.ApplicationWindow):
    app_title = "dir-size"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 250)
        self.set_title(self.app_title)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)


        self.center_box.set_vexpand(True)
        
        self.bottom_box.set_spacing(10)
        self.bottom_box.set_margin_top(10)
        self.bottom_box.set_margin_bottom(10)
        self.bottom_box.set_margin_start(10)
        self.bottom_box.set_margin_end(10)
        self.bottom_box.set_homogeneous(True)

        self.set_child(self.main_box)
        self.main_box.append(self.center_box)
        self.main_box.append(self.bottom_box)

        self.open_bt = Gtk.Button(label="Select dir")
        self.open_bt.connect("clicked", self.show_open_dialog)
        self.bottom_box.append(self.open_bt)
        
        self.clac_bt = Gtk.Button(label="Calculate")
        self.clac_bt.connect('clicked', self.calculate)
        self.bottom_box.append(self.clac_bt)

        self.abort_bt = Gtk.Button(label="Abort")
        self.abort_bt.connect('clicked', self.abort)
        self.bottom_box.append(self.abort_bt)

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        self.open_dialog = Gtk.FileDialog.new()
        self.open_dialog.set_title("Select directory")


        app = self.get_application()
        sm = app.get_style_manager()
        sm.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT) ## Adw.ColorScheme.PREFER_DARK
        # для стилизации приложения - adwaita
        # https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/styles-and-appearance.html


    def show_open_dialog(self, button):
        print("open dialog")
        self.open_dialog.select_folder(parent=self, callback=self.open_dialog_open_callback)

    def open_dialog_open_callback(self, dialog, result):
        print("open_dialog_open_callback")
        try:
            dir = dialog.select_folder_finish(result)
            if dir is not None:
                self.root_dir = dir.get_path()
                print(f"dir is {self.root_dir}")
                self.set_title(self.app_title + ":" + self.root_dir)
        except GLib.Error as error:
            print(f"Error opening file: {error.message}")
            
    def calculate(self, button):
        print("calculate")

    def abort(self, button):
        print("abort")


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present() # показываем это окно


app = MyApp()
app.run(sys.argv)
