import gi
from time import localtime, strftime


gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject

#import utils

class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    name = GObject.Property(type=GObject.TYPE_STRING, default="")
    diff = GObject.Property(type=GObject.TYPE_STRING, default="")
    a_to_b = GObject.Property(type=GObject.TYPE_UINT, default=0)
    del_a = GObject.Property(type=GObject.TYPE_UINT, default=0)
    b_to_a = GObject.Property(type=GObject.TYPE_UINT, default=0) # use INT instead BOOLEAN for sake of sort support
    del_b = GObject.Property(type=GObject.TYPE_UINT, default=0) # use INT instead BOOLEAN for sake of sort support
    type_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    type_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    size_a = GObject.Property(type=GObject.TYPE_INT64, default=-1)
    size_b = GObject.Property(type=GObject.TYPE_INT64, default=-1)
    time_a = GObject.Property(type=GObject.TYPE_DOUBLE, default=0)
    time_b = GObject.Property(type=GObject.TYPE_DOUBLE, default=0)
    owner_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    owner_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    # perm_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    # perm_b = GObject.Property(type=GObject.TYPE_STRING, default="")

    def __init__(self, name, diff, type_a, type_b, size_a, size_b, time_a, time_b, owner_a='', owner_b=''):
        super().__init__()
        self.name = name
        self.diff = diff
        self.type_a = type_a
        self.type_b = type_b
        self.size_a = size_a
        self.size_b = size_b
        self.owner_a = owner_a
        self.owner_b = owner_b
        self.time_a = time_a
        self.time_b = time_b

def _format_time(tm):
    return strftime("%Y-%m-%d %H:%M:%S", localtime(tm))

def _create_list_column(name, data_field, setup_fn, bind_fn, sorter_type):
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup_fn)
    factory.connect("bind", bind_fn)
    exp = Gtk.PropertyExpression.new(DataObject, None, data_field)

    if sorter_type == "str": sorter = Gtk.StringSorter(expression=exp)
    elif sorter_type == "num": sorter = Gtk.NumericSorter(expression=exp)
    else: sorter = None

    column = Gtk.ColumnViewColumn(title=name, factory=factory)
    column.set_sorter(sorter)
    return column

class ResultList():
    def __init__(self):
        self.store = Gio.ListStore(item_type=DataObject)
        self.list_view = Gtk.ColumnView()

        name_col = _create_list_column("Name", "name", self.setup_name, self.bind_name, "str")
        name_col.set_expand(True)
        self.list_view.append_column(name_col)
        self.list_view.append_column(_create_list_column("Diff", "diff", self.setup_diff, self.bind_diff, "str"))
        self.list_view.append_column(_create_list_column("A->B", "a_to_b", self.setup_a_to_b, self.bind_a_to_b, "num"))
        self.list_view.append_column(_create_list_column("Del A", "del_a", self.setup_del_a, self.bind_del_a, "num"))
        self.list_view.append_column(_create_list_column("B->A", "b_to_a", self.setup_b_to_a, self.bind_b_to_a, "num"))
        self.list_view.append_column(_create_list_column("Del B", "del_b", self.setup_del_b, self.bind_del_b, "num"))

        self.list_view.append_column(_create_list_column("A type", "type_a", self.setup_type_a, self.bind_type_a, "str"))
        self.list_view.append_column(_create_list_column("B type", "type_b", self.setup_type_b, self.bind_type_b, "str"))
        self.list_view.append_column(_create_list_column("A size", "size_a", self.setup_size_a, self.bind_size_a, "num"))
        self.list_view.append_column(_create_list_column("B size", "size_b", self.setup_size_b, self.bind_size_b, "num"))
        self.list_view.append_column(_create_list_column("A time", "time_a", self.setup_time_a, self.bind_time_a, "num"))
        self.list_view.append_column(_create_list_column("B time", "time_b", self.setup_time_b, self.bind_time_b, "num"))
        self.list_view.append_column(_create_list_column("A owner", "owner_a", self.setup_owner_a, self.bind_owner_a, "str"))
        self.list_view.append_column(_create_list_column("B owner", "owner_b", self.setup_owner_b, self.bind_owner_b, "str"))

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
        self.selection = Gtk.SingleSelection(model=self.sort_model)
        # self.selection.connect("selection-changed", self.on_sel_changed)

        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)
    #     self.list_view.sort_by_column(self.size_column, Gtk.SortType.DESCENDING) # Gtk.SortType.ASCENDING
    #     self.list_view.connect("activate", self.on_activate);

        self.store.append(DataObject("name-2", "B", "type-11", "type-22", -10000, 4567, 123.456, 121.456, "aaa", "bbb"))
        self.store.append(DataObject("name-1", "A", "type-1", "type-2", 123, 456, 1761235050.4936545, 123.456))
        self.store.append(DataObject("name-2", "B", "type-11", "type-22", 1234, 4567, 123.456, 123.456))
        self.store.append(DataObject("name-2", "B", "type-11", "type-22", -1, 444, 1741622985.4395833, 123.456))
        self.store.append(DataObject("name-2", "B", "type-11", "type-22", -10, 456, 12.456, 123.456))

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
        label.set_text(str(obj.size_a) if obj.size_a >= 0 else '') # -1 is size unknown

    def setup_size_b(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_size_b(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(str(obj.size_b) if obj.size_b >= 0 else '')# -1 is size unknown

    def setup_diff(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_diff(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.diff)

    def setup_owner_a(self, factory, item):
        label = Gtk.Label()
        # label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_owner_a(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.owner_a)

    def setup_owner_b(self, factory, item):
        label = Gtk.Label()
        # label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_owner_b(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(obj.owner_b)

    def setup_time_a(self, factory, item):
        label = Gtk.Label()
        # label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_time_a(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(_format_time(obj.time_a))

    def setup_time_b(self, factory, item):
        label = Gtk.Label()
        # label.set_xalign(0.5)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_time_b(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(_format_time(obj.time_b))

    def setup_a_to_b(self, factory, item):
        def on_toogle(_):
            item.get_item().a_to_b = 0 if item.get_item().a_to_b == 1 else 1

        cb = Gtk.CheckButton()
        item.set_child(cb)
        cb.connect('toggled', on_toogle)
        #self.connect_menu(cb, item)

    def bind_a_to_b(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        cb.set_active(obj.a_to_b > 0)

    def setup_b_to_a(self, factory, item):
        def on_toogle(_):
            item.get_item().b_to_a = 0 if item.get_item().b_to_a == 1 else 1

        cb = Gtk.CheckButton()
        cb.connect('toggled', on_toogle)
        item.set_child(cb)
        #self.connect_menu(cb, item)

    def bind_b_to_a(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        cb.set_active(obj.b_to_a > 0)

    def setup_del_a(self, factory, item):
        def on_toogle(_):
            item.get_item().del_a = 0 if item.get_item().del_a == 1 else 1

        cb = Gtk.CheckButton()
        cb.connect('toggled', on_toogle)
        item.set_child(cb)
        #self.connect_menu(cb, item)

    def bind_del_a(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        cb.set_active(obj.del_a > 0)

    def setup_del_b(self, factory, item):
        def on_toogle(_):
            item.get_item().del_b = 0 if item.get_item().del_b == 1 else 1

        cb = Gtk.CheckButton()
        cb.connect('toggled', on_toogle)
        item.set_child(cb)
        #self.connect_menu(cb, item)

    def bind_del_b(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        cb.set_active(obj.del_b > 0)

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

    def append(self, name, diff, type_a, type_b, size_a, size_b, time_a, time_b, owner_a, owner_b):
        obj = DataObject(name,
                         diff,
                         type_a,
                         type_b,
                         -1 if size_a is None else size_a,
                         -1 if size_b is None else size_b,
                         time_a,
                         time_b,
                         owner_a,
                         owner_b
                         )
        
        self.store.append(obj)
        # model = self.selection
        # model.select_item(0, True)
        # self.list_view.scroll_to(0,
        #                          self.name_column,
        #                          flags=Gtk.ListScrollFlags(Gtk.ListScrollFlags.SELECT))

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
