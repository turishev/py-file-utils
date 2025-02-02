import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject


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
        self.store = Gio.ListStore(item_type=DataObject)

        factory_c1 = Gtk.SignalListItemFactory()
        factory_c1.connect("setup", self.setup_c1)
        factory_c1.connect("bind", self.bind_c1)

        factory_c2 = Gtk.SignalListItemFactory()
        factory_c2.connect("setup", self.setup_c2)
        factory_c2.connect("bind", self.bind_c2)

        c1 = Gtk.ColumnViewColumn(title="size", factory=factory_c1)
        c1.set_sorter(Gtk.NumericSorter(expression=Gtk.PropertyExpression.new(DataObject, None, "number")))

        c2 = Gtk.ColumnViewColumn(title="name", factory=factory_c2)
        c2.set_sorter(Gtk.StringSorter(expression=Gtk.PropertyExpression.new(DataObject, None, "text")))
        c2.set_expand(True);

        self.list_view = Gtk.ColumnView()
        self.list_view.append_column(c1)
        self.list_view.append_column(c2)

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
        self.selection = Gtk.SingleSelection(model=self.sort_model)
        self.selection.connect("selection-changed", self.on_sel_changed)

        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)
        self.list_view.sort_by_column(c1, Gtk.SortType.DESCENDING) # Gtk.SortType.ASCENDING
        self.list_view.connect("activate", self.on_activate);

        self.create_actions()


    def setup_c1(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_c1(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(str(obj.number))

    def setup_c2(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_c2(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.text)

    def connect_menu(self, widget, item):
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("pressed", self.on_mouse_right_button_down, item)
        click.connect("released", self.on_mouse_right_button_up, item)
        widget.add_controller(click)

    def on_activate(self): pass

    def on_sel_changed(self, selection, position, item):
        if item is not None:
            print(f"Selected item: {selection}, {position}, {item}")
        else:
            print("No item selected")

    def append(self, name, size):
        self.store.append(DataObject(name, size))

    def clear(self):
        self.store.remove_all()

    def on_mouse_right_button_down(self, gesture : Gtk.GestureClick, count: int, \
                                   x : float, y : float, cell : Gtk.ColumnViewCell):
        print("on_mouse_right_button_down")
        data = cell.get_item()
        print(data)
        self.select_item(data)

    def on_mouse_right_button_up(self, gesture : Gtk.GestureClick, count: int, \
                                 x : float, y : float, cell : Gtk.ColumnViewCell):
        print("on_mouse_right_button_up")
        data = cell.get_item()
        self.show_item_menu(cell.get_child(), x, y, data)

    def select_item(self, item):
        model = self.selection
        for i in range(model.get_n_items()):
            if model.get_item(i) == item:
                model.select_item(i, True)

    def delete_item(self, item):
        print("delete_item: %s" % item.text)
        model = self.store
        for i in range(model.get_n_items()):
            if model.get_item(i) == item:
                model.remove(i)
                break
                
    def create_item_menu(self, widget, data):
        gmenu = Gio.Menu()
        gmenu.append("Delete", "file-list.delete-file")
        menu = Gtk.PopoverMenu.new_from_model(gmenu)
        menu.set_parent(widget)
        return menu

    def show_item_menu(self, widget, x, y, data):
        print("show_item_menu")
        menu = self.create_item_menu(widget, data)
        menu.set_offset(x, y)
        menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        menu.popup()

    def get_selected_item(self):
        model = self.selection
        sel_inx = model.get_selected()
        return model.get_item(sel_inx)

        
    def delete_act_handler(self, action, param):
        print("delete_act_handler")
        item = self.get_selected_item()
        name = item.text
        print("file:" + name)
        self.delete_item(item)

    def create_actions(self):
        print("create_actions")
        delete_act = Gio.SimpleAction(name="delete-file")
        delete_act.connect("activate", self.delete_act_handler)
        action_group = Gio.SimpleActionGroup()
        action_group.add_action(delete_act)
        self.list_view.insert_action_group('file-list', action_group)
