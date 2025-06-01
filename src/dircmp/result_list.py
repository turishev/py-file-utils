import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject

#import utils

class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    name = GObject.Property(type=GObject.TYPE_STRING, default="")
    diff = GObject.Property(type=GObject.TYPE_STRING, default="")
    a_to_b = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    del_a = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    b_to_a = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    del_b = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    type_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    type_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    size_a = GObject.Property(type=GObject.TYPE_UINT64, default=0)
    size_b = GObject.Property(type=GObject.TYPE_UINT64, default=0)
    time_a = GObject.Property(type=GObject.TYPE_DOUBLE, default=0)
    time_b = GObject.Property(type=GObject.TYPE_DOUBLE, default=0)
    owner_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    owner_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    perm_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    perm_b = GObject.Property(type=GObject.TYPE_STRING, default="")

    def __init__(self, name, diff, type_a, type_b, size_a, size_b):#TODO
        super().__init__()
        self.name = name
        self.diff = diff
        self.type_a = type_a
        self.type_b = type_b
        self.size_a = size_a
        self.size_b = size_b

def create_list_column(name, data_field, setup_fn, bind_fn, sorter_type):
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup_fn)
    factory.connect("bind", bind_fn)
    exp = Gtk.PropertyExpression.new(DataObject, None, data_field)
    sorter = Gtk.NumericSorter(expression=exp) if (sorter_type == "numeric") else Gtk.StringSorter(expression=exp) # "string"
    column = Gtk.ColumnViewColumn(title=name, factory=factory)
    column.set_sorter(sorter)
    return column
        
class ResultList():
    def __init__(self):
        self.store = Gio.ListStore(item_type=DataObject)
        self.list_view = Gtk.ColumnView()

        name_col = create_list_column("Name", "name", self.setup_name, self.bind_name, "string")
        name_col.set_expand(True)
        self.list_view.append_column(name_col)
        self.list_view.append_column(create_list_column("Diff", "diff", self.setup_diff, self.bind_diff, "string"))

        self.list_view.append_column(create_list_column("A type", "type_a", self.setup_type_a, self.bind_type_a, "string"))
        self.list_view.append_column(create_list_column("B type", "type_b", self.setup_type_b, self.bind_type_b, "string"))
        self.list_view.append_column(create_list_column("A size", "type_a", self.setup_size_a, self.bind_size_a, "number"))
        self.list_view.append_column(create_list_column("B size", "type_b", self.setup_size_b, self.bind_size_b, "number"))

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
        self.selection = Gtk.SingleSelection(model=self.sort_model)
        # self.selection.connect("selection-changed", self.on_sel_changed)

        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)
    #     self.list_view.sort_by_column(self.size_column, Gtk.SortType.DESCENDING) # Gtk.SortType.ASCENDING
    #     self.list_view.connect("activate", self.on_activate);

        self.store.append(DataObject("name-1", "A", "type-1", "type-2", 123, 456))
        self.store.append(DataObject("name-2", "B", "type-11", "type-22", 1234, 4567))

    
    def setup_name(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_name(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.name)


    def setup_type_a(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_type_a(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.type_a)

    def setup_type_b(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_type_b(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.type_b)

    def setup_size_a(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_size_a(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        #label.set_text(utils.format_size(obj.size_a))
        label.set_text(str(obj.size_a))

    def setup_size_b(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_size_b(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        #label.set_text(utils.format_size(obj.size_b))
        label.set_text(str(obj.size_b))

    def setup_diff(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)
        
    def bind_diff(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.diff)

    def connect_menu(self, widget, item):
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("pressed", self.on_mouse_right_button_down, item)
        click.connect("released", self.on_mouse_right_button_up, item)
        widget.add_controller(click)

    # def on_activate(self): pass

    # def on_sel_changed(self, selection, position, item):
    #     if item is not None:
    #         #print(f"Selected item: {selection}, {position}, {item}")
    #         pass
    #     else:
    #         #print("No item selected")
    #         pass

    # def append(self, name, type, size):
    #     self.store.append(DataObject(name, type, size))
    #     # model = self.selection
    #     # model.select_item(0, True)
    #     self.list_view.scroll_to(0,
    #                              self.name_column,
    #                              flags=Gtk.ListScrollFlags(Gtk.ListScrollFlags.SELECT))

    # def clear(self):
    #     self.store.remove_all()

    def on_mouse_right_button_down(self, gesture : Gtk.GestureClick, count: int,
                                   x : float, y : float, cell : Gtk.ColumnViewCell):
        # print("on_mouse_right_button_down")
        data = cell.get_item()
        print(data)
        # self.select_item(data)

    def on_mouse_right_button_up(self, gesture : Gtk.GestureClick, count: int,
                                 x : float, y : float, cell : Gtk.ColumnViewCell):
        # print("on_mouse_right_button_up")
        data = cell.get_item()
        # self.show_item_menu(cell.get_child(), x, y, data)

    # def select_item(self, item):
    #     model = self.selection
    #     for i in range(model.get_n_items()):
    #         if model.get_item(i) == item:
    #             model.select_item(i, True)

    # def delete_item(self, item):
    #     print("delete_item: %s" % item.name)
    #     model = self.store
    #     for i in range(model.get_n_items()):
    #         if model.get_item(i) == item:
    #             model.remove(i)
    #             break

    # def create_item_menu(self, widget, item):
    #     gmenu = Gio.Menu()
    #     if item.type == 'D':
    #         gmenu.append("dirsize", "app.dirsize-selected-file")
    #     gmenu.append("open", "app.open-selected-file")
    #     gmenu.append("delete", "app.delete-selected-file")
    #     menu = Gtk.PopoverMenu.new_from_model(gmenu)
    #     menu.set_parent(widget)
    #     return menu

    # def show_item_menu(self, widget, x, y, item):
    #     print("show_item_menu")
    #     menu = self.create_item_menu(widget, item)
    #     menu.set_offset(x, y)
    #     menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
    #     menu.popup()

    # def get_selected_item(self):
    #     model = self.selection
    #     sel_inx = model.get_selected()
    #     return model.get_item(sel_inx)

    # def get_selected_name(self):
    #     return self.get_selected_item().name

    # def delete_selected_item(self):
    #     print("delete_act_handler")
    #     item = self.get_selected_item()
    #     print("file:" + item.name)
    #     self.delete_item(item)
