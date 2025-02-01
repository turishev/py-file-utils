import os
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib, GObject


class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    text = GObject.Property(type=GObject.TYPE_STRING, default="")
    number = GObject.Property(type=GObject.TYPE_UINT64, default=0)

    def __init__(self, text, number):
        super().__init__()
        self.text = text
        self.number = number


class FileSizeList():
    def __init__(self):
        self.store = Gio.ListStore.new(DataObject)

        factory_c1 = Gtk.SignalListItemFactory()
        factory_c1.connect("setup", self.setup_c1)
        factory_c1.connect("bind", self.bind_c1)

        factory_c2 = Gtk.SignalListItemFactory()
        factory_c2.connect("setup", self.setup_c2)
        factory_c2.connect("bind", self.bind_c2)

        c1 = Gtk.ColumnViewColumn.new("size", factory_c1)
        c1.set_sorter(Gtk.NumericSorter.new(Gtk.PropertyExpression.new(DataObject, None, "number")))

        c2 = Gtk.ColumnViewColumn.new("name", factory_c2)
        c2.set_sorter(Gtk.StringSorter.new(Gtk.PropertyExpression.new(DataObject, None, "text")))
        c2.set_expand(True);

        self.list_view = Gtk.ColumnView.new()
        self.list_view.append_column(c1)
        self.list_view.append_column(c2)

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel.new(self.store, sorter)
        self.selection = Gtk.SingleSelection.new(self.sort_model)
        self.selection.connect("selection-changed", self.on_sel_changed)

        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)
        self.list_view.sort_by_column(c1, Gtk.SortType.DESCENDING) # Gtk.SortType.ASCENDING
        self.list_view.connect("activate", self.activate_cb);

        self.mouse_controller = Gtk.GestureClick.new()
        self.list_view.add_controller(self.mouse_controller)
        self.mouse_controller.set_button(3)
        self.mouse_controller.connect("released", self.on_mouse_right_button_up)

    def setup_c1(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)

    def bind_c1(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(str(obj.number))

    def setup_c2(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.0)
        item.set_child(label)

    def bind_c2(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.text)

    def activate_cb(self): pass

    def on_sel_changed(self, selection, position, item):
        if item is not None:
            print(f"Selected item: {selection}, {position}, {item}")
        else:
            print("No item selected")

    def append(self, name, size):
        self.store.append(DataObject(name, size))

    def clear(self):
        self.store.remove_all()

    def on_mouse_right_button_up(self, press_count, press_x, press_y, user_data):
        print("on_mouse_right_button_up")
        print(self.selection.get_selected())
