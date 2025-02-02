import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio, GObject


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
        self.list_view.connect("activate", self.on_activate);

        #self.create_item_actions()


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
        click = Gtk.GestureClick.new()
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
        ''' select item in the SORTED list '''
        model = self.list_view.get_model()
        for i in range(self.store.get_n_items()):
            if model.get_item(i) == item:
                model.select_item(i, True)

    def create_item_menu(self, widget, data):
        gmenu = Gio.Menu.new()
        gmenu.append("something", "app.something")
        menu = Gtk.PopoverMenu.new_from_model(gmenu)
        menu.set_parent(widget)
        return menu

    def show_item_menu(self, widget, x, y, data):
        print("show_item_menu")
        menu = self.create_item_menu(widget, data)
        # menu.set_offset(x, y)
        # menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        menu.popup()

    # def create_item_actions(self):
    #     print("create_item_actions")
    #     def print_something(self, action, param):
    #         print("Something!")

    #     action = Gio.SimpleAction.new("something", None)
    #     action.connect("activate", print_something)
    #     act = self.list_view.insert_action_group("list_actions")
    #     print(act)
    #     self.list_view.add_action(action)
    #     # Here the action is being added to the window, but you could add it to the
    #     # application or an "ActionGroup"

    def delete_item(self):
        print("delete_item")
