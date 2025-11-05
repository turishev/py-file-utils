from __future__ import annotations # for list annotations
from typing import TypeAlias

import gi
from time import localtime, strftime


gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject

from app_types import *


class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    name = GObject.Property(type=GObject.TYPE_STRING, default="")
    diff = GObject.Property(type=GObject.TYPE_STRING, default="")
    a_to_b = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    del_a = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)
    b_to_a = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False) # use INT instead BOOLEAN for sake of sort support
    del_b = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False) # use INT instead BOOLEAN for sake of sort support
    type_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    type_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    size_a = GObject.Property(type=GObject.TYPE_INT64, default=-1)
    size_b = GObject.Property(type=GObject.TYPE_INT64, default=-1)
    time_a = GObject.Property(type=GObject.TYPE_DOUBLE, default=0)
    time_b = GObject.Property(type=GObject.TYPE_DOUBLE, default=0)
    # owner_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    # owner_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    # perm_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    # perm_b = GObject.Property(type=GObject.TYPE_STRING, default="")
    path_a = GObject.Property(type=GObject.TYPE_STRING, default="")
    path_b = GObject.Property(type=GObject.TYPE_STRING, default="")

    def __init__(self, name, diff, type_a, type_b, size_a, size_b, time_a, time_b,
                 path_a, path_b,
                 # owner_a='', owner_b=''
                 ):
        super().__init__()
        self.name = name
        self.diff = diff
        self.type_a = type_a
        self.type_b = type_b
        self.size_a = size_a
        self.size_b = size_b
        # self.owner_a = owner_a
        # self.owner_b = owner_b
        self.time_a = time_a
        self.time_b = time_b
        self.path_a = path_a
        self.path_b = path_b


def _format_time(tm):
    return strftime("%Y-%m-%d %H:%M:%S", localtime(tm))

def _get_op_type(a_to_b : bool, b_to_a : bool, del_a : bool, del_b : bool) -> OperType:
    if a_to_b:
        if b_to_a or del_b: return OperType.NOTHING
        elif del_a: return OperType.MOVE_AB
        else: return OperType.COPY_AB
    elif b_to_a:
        if del_a: return OperType.NOTHING
        elif del_b: return OperType.MOVE_BA
        else: return OperType.COPY_BA
    elif del_a and del_b: return OperType.DEL_AB
    else:
        if del_a: return OperType.DEL_A
        elif del_b: return OperType.DEL_B
        else: return OperType.NOTHING


def _create_list_column(name, data_field, setup_fn, bind_fn, sorter_type):
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup_fn)
    factory.connect("bind", bind_fn)
    exp = Gtk.PropertyExpression.new(DataObject, None, data_field)

    if sorter_type == "str": sorter = Gtk.StringSorter(expression=exp)
    elif sorter_type == "num": sorter = Gtk.NumericSorter(expression=exp) # works for bool also
    else: sorter = None

    column = Gtk.ColumnViewColumn(title=name, factory=factory)
    column.set_sorter(sorter)
    return column

class ResultList():
    def __init__(self):
        self.store = Gio.ListStore(item_type=DataObject)
        self.list_view = Gtk.ColumnView()

        self.name_column = _create_list_column("Name", "name", self.setup_name, self.bind_name, "str")
        self.name_column.set_expand(True)
        self.list_view.append_column(self.name_column)
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
        # self.list_view.append_column(_create_list_column("A owner", "owner_a", self.setup_owner_a, self.bind_owner_a, "str"))
        # self.list_view.append_column(_create_list_column("B owner", "owner_b", self.setup_owner_b, self.bind_owner_b, "str"))

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
        # self.selection = Gtk.SingleSelection(model=self.sort_model)
        self.selection = Gtk.MultiSelection(model=self.sort_model)
        # self.selection.connect("selection-changed", self.on_sel_changed)

        self.list_view.set_model(self.selection)
        self.list_view.set_hexpand(True)
        self.list_view.set_vexpand(True)
    #     self.list_view.sort_by_column(self.size_column, Gtk.SortType.DESCENDING) # Gtk.SortType.ASCENDING
    #     self.list_view.connect("activate", self.on_activate);

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
        cb = Gtk.CheckButton()
        item.set_child(cb)

    def bind_a_to_b(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        if obj.diff == 'B': cb.set_sensitive(False)
        else:  cb.set_active(obj.a_to_b > 0)
        obj.bind_property("a_to_b", cb , "active", GObject.BindingFlags.BIDIRECTIONAL)

    def setup_b_to_a(self, factory, item):
        cb = Gtk.CheckButton()
        item.set_child(cb)

    def bind_b_to_a(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        if obj.diff == 'A': cb.set_sensitive(False)
        else: cb.set_active(obj.b_to_a > 0)
        obj.bind_property("b_to_a", cb , "active", GObject.BindingFlags.BIDIRECTIONAL)

    def setup_del_a(self, factory, item):
        cb = Gtk.CheckButton()
        item.set_child(cb)

    def bind_del_a(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        if obj.diff == 'B': cb.set_sensitive(False)
        else: cb.set_active(obj.del_a > 0)
        obj.bind_property("del_a", cb , "active", GObject.BindingFlags.BIDIRECTIONAL)

    def setup_del_b(self, factory, item):
        cb = Gtk.CheckButton()
        item.set_child(cb)

    def bind_del_b(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        if obj.diff == 'A': cb.set_sensitive(False)
        else: cb.set_active(obj.del_b > 0)
        obj.bind_property("del_b", cb , "active", GObject.BindingFlags.BIDIRECTIONAL)

    def connect_menu(self, widget, item):
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("pressed", self.on_mouse_right_button_down, item)
        click.connect("released", self.on_mouse_right_button_up, item)
        widget.add_controller(click)

    def append(self, item : CompareResultItem):
        obj = DataObject(item.name,
                         item.diff,
                         '' if item.file_a is None else item.file_a.type,
                         '' if item.file_b is None else item.file_b.type,
                         -1 if item.file_a is None else item.file_a.size,
                         -1 if item.file_b is None else item.file_b.size,
                         -1 if item.file_a is None else item.file_a.time,
                         -1 if item.file_b is None else item.file_b.time,
                         # '' if item.file_a is None else item.file_a.owner,
                         # '' if item.file_b is None else item.file_b.owner
                         '' if item.file_a is None else item.file_a.path,
                         '' if item.file_b is None else item.file_b.path,
                         )

        self.store.append(obj)
        model = self.selection
        model.select_item(0, True)
        self.list_view.scroll_to(0,
                                 self.name_column,
                                 flags=Gtk.ListScrollFlags(Gtk.ListScrollFlags.SELECT))

    def clear(self):
        self.store.remove_all()

    def on_mouse_right_button_down(self, gesture : Gtk.GestureClick, count: int,
                                   x : float, y : float, cell : Gtk.ColumnViewCell):
        print("on_mouse_right_button_down")
        data = cell.get_item()
        print(f"on_mouse_right_button_down: {data}")
        self.select_item(data)

    def on_mouse_right_button_up(self, gesture : Gtk.GestureClick, count: int,
                                 x : float, y : float, cell : Gtk.ColumnViewCell):
        # print("on_mouse_right_button_up")
        data = cell.get_item()
        self.show_item_menu(cell.get_child(), x, y, data)

    def select_item(self, item):
        model = self.selection
        for i in range(model.get_n_items()):
            if model.get_item(i) == item:
                model.select_item(i, True)

    # def delete_item(self, item):
    #     print("delete_item: %s" % item.name)
    #     model = self.store
    #     for i in range(model.get_n_items()):
    #         if model.get_item(i) == item:
    #             model.remove(i)
    #             break

    def create_item_menu(self, widget, item):
        gmenu = Gio.Menu()
        gmenu.append("set flags", "app.set-operation-flags")
        gmenu.append("exclude paths from list", "app.exclude-files-from-list")
        gmenu.append("exclude names from list", "app.exclude-names-from-list")
        gmenu.append("open A", "app.open-selected-file-a")
        gmenu.append("open B", "app.open-selected-file-b")
        gmenu.append("open dir A", "app.open-selected-file-dir-a")
        gmenu.append("open dir B", "app.open-selected-file-dir-b")

        menu = Gtk.PopoverMenu.new_from_model(gmenu)
        menu.set_parent(widget)
        return menu

    def show_item_menu(self, widget, x, y, item):
        print("show_item_menu")
        menu = self.create_item_menu(widget, item)
        menu.set_offset(x, y)
        menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        menu.popup()

    def get_single_selection_item(self):
        sel : Gtk.Bitset = self.selection.get_selection()
        if sel.get_size() != 1: return None
        inx = sel.get_minimum()
        return self.selection.get_item(inx)


    # def delete_selected_item(self):
    #     print("delete_act_handler")
    #     item = self.get_selected_item()
    #     print("file:" + item.name)
    #     self.delete_item(item)

    def get_oper_list(self):
        result = []
        pos = 0
        while True:
            item = self.store.get_item(pos)
            pos += 1
            if item is None:
                break
            else:
                optype = _get_op_type(item.a_to_b, item.b_to_a, item.del_a, item.del_b)
                if optype != OperType.NOTHING:
                    result.append(Oper(optype, item.path_a, item.path_b))

        return result

    def get_list_len(self):
        return len(self.store)

    def get_selected_file_path(self, letter):
        if letter == 'a': return self.get_single_selection_item().path_a
        if letter == 'b': return self.get_single_selection_item().path_b
        return ''


    def get_selected_name(self):
        return self.get_single_selection_item().name


    def set_oper_flags_for_selected_items(self, oper : OperType):
        def get_flag(inx):
            data_row = self.selection.get_item(inx)
            if oper == OperType.COPY_AB: return data_row.a_to_b
            elif oper == OperType.COPY_BA: return data_row.b_to_a
            elif oper == OperType.DEL_A: return data_row.del_a
            elif oper == OperType.DEL_B: return data_row.del_b
            else: return False

        def set_flag(inx, v):
            data_row = self.selection.get_item(inx)

            if oper == OperType.COPY_AB:
                data_row.b_to_a = False
                data_row.del_b = False
                if  data_row.diff != 'B': data_row.a_to_b = v
            elif oper == OperType.COPY_BA:
                data_row.a_to_b = False
                data_row.del_a = False
                if  data_row.diff != 'A': data_row.b_to_a = v
            elif oper == OperType.DEL_A:
                if  data_row.diff != 'B:': data_row.del_a = v
            elif oper == OperType.DEL_B:
                if data_row.diff != 'A': data_row.del_b = v

        sel : Gtk.Bitset = self.selection.get_selection()
        is_valid,iter,data_index = Gtk.BitsetIter.init_first(sel)
        new_flag_value = not get_flag(data_index) if is_valid else False

        while is_valid:
            set_flag(data_index, new_flag_value)
            is_valid,data_index =  iter.next()
