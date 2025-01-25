#!/bin/env python3

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib, GObject


class DataObject(GObject.GObject):
    #__gtype_name__ = 'DataObject'
    text = GObject.Property(type=str, default=None)

    def __init__(self, text, number):
        super().__init__()
        self.text = text
        self.number = number


class FileSizeList():
    def __init__(self):
        self.store = Gio.ListStore.new(DataObject)
        sel_model = Gtk.SingleSelection.new(self.store)
        self.list_view = Gtk.ColumnView.new(sel_model)

        factory_c1 = Gtk.SignalListItemFactory()
        factory_c1.connect("setup", self._setup_c1)
        factory_c1.connect("bind", self._bind_c1)

        factory_c2 = Gtk.SignalListItemFactory()
        factory_c2.connect("setup", self._setup_c2)
        factory_c2.connect("bind", self._bind_c2)

        self.list_view = Gtk.ColumnView.new(sel_model)
        self.list_view.append_column(Gtk.ColumnViewColumn.new("size", factory_c1))
        self.list_view.append_column(Gtk.ColumnViewColumn.new("name", factory_c2))
        self.list_view.connect ("activate", self._activate_cb);

    def _setup_c1(self, factory, item):
        label = Gtk.Label()
        item.set_child(label)

    def _bind_c1(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.number)

    def _setup_c2(self, factory, item):
        label = Gtk.EditableLabel()
        item.set_child(label)

    def _bind_c2(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.text)
        label.bind_property("text", obj, "text")

    def _activate_cb(self): pass

    def append(self, name, size):
        self.store.append(DataObject(name, str(size)))


class MainWindow(Gtk.ApplicationWindow):
    app_title = "dir-size"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 250)
        self.set_title(self.app_title)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.center_box.set_vexpand(True)
        self.main_box.append(self.center_box)

        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.bottom_box.set_spacing(10)
        self.bottom_box.set_margin_top(10)
        self.bottom_box.set_margin_bottom(10)
        self.bottom_box.set_margin_start(10)
        self.bottom_box.set_margin_end(10)
        self.bottom_box.set_homogeneous(True)
        self.main_box.append(self.bottom_box)

        self.result_list = FileSizeList()
        self.center_box.append(self.result_list.list_view)
        self.result_list.append("xxx", 123)
        self.result_list.append("yyy", 456)

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
