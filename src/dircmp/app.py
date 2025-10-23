import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
from main_window import MainWindow
from actions import AppActions
from files import FileOps

class MyApp(Adw.Application):
    def __init__(self, dir_a, dir_b):
        super().__init__()
        cwd = os.getcwd()
        da = dir_a if dir_a else cwd
        db = dir_b if dir_b else cwd
        
        self.file_ops = FileOps(da, db)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        print('app: on_activate')
        self.win = MainWindow(application=app)
        self.actions = AppActions(self.win, self.file_ops)
        self.actions.register_actions(self)
        self.win.present()
        # self.win.after_init()

