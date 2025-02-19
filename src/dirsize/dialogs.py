import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Gio


def show_confirm_dialog(parent, message, on_ok):
    def do_act(source_obj, async_res):
        if source_obj.choose_finish(async_res) == 1:
            print("OK")
            on_ok()
        else:
            print("Cancel")

    alert = Gtk.AlertDialog()
    alert.set_message(message)
    alert.set_modal(True)
    alert.set_buttons(["Cancel", "OK"])
    alert.set_default_button(0)
    alert.choose(parent, None, do_act)


def show_open_dir_dialog(parent, init_dir, on_select):
    dialog = Gtk.FileDialog()
    dialog.set_title("Select directory")
    dialog.set_initial_folder(Gio.File.new_for_path(init_dir))

    def _open_callback(_, result):
        try:
            dir = dialog.select_folder_finish(result)
            if dir is not None:
                on_select(dir.get_path())
        except GLib.Error as error:
            print(f"Error opening file: {error.message}")

    dialog.select_folder(parent=parent, callback=_open_callback)
