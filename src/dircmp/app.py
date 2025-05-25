import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
from main_window import MainWindow
from actions import AppActions
from files import FileOps

class MyApp(Adw.Application):
    def __init__(self, script_file, root_dir):
        super().__init__()
        auto_run = False
        if root_dir is None:
            root_dir = os.getcwd()
        else:
            auto_run = True

        self.file_ops = FileOps(root_dir)
        self.script_file = script_file
        self.connect('activate', self.on_activate, auto_run)

    def on_activate(self, app, auto_run):
        print('app: on_activate')
        self.win = MainWindow(application=app)
        self.win.set_root_dir(str(self.file_ops.root_dir))
        # self.actions.register_actions(self)
        self.win.present()
        # self.win.after_init()
        if auto_run:
            self.actions.calculate_handler()
