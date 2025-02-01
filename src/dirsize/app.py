import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
from main_window import MainWindow

class MyApp(Adw.Application):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present() # показываем это окно
