from __future__ import annotations # for list annotations
from typing import TypeAlias

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


from app_types import *
from shortcuts import shortcuts
from result_list import ResultList

def make_button(label, action):
    shortcut = f"({shortcuts[action]})" if action in shortcuts else ""
    bt = Gtk.Button(label=f"{label} {shortcut}")
    bt.set_action_name('app.' + action)
    return bt

class ToolsPanel():
    def __init__(self):
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # self.box.set_homogeneous(True)
        self.box.set_spacing(8)
        self.box.set_margin_top(8)
        self.box.set_margin_start(8)
        self.box.set_margin_end(8)
        self.box.append(make_button('A->B', 'selected-files-a-to-b'))
        self.box.append(make_button('Del A', 'selected-files-del-a'))
        self.box.append(make_button('B->A', 'selected-files-b-to-a'))
        self.box.append(make_button('Del B', 'selected-files-del-b'))
    def get_box(self):
        return self.box

class OptionsPanel():
    sync_types = [
        ('A<->B', SyncDirection.BOTH),
        ('A->B', SyncDirection.A_TO_B),
        ('B->A', SyncDirection.B_TO_A)
    ]
    def __init__(self):
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # self.box.set_homogeneous(True)
        self.box.set_margin_top(8)
        self.box.set_margin_start(8)
        self.box.set_margin_end(8)

        self.sync_type_selector = Gtk.DropDown.new_from_strings([v[0] for v in self.sync_types])
        self.box.append(self.sync_type_selector)

        box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_1.set_margin_start(12)
        self.size_cb = Gtk.CheckButton()
        self.size_cb.set_active(True)
        box_1.append(self.size_cb)
        box_1.append(Gtk.Label.new_with_mnemonic('check size'))
        self.box.append(box_1)

        box_3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_3.set_margin_start(12)
        self.time_cb = Gtk.CheckButton()
        self.time_cb.set_active(True)
        box_3.append(self.time_cb)
        box_3.append(Gtk.Label.new_with_mnemonic('check time'))
        self.box.append(box_3)

        box_3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_3.set_margin_start(12)
        self.content_cb = Gtk.CheckButton()
        box_3.append(self.content_cb)
        box_3.append(Gtk.Label.new_with_mnemonic('check content'))
        self.box.append(box_3)

    def get_box(self):
        return self.box

    def get_options(self) -> SyncOptions:
        sync_type_inx = self.sync_type_selector.get_selected()
        sync_dir = self.sync_types[sync_type_inx][1]
        return SyncOptions(sync_direction=sync_dir,
                           check_size=self.size_cb.get_active(),
                           check_time=self.time_cb.get_active(),
                           check_content=self.content_cb.get_active())


class MainWindow(Gtk.ApplicationWindow):
    app_title = "dircmp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_dir = None
        self.set_default_size(1024, 800)
        self.set_title(self.app_title)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)

        self.dir_a_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dir_a_box.set_spacing(8)
        self.dir_a_box.set_margin_top(8)
        # self.dir_a_box.set_margin_bottom(8)
        self.dir_a_box.set_margin_start(8)
        self.dir_a_box.set_margin_end(8)

        self.dir_b_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dir_b_box.set_spacing(8)
        self.dir_b_box.set_margin_top(8)
        # self.dir_b_box.set_margin_bottom(8)
        self.dir_b_box.set_margin_start(8)
        self.dir_b_box.set_margin_end(8)
        self.dir_b_box.set_spacing(8)

        self.main_box.append(self.dir_a_box)
        self.main_box.append(self.dir_b_box)
        self.dir_a_bt = make_button("A", "select-dir-a")

        self.dir_b_bt = make_button("B", "select-dir-b")
        self.dir_a_box.append(self.dir_a_bt);
        self.dir_b_box.append(self.dir_b_bt);
        self.dir_a_entry = Gtk.Entry()
        self.dir_a_entry.set_hexpand(True)
        self.dir_a_box.append(self.dir_a_entry);
        self.dir_b_entry = Gtk.Entry()
        self.dir_b_entry.set_hexpand(True)
        self.dir_b_box.append(self.dir_b_entry);

        
        self.top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.top_box.set_spacing(32)
        self.top_box.set_margin_bottom(8)
        self.main_box.append(self.top_box)
        self.options_box = OptionsPanel()
        self.top_box.append(self.options_box.get_box())
        self.top_box.append(ToolsPanel().get_box())

        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box.set_margin_start(8)
        self.center_box.set_margin_end(8)
        self.main_box.append(self.center_box)

        self.status_label = Gtk.Label()
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.status_box.set_margin_top(8)
        self.status_box.set_margin_start(8)
        self.status_box.append(self.status_label)
        self.main_box.append(self.status_box)

        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.bottom_box.set_spacing(10)
        self.bottom_box.set_margin_top(10)
        self.bottom_box.set_margin_bottom(10)
        self.bottom_box.set_margin_start(10)
        self.bottom_box.set_margin_end(10)
        self.bottom_box.set_homogeneous(True)
        self.main_box.append(self.bottom_box)

        self.result_list = ResultList()
        sw = Gtk.ScrolledWindow()
        self.center_box.append(sw)
        sw.set_child(self.result_list.list_view)
        self.result_list.list_view.grab_focus()

        self.compare_bt = make_button("Compare", "compare-dirs")
        self.bottom_box.append(self.compare_bt)

        self.execute_bt = make_button("Execute", "exec-operations")
        self.execute_bt.set_sensitive(False)
        self.bottom_box.append(self.execute_bt)

        self.break_bt = make_button("Break", "break-operations")
        self.break_bt.set_sensitive(False)
        self.bottom_box.append(self.break_bt)

        self.close_bt = make_button("Close", "quit")
        self.bottom_box.append(self.close_bt)

    #     self.header = Gtk.HeaderBar()
    #     self.set_titlebar(self.header)

    #     app = self.get_application()
    #     sm = app.get_style_manager()
    #     sm.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT) ## Adw.ColorScheme.PREFER_DARK
    #     # для стилизации приложения - adwaita
    #     # https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/styles-and-appearance.html


    def after_init(self):
        print('after_init')
         # this doesn't work in __init__
        self.break_bt.set_sensitive(False);
        self.execute_bt.set_sensitive(False)

    def set_status(self, text):
        self.status_label.set_text(text)

    def start_compare(self):
        self.compare_bt.set_sensitive(False)
        self.execute_bt.set_sensitive(False)
        self.dir_a_bt.set_sensitive(False)
        self.dir_b_bt.set_sensitive(False)
        self.break_bt.set_sensitive(True)
        self.result_list.clear()
        self.set_status('Comparing..')

    def execute_operations(self, oper_list):
        self.compare_bt.set_sensitive(False)
        self.execute_bt.set_sensitive(False)
        self.dir_a_bt.set_sensitive(False)
        self.dir_b_bt.set_sensitive(False)
        self.break_bt.set_sensitive(True)
        self.set_status('Executing..')

    def stop_operations(self, is_abort=False):
        self.compare_bt.set_sensitive(True)
        if self.result_list.get_list_len() > 0: self.execute_bt.set_sensitive(True)
        self.break_bt.set_sensitive(False)
        self.dir_a_bt.set_sensitive(True)
        self.dir_b_bt.set_sensitive(True)
        if is_abort: self.set_status('Aborted')
        else: self.set_status('Finished')

    def set_dir(self, letter, dir):
        if letter == 'a': self.dir_a_entry.set_text(dir)
        else: self.dir_b_entry.set_text(dir)
        if self.dir_a_entry.get_text() != "" and self.dir_b_entry.set_text != "":
            self.compare_bt.set_sensitive(True)

    def get_dir(self, letter):
        if letter == 'a': return self.dir_a_entry.get_text()
        else: return self.dir_b_entry.get_text()

    def append_to_list(self, item  : CompareResultItem):
        self.result_list.append(item)

    def get_sync_options(self) -> SyncOptions:
        return self.options_box.get_options()

    def get_oper_list(self):
        return self.result_list.get_oper_list()
