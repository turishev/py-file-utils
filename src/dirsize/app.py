import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio, GLib
from main_window import MainWindow
from actions import AppActions

class MyApp(Adw.Application):
    def __init__(self, file_ops, script_file, auto_run):
        super().__init__()
        self.file_ops = file_ops
        self.script_file = script_file
        self.connect('activate', self.on_activate, auto_run)

    def on_activate(self, app, auto_run):
        print('app: on_activate')
        self.win = MainWindow(application=app)
        self.win.set_root_dir(str(self.file_ops.root_dir))
        self.actions = AppActions(self.win, self.file_ops, self.script_file)
        self.actions.register_actions(self)
        self.win.present()
        if auto_run:
            self.actions.calculate_act_handler()
