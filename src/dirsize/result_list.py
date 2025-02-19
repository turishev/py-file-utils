import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject


class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    name = GObject.Property(type=GObject.TYPE_STRING, default="")
    type = GObject.Property(type=GObject.TYPE_STRING, default="")
    size = GObject.Property(type=GObject.TYPE_UINT64, default=0)

    def __init__(self, name, type, size):
        super().__init__()
        self.name = name
        self.type = type
        self.size = size


class FileSizeList():
    def __init__(self):
        self.store = Gio.ListStore(item_type=DataObject)

        factory_type_column = Gtk.SignalListItemFactory()
        factory_type_column.connect("setup", self.setup_type_column)
        factory_type_column.connect("bind", self.bind_type_column)

        factory_size_column = Gtk.SignalListItemFactory()
        factory_size_column.connect("setup", self.setup_size_column)
        factory_size_column.connect("bind", self.bind_size_column)

        factory_name_column = Gtk.SignalListItemFactory()
        factory_name_column.connect("setup", self.setup_name_column)
        factory_name_column.connect("bind", self.bind_name_column)

        type_column = Gtk.ColumnViewColumn(title="type", factory=factory_type_column)
        type_column.set_sorter(Gtk.StringSorter(expression=Gtk.PropertyExpression.new(DataObject, None, "type")))

        size_column = Gtk.ColumnViewColumn(title="size", factory=factory_size_column)
        size_column.set_sorter(Gtk.NumericSorter(expression=Gtk.PropertyExpression.new(DataObject, None, "size")))

        name_column = Gtk.ColumnViewColumn(title="name", factory=factory_name_column)
        name_column.set_sorter(Gtk.StringSorter(expression=Gtk.PropertyExpression.new(DataObject, None, "name")))
        name_column.set_expand(True);

        self.list_view = Gtk.ColumnView()
        self.list_view.append_column(type_column)
        self.list_view.append_column(size_column)
        self.list_view.append_column(name_column)

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
        self.selection = Gtk.SingleSelection(model=self.sort_model)
        self.selection.connect("selection-changed", self.on_sel_changed)

        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)
        self.list_view.sort_by_column(size_column, Gtk.SortType.DESCENDING) # Gtk.SortType.ASCENDING
        self.list_view.connect("activate", self.on_activate);


    def setup_type_column(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_type_column(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(str(obj.type))

    def setup_size_column(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_size_column(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(str(obj.size))

    def setup_name_column(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_name_column(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.name)

    def connect_menu(self, widget, item):
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("pressed", self.on_mouse_right_button_down, item)
        click.connect("released", self.on_mouse_right_button_up, item)
        widget.add_controller(click)

    def on_activate(self): pass

    def on_sel_changed(self, selection, position, item):
        if item is not None:
            #print(f"Selected item: {selection}, {position}, {item}")
            pass
        else:
            #print("No item selected")
            pass

    def append(self, name, type, size):
        self.store.append(DataObject(name, type, size))

    def clear(self):
        self.store.remove_all()

    def on_mouse_right_button_down(self, gesture : Gtk.GestureClick, count: int, \
                                   x : float, y : float, cell : Gtk.ColumnViewCell):
        # print("on_mouse_right_button_down")
        data = cell.get_item()
        print(data)
        self.select_item(data)

    def on_mouse_right_button_up(self, gesture : Gtk.GestureClick, count: int, \
                                 x : float, y : float, cell : Gtk.ColumnViewCell):
        # print("on_mouse_right_button_up")
        data = cell.get_item()
        self.show_item_menu(cell.get_child(), x, y, data)

    def select_item(self, item):
        model = self.selection
        for i in range(model.get_n_items()):
            if model.get_item(i) == item:
                model.select_item(i, True)

    def delete_item(self, item):
        print("delete_item: %s" % item.name)
        model = self.store
        for i in range(model.get_n_items()):
            if model.get_item(i) == item:
                model.remove(i)
                break

    def create_item_menu(self, widget, item):
        gmenu = Gio.Menu()
        if item.type == 'D':
            gmenu.append("dirsize", "app.dirsize-selected-file")
        gmenu.append("open", "app.open-selected-file")
        gmenu.append("delete", "app.delete-selected-file")
        menu = Gtk.PopoverMenu.new_from_model(gmenu)
        menu.set_parent(widget)
        return menu

    def show_item_menu(self, widget, x, y, item):
        print("show_item_menu")
        menu = self.create_item_menu(widget, item)
        menu.set_offset(x, y)
        menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        menu.popup()

    def get_selected_item(self):
        model = self.selection
        sel_inx = model.get_selected()
        return model.get_item(sel_inx)

    def get_selected_name(self):
        return self.get_selected_item().name

    def delete_selected_item(self):
        print("delete_act_handler")
        item = self.get_selected_item()
        print("file:" + item.name)
        self.delete_item(item)
