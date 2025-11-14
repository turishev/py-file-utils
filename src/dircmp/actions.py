from __future__ import annotations # for list annotations
import enum

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib

from subprocess import Popen, DEVNULL, STDOUT
from pathlib import PurePath
# from threading import Timer


from app_types import *
import files
from dialogs import show_open_dir_dialog, show_confirm_dialog, show_info_dialog, ExcludeFilesDialog, ExcludeNamesDialog, ExcludeOperFlagsDialog, ExecLogDialog
from shortcuts import shortcuts;


class ActionStatus(enum.Enum):
    WAIT = 0
    RUN = 1
    ABORT = 2

_action_status = ActionStatus.WAIT
#_main_window = None


def _update_ui():
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)

def quit_handler():
    global _main_window
    # self.file_ops.stop_calculation()
    _main_window.destroy()


def compare_handler():
    global _main_window
    global _action_status

    if _action_status == ActionStatus.RUN: return
    _action_status = ActionStatus.RUN
    _main_window.start_compare()

    dir_a = _main_window.get_dir('a')
    dir_b = _main_window.get_dir('b')
    opts = _main_window.get_sync_options()

    items_count = 0
    def _add_new_item(item : CompareResultItem):
        nonlocal items_count
        items_count += 1
        _main_window.result_list.append(item)
        _main_window.set_count(items_count)
        _update_ui()

    result = files.compare_dirs(dir_a, dir_b, opts, _add_new_item)

    # for item in result:
    #     _main_window.result_list.append(item)

    _main_window.end_compare(abort=_action_status == ActionStatus.ABORT)
    _action_status = ActionStatus.WAIT


def exec_handler():
    global _action_status
    if _action_status != ActionStatus.WAIT: return

    def do_oper():
        global _main_window
        global _action_status
        _action_status = ActionStatus.RUN
        test_run = _main_window.get_sync_options().test_run
        oper_list = _main_window.get_oper_list()
        _main_window.execute_operations(oper_list, test_run=test_run)

        aborted = False
        def on_break():
            nonlocal aborted
            files.break_operations()
            aborted = True

        dialog = ExecLogDialog(_main_window, on_break)
        dialog.present()
        dialog.add_line('Start synchronization')

        files.execute_operations(oper_list, lambda text: dialog.add_line(text), test_run)

        fin_line = 'Synchronization is aborted' if aborted else 'Synchronization is done'
        dialog.add_line(fin_line)
        dialog.operations_end()
        _main_window.end_execution(test_run=test_run, abort=aborted)
        _action_status = ActionStatus.WAIT

    show_confirm_dialog(_main_window, "All operations will be executed. Proceed it?", do_oper)


def abort_compare():
    global _main_window
    global _action_status
    if _action_status != ActionStatus.RUN: return
    files.break_operations()
    _main_window.end_compare(abort=True)
    _action_status = ActionStatus.ABORT


def open_selected_file_handler(letter : str):
    if _action_status == ActionStatus.RUN: return
    path = _main_window.result_list.get_selected_file_path(letter)
    print(f"open_selected_file_handler: {letter} {path}")

    if path != '':
        Popen(['xdg-open', path],
              start_new_session=True,
              close_fds=True,
              stdout=DEVNULL,
              stderr=STDOUT)


def open_selected_file_dir_handler(letter : str):
    if _action_status == ActionStatus.RUN: return
    path = _main_window.result_list.get_selected_file_path(letter)
    print(f"open_selected_file_dir_handler: {letter} {path}")

    if path != '':
        dir = str(PurePath(path).parent)
        Popen(['xdg-open', dir],
              start_new_session=True,
              close_fds=True,
              stdout=DEVNULL,
              stderr=STDOUT)


def open_dir_handler(letter):
    global _main_window
    global _action_status

    if _action_status == ActionStatus.RUN: return

    show_open_dir_dialog(_main_window,
                         _main_window.get_dir(letter),
                         lambda dir: _main_window.set_dir(letter, dir))


def set_oper_flags_handler(oper :  OperType):
    global _main_window
    global _action_status
    if _action_status == ActionStatus.RUN: return
    _main_window.result_list.set_oper_flags_for_selected_items(oper)


def set_operation_flags():
    global _main_window
    global _action_status
    if _action_status == ActionStatus.RUN: return
    name = _main_window.result_list.get_selected_name()
    path_list = files.make_path_list(name)[1:] # exclude full file path

    def on_done(path='', a_to_b=False, del_a=False, b_to_a=False, del_b=False):
        if path != '':
            _main_window.result_list.set_oper_flags_batch(path=path, a_to_b=a_to_b, del_a=del_a, b_to_a=b_to_a, del_b=del_b)

    dialog = ExcludeOperFlagsDialog(_main_window, path_list, on_done)
    dialog.present()



def exclude_files_from_list():
    global _main_window
    global _action_status
    if _action_status == ActionStatus.RUN: return

    name = _main_window.result_list.get_selected_name()
    path_list = files.make_path_list(name)

    def on_done(path):
        if path != '':
            _main_window.result_list.delete_items('starts-with', path)
            _main_window.set_count(_main_window.result_list.get_list_len())

    dialog = ExcludeFilesDialog(_main_window, path_list, on_done)
    dialog.present()


def exclude_names_from_list():
    global _main_window
    global _action_status
    if _action_status == ActionStatus.RUN: return

    def on_done(result):
        print(f"_exclude_names_from_list result:{result}")
        if result is not None:
            _main_window.result_list.delete_items(result[0], result[1])
            _main_window.set_count(_main_window.result_list.get_list_len())

    dialog = ExcludeNamesDialog(_main_window, on_done)
    dialog.present()


def show_help_handler():
    print("show_help_handler")
    global _main_window
    head = "Shortcuts\n"
    text = head + "\n".join([f"{v[0]}\t{v[1]}" for v in shortcuts.values()])
    show_info_dialog(_main_window, text)


_actions = [
    ('quit', quit_handler),
    ('compare-dirs', compare_handler),
    ('exec-operations', exec_handler),
    ('break-operations', abort_compare),
    ('select-dir-a', lambda: open_dir_handler('a')),
    ('select-dir-b', lambda: open_dir_handler('b')),
    ('open-selected-file-a', lambda: open_selected_file_handler('a')),
    ('open-selected-file-b', lambda: open_selected_file_handler('b')),
    ('open-selected-file-dir-a', lambda: open_selected_file_dir_handler('a')),
    ('open-selected-file-dir-b', lambda: open_selected_file_dir_handler('b')),
    ('selected-files-a-to-b', lambda: set_oper_flags_handler(OperType.COPY_AB)),
    ('selected-files-del-a', lambda: set_oper_flags_handler(OperType.DEL_A)),
    ('selected-files-b-to-a', lambda: set_oper_flags_handler(OperType.COPY_BA)),
    ('selected-files-del-b', lambda: set_oper_flags_handler(OperType.DEL_B)),
    ('set-operation-flags', set_operation_flags),
    ('exclude-files-from-list', exclude_files_from_list),
    ('exclude-names-from-list', exclude_names_from_list),
    ('help', show_help_handler),
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
        key = shortcuts[act][0] if act in shortcuts else ""
        _create_act(act, [key], handler)
