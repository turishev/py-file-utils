import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
from main_window import MainWindow
from actions import AppActions
from files import FileOps

class MyApp(Adw.Application):
    def __init__(self, root_dir):
        super().__init__()
        if root_dir is None:
            root_dir = os.getcwd()

        self.file_ops = FileOps(root_dir)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        print('app: on_activate')
        self.win = MainWindow(application=app)
        self.actions = AppActions(self.win, self.file_ops)
        self.actions.register_actions(self)
        self.win.present()
        # self.win.after_init()

