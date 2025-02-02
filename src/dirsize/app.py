import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio, GLib
from main_window import MainWindow


class MyApp(Adw.Application):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.connect('activate', self.on_activate)

    def create_actions(self):
        quit_act = Gio.SimpleAction(name='quit')
        quit_act.connect('activate', lambda *args: self.win.destroy())
        self.add_action(quit_act)
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.create_actions()
        self.win.present()
