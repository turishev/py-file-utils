from __future__ import annotations # for list annotations
from typing import TypeAlias

import gi
from time import localtime, strftime
import re


gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk, Gio, GObject

from app_types import *


class DataObject(GObject.GObject):
    __gtype_name__ = 'DataObject'

    name = GObject.Property(type=str, default="")
    diff = GObject.Property(type=str, default="")
    a_to_b = GObject.Property(type=bool, default=False)
    del_a = GObject.Property(type=bool, default=False)
    b_to_a = GObject.Property(type=bool, default=False)
    del_b = GObject.Property(type=bool, default=False)
    type_a = GObject.Property(type=str, default="")
    type_b = GObject.Property(type=str, default="")
    size_a = GObject.Property(type=GObject.TYPE_INT64, default=-1) # do not use int here!
    size_b = GObject.Property(type=GObject.TYPE_INT64, default=-1) # do not use int here!
    time_a = GObject.Property(type=float, default=0.0)
    time_b = GObject.Property(type=float, default=0.0)
    path_a = GObject.Property(type=str, default="")
    path_b = GObject.Property(type=str, default="")

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
        self.a_to_b=False
        self.del_a=False
        self.b_to_a=False
        self.del_b=False


def _format_time(tm):
    if tm <= 0: return ''
    else: return strftime("%Y-%m-%d %H:%M:%S", localtime(tm))

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

        sorter = Gtk.ColumnView.get_sorter(self.list_view)
        self.sort_model = Gtk.SortListModel(model=self.store, sorter=sorter)
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
        label.set_text(str(obj.size_a) if obj.size_a > 0 else '') # -1 is size unknown

    def setup_size_b(self, factory, item):
        label = Gtk.Label()
        label.set_xalign(1.0)
        item.set_child(label)
        self.connect_menu(label, item)

    def bind_size_b(self, factory, item):
        label = item.get_child()
        obj = item.get_item()
        label.set_text(str(obj.size_b) if obj.size_b > 0 else '')# -1 is size unknown

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

    def _update_bool_field(self, button, item, field):
        obj : DataObject = item.get_item()
        print(f"toggle {button.get_active()} {obj.name} {obj.a_to_b}")
        try:
            obj.set_property(field, button.get_active())
        except TypeError as e:
            print(f"Error setting property: {e}")
        except GObject.GError as e:
            print(f"GObject Error: {e}")

    def setup_a_to_b(self, factory, item : Gtk.ColumnViewCell):
        # print(f"setup_a_to_b {item}")
        bt = Gtk.ToggleButton()
        bt.connect('toggled', lambda _: self._update_bool_field(bt, item, 'a_to_b'))
        item.set_child(bt)

    def bind_a_to_b(self, factory, item : Gtk.ColumnViewCell):
        cb = item.get_child()
        obj : DataObject = item.get_item()
        # print(f"a_to_b: {item} {obj.name} {obj.diff}")
        if obj.diff == 'B':
            cb.set_visible(False)
        else:
            cb.set_visible(True)
            obj.bind_property("a_to_b", cb , "active", GObject.BindingFlags.SYNC_CREATE)

    def setup_b_to_a(self, factory, item):
        bt = Gtk.ToggleButton()
        bt.connect('toggled', lambda _: self._update_bool_field(bt, item, 'b_to_a'))
        item.set_child(bt)


    def bind_b_to_a(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        # print(f"b_to_a: {obj.name} {obj.diff}")
        if obj.diff == 'A': cb.set_visible(False)
        else:
            cb.set_visible(True)
            obj.bind_property("b_to_a", cb , "active", GObject.BindingFlags.SYNC_CREATE)


    def setup_del_a(self, factory, item):
        bt = Gtk.ToggleButton()
        bt.connect('toggled', lambda _: self._update_bool_field(bt, item, 'del_a'))
        item.set_child(bt)


    def bind_del_a(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        # print(f"del_a: {obj.name} {obj.diff}")
        if obj.diff == 'B': cb.set_visible(False)
        else:
            cb.set_visible(True)
            obj.bind_property("del_a", cb, "active", GObject.BindingFlags.SYNC_CREATE)


    def setup_del_b(self, factory, item):
        bt = Gtk.ToggleButton()
        bt.connect('toggled', lambda _: self._update_bool_field(bt, item, 'del_b'))
        item.set_child(bt)


    def bind_del_b(self, factory, item):
        cb = item.get_child()
        obj = item.get_item()
        # print(f"del_b: {obj.name} {obj.diff}")
        if obj.diff == 'A': cb.set_visible(False)
        else:
            cb.set_visible(True)
            obj.bind_property("del_b", cb , "active", GObject.BindingFlags.SYNC_CREATE)

    def connect_menu(self, widget, item):
        click = Gtk.GestureClick()
        click.set_button(3)
        click.connect("pressed", self.on_mouse_right_button_down, item)
        click.connect("released", self.on_mouse_right_button_up, item)
        widget.add_controller(click)

    def append(self, item : CompareResultItem):
        try:
            obj = DataObject(name=item.name,
                             diff=item.diff,
                             type_a='' if item.file_a is None else item.file_a.type,
                             type_b='' if item.file_b is None else item.file_b.type,
                             size_a=-1 if item.file_a is None else item.file_a.size,
                             size_b=-1 if item.file_b is None else item.file_b.size,
                             time_a=-1 if item.file_a is None else item.file_a.time,
                             time_b=-1 if item.file_b is None else item.file_b.time,
                             # '' if item.file_a is None else item.file_a.owner,
                             # '' if item.file_b is None else item.file_b.owner
                             path_a='' if item.file_a is None else item.file_a.path,
                             path_b='' if item.file_b is None else item.file_b.path,
                             )

            self.store.append(obj)
            # model = self.selection
            # model.select_item(0, True)
            # self.list_view.scroll_to(0,
            #                          self.name_column,
            #                          flags=Gtk.ListScrollFlags(Gtk.ListScrollFlags.SELECT))
        except Exception as e:# we can run into error if name in invalid encoding
            print(f"Error of creating DataObject:{e}")


    def clear(self):
        self.store.remove_all()

    def on_mouse_right_button_down(self, gesture : Gtk.GestureClick, count: int,
                                   x : float, y : float, cell : Gtk.ColumnViewCell):
        data = cell.get_item()
        # print(f"on_mouse_right_button_down: {data}")
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

    def delete_items(self, method : str, text : str):
        if method == 'starts-with':
            self._delete_by_predicate_backward(lambda item: item.name.startswith(text))
        elif method == 'ends-with':
            self._delete_by_predicate_backward(lambda item: item.name.endswith(text))
        elif method == 'contains':
            self._delete_by_predicate_backward(lambda item: text in item.name)
        elif method == 'regexp':
            pattern = re.compile(text)
            self._delete_by_predicate_backward(lambda item: pattern.match(item.name))


    def _delete_by_predicate_backward(self, predicate):
        # removing backward is more safely
        store =  self.store
        # Iterate backward using indices
        for i in range(store.get_n_items() - 1, -1, -1):
            item = store.get_item(i)
            if predicate(item):
                # Remove the item at the current index
                store.remove(i)


    def create_item_menu(self, widget, item):
        # print(item)
        gmenu = Gio.Menu()
        gmenu.append("set flags", "app.set-operation-flags")
        gmenu.append("exclude paths from list", "app.exclude-files-from-list")
        gmenu.append("exclude names from list", "app.exclude-names-from-list")
        if item.diff != 'B':
            gmenu.append("open A", "app.open-selected-file-a")
        if item.diff != 'A':
            gmenu.append("open B", "app.open-selected-file-b")
        if item.diff != 'B':
            gmenu.append("open dir A", "app.open-selected-file-dir-a")
        if item.diff != 'A':
            gmenu.append("open dir B", "app.open-selected-file-dir-b")

        menu = Gtk.PopoverMenu.new_from_model(gmenu)
        menu.set_parent(widget)
        return menu


    def show_item_menu(self, widget, x, y, item):
        menu = self.create_item_menu(widget, item)
        menu.set_offset(x, y)
        menu.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        menu.popup()


    def get_single_selection_item(self):
        sel : Gtk.Bitset = self.selection.get_selection()
        if sel.get_size() != 1: return None
        inx = sel.get_minimum()
        return self.selection.get_item(inx)


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
        item = self.get_single_selection_item()
        if item is not None:
            if letter == 'a': return item.path_a
            elif letter == 'b': return item.path_b
            else: return ''
        else: return ''



    def get_selected_name(self):
        item = self.get_single_selection_item()
        return item.name if item is not None else ""


    def set_oper_flags_for_selected_items(self, oper : OperType):
        def get_flag(inx):
            item = self.selection.get_item(inx)
            if oper == OperType.COPY_AB: return item.a_to_b
            elif oper == OperType.COPY_BA: return item.b_to_a
            elif oper == OperType.DEL_A: return item.del_a
            elif oper == OperType.DEL_B: return item.del_b
            else: return False

        def set_flag(inx, v):
            item = self.selection.get_item(inx)

            if oper == OperType.COPY_AB:
                item.b_to_a = False
                item.del_b = False
                if  item.diff != 'B': item.a_to_b = v
            elif oper == OperType.COPY_BA:
                item.a_to_b = False
                item.del_a = False
                if  item.diff != 'A': item.b_to_a = v
            elif oper == OperType.DEL_A:
                if  item.diff != 'B:': item.del_a = v
            elif oper == OperType.DEL_B:
                if item.diff != 'A': item.del_b = v

        sel : Gtk.Bitset = self.selection.get_selection()
        is_valid,iter,data_index = Gtk.BitsetIter.init_first(sel)
        new_flag_value = not get_flag(data_index) if is_valid else False

        while is_valid:
            set_flag(data_index, new_flag_value)
            is_valid,data_index =  iter.next()


    def set_oper_flags_batch(self, path, a_to_b, del_a, b_to_a, del_b):
        model = self.store
        for i in range(model.get_n_items()):
            item = model.get_item(i)
            if item.name.startswith(path):
                item.a_to_b = a_to_b and item.diff != 'B'
                item.b_to_a = b_to_a and item.diff != 'A'
                item.del_a = del_a and not b_to_a and item.diff != 'B'
                item.del_b = del_b and not a_to_b and item.diff != 'A'
