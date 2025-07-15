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

class ActionStatus(enum.Enum):
    WAIT = 0
    RUN = 1

class AppActions:
    def __init__(self, win, file_ops):
        self.status = ActionStatus.WAIT
        self.win = win
        self.file_ops = file_ops
        self.actions = [
            ('quit', self.quit_handler),
            # ('calculate-sizes', self.calculate_handler),
            # ('delete-selected-file', self.delete_handler),
            # ('break-calculation', self.break_calculation_handler),
            # ('dirsize-selected-file', self.dirsize_handler),
            # ('open-selected-file', self.open_handler),
            ('select-dir-a', lambda: self.open_dir_handler('a')),
            ('select-dir-b', lambda: self.open_dir_handler('b')),
            ]


    def _update_ui(self):
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)

    def register_actions(self, app):
        def _create_act(name, keys, fn):
            # we need pass name, keys, fn as values into a separate function
            # to decouple them from mutable iterators
            act = Gio.SimpleAction(name=name)
            act.connect('activate', lambda *_: fn())
            app.add_action(act)
            app.set_accels_for_action("app.%s" % name, keys)

        for act, handler in self.actions:
            key = shortcuts[act]  if act in shortcuts else ""
            _create_act(act, [key], handler)


    def quit_handler(self):
        # self.file_ops.stop_calculation()
        self.win.destroy()


    # def calculate_handler(self):
    #     if self.status == ActionStatus.RUN: return
    #     self.status = ActionStatus.RUN
    #     self.win.start_calculation()

    #     sum_size = 0

    #     def set_status(sz):
    #         self.win.set_status(f"Calculating ... {utils.format_size(sz)}  bites")

    #     set_status(0)

    #     def _add_new_item(name, size, type):
    #         nonlocal sum_size
    #         sum_size += size
    #         self.win.result_list.append(name, type, size)
    #         set_status(sum_size)
    #         self._update_ui()

    #     self.file_ops.get_dir_size_list(lambda v: _add_new_item(*v), self._update_ui)

    #     size_bounds = [(1024**3, 'Gb'),
    #                    (1024**2, 'Mb'),
    #                    (1024, 'kb'),
    #                    (0, '')]

    #     sums = ""

    #     for i in range(len(size_bounds) - 1):
    #         delim = size_bounds[i][0]
    #         sign = size_bounds[i][1]

    #         if sum_size >= delim:
    #             sums = f'~ {round(sum_size / delim, 1)} {sign}'
    #             break

    #     self.win.set_status("%s  bites    %s" % (utils.format_size(sum_size), sums))
    #     self.win.stop_calculation()
    #     self.status = ActionStatus.WAIT


    # def break_calculation_handler(self):
    #     print('stop_calculation_handler')
    #     if not self.status == ActionStatus.RUN: return
    #     self.file_ops.stop_calculation()
    #     self.win.set_status("Calculation aborted")
    #     self.status = ActionStatus.WAIT


    # def open_handler(self):
    #     if self.status == ActionStatus.RUN: return
    #     result_list = self.win.result_list
    #     file_name = result_list.get_selected_name()
    #     path = self.file_ops.file_path(file_name)

    #     Popen(['xdg-open', path],
    #           start_new_session=True,
    #           close_fds=True,
    #           stdout=DEVNULL,
    #           stderr=STDOUT)


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

    def open_dir_handler(self, letter):
        if self.status == ActionStatus.RUN: return

        def on_select_dir(dir):
            self.file_ops.set_dir(letter, dir)
            self.win.set_dir(letter, dir)

        show_open_dir_dialog(self.win,
                             self.file_ops.get_dir(letter),
                             on_select_dir)
