from __future__ import annotations # for list annotations
from typing import TypeAlias

import enum

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib
from subprocess import Popen, DEVNULL, STDOUT
# from dialogs import show_confirm_dialog, show_open_dir_dialog
from dialogs import show_open_dir_dialog
from shortcuts import shortcuts;
# import utils
from pathlib import Path, PurePath

from app_types import *
from files import compare_dirs


class ActionStatus(enum.Enum):
    WAIT = 0
    RUN = 1

_action_status = ActionStatus.WAIT
#_main_window = None


def _update_ui():
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)

def _quit_handler():
    global _main_window
    # self.file_ops.stop_calculation()
    _main_window.destroy()


def _compare_handler():
    global _main_window
    global _action_status

    if _action_status == ActionStatus.RUN: return
    _action_status = ActionStatus.RUN
    _main_window.start_compare()

    dir_a = _main_window.get_dir('a')
    dir_b = _main_window.get_dir('b')
    opts = _main_window.get_sync_options()

    print(f"compare opts:{opts}")

    def _add_new_item(item : CompareResultItem):
        print(f"_add_new_item: {item}")
        _main_window.append_to_list(item)
        _update_ui()

    result = compare_dirs(dir_a, dir_b, opts, _add_new_item)
    _main_window.stop_operations()
    _action_status = ActionStatus.WAIT

def _exec_handler():
    global _main_window
    global _action_status

    if _action_status == ActionStatus.RUN: return
    _action_status = ActionStatus.RUN

    oper_list = _main_window.get_oper_list()
    print(f"oper_list:{oper_list}")
    _main_window.execute_operations(oper_list)
    _main_window.stop_operations()
    _action_status = ActionStatus.WAIT


def _break_operations_handler():
    global _main_window
    global _action_status
    if _action_status != ActionStatus.RUN: return
    _main_window.stop_operations(is_abort=True)
    _action_status = ActionStatus.WAIT


def _open_selected_file_handler(letter : str):
    if _action_status == ActionStatus.RUN: return
    path = _main_window.result_list.get_selected_file_path(letter)
    print(f"_open_selected_file_handler {letter} {path}")

    if path != '':
        Popen(['xdg-open', path],
              start_new_session=True,
              close_fds=True,
              stdout=DEVNULL,
              stderr=STDOUT)


def _open_selected_file_dir_handler(letter : str):
    if _action_status == ActionStatus.RUN: return
    path = _main_window.result_list.get_selected_file_path(letter)
    print(f"_open_selected_file_dir_handler {letter} {path}")

    if path != '':
        dir = str(PurePath(path).parent)
        Popen(['xdg-open', dir],
              start_new_session=True,
              close_fds=True,
              stdout=DEVNULL,
              stderr=STDOUT)


    # def delete_handler(self):
    #     if self.status == ActionStatus.RUN: return
    #     result_list = self.win.result_list
    #     file_name = result_list.get_selected_name()
    #     print("delete:"  +  file_name)

    #     def do_delete():
    #         print("do_delete:" + file_name)
    #         self.win.result_list.delete_selected_item()
    #         self.file_ops.delete(file_name)

    #     show_confirm_dialog(self.win,
    #                         f"File or dir '{file_name}' will be deleted, do continue?",
    #                         do_delete)

def _open_dir_handler(letter):
    global _main_window
    global _action_status

    if _action_status == ActionStatus.RUN: return

    show_open_dir_dialog(_main_window,
                         _main_window.get_dir(letter),
                         lambda dir: _main_window.set_dir(letter, dir))


def _set_oper_flags_handler(oper :  OperType):
    global _main_window
    global _action_status
    if _action_status == ActionStatus.RUN: return
    _main_window.result_list.set_oper_flags_for_selected_items(oper)
    


_actions = [
    ('quit', _quit_handler),
    ('compare-dirs', _compare_handler),
    ('exec-operations', _exec_handler),
    ('break-operations', _break_operations_handler),
    ('select-dir-a', lambda: _open_dir_handler('a')),
    ('select-dir-b', lambda: _open_dir_handler('b')),
    ('open-selected-file-a', lambda: _open_selected_file_handler('a')),
    ('open-selected-file-b', lambda: _open_selected_file_handler('b')),
    ('open-selected-file-dir-a', lambda: _open_selected_file_dir_handler('a')),
    ('open-selected-file-dir-b', lambda: _open_selected_file_dir_handler('b')),
    ('selected-files-a-to-b', lambda: _set_oper_flags_handler(OperType.COPY_AB)),
    ('selected-files-del-a', lambda: _set_oper_flags_handler(OperType.DEL_A)),
    ('selected-files-b-to-a', lambda: _set_oper_flags_handler(OperType.COPY_BA)),
    ('selected-files-del-b', lambda: _set_oper_flags_handler(OperType.DEL_B)),
]


def init_actions(app, win):
    global _main_window
    global _action_status
    _action_status = ActionStatus.WAIT
    _main_window = win

    def _create_act(name, keys, fn):
        # we need pass name, keys, fn as values into a separate function
        # to decouple them from mutable iterators
        act = Gio.SimpleAction(name=name)
        act.connect('activate', lambda *_: fn())
        app.add_action(act)
        app.set_accels_for_action("app.%s" % name, keys)

    for act, handler in _actions:
        key = shortcuts[act]  if act in shortcuts else ""
        _create_act(act, [key], handler)
