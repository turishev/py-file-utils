import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Gio


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


class ExcludeFilesDialog(Gtk.Dialog):
    def __init__(self, parent, path_list, on_done):
        super().__init__(title="Exclude files from list", transient_for=parent, modal=True)
        self.path_list = path_list
        self.on_done = on_done
        self.set_default_size(600, 150)
        self.connect("response", self.on_response)

        content_area = self.get_content_area()
        content_area.set_vexpand(True)
        content_area.set_margin_top(8)
        content_area.set_margin_start(8)
        content_area.set_margin_end(8)

        self.selector = Gtk.DropDown.new_from_strings(path_list)
        content_area.append(self.selector)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("OK", Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

    def on_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            inx = self.selector.get_selected()
            self.on_done(self.path_list[inx])
        elif response_id == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
            self.on_done('')
        self.destroy()



# def show_confirm_dialog(parent, message, on_ok):
#     def do_act(source_obj, async_res):
#         if source_obj.choose_finish(async_res) == 1:
#             print("OK")
#             on_ok()
#         else:
#             print("Cancel")

#     alert = Gtk.AlertDialog()
#     alert.set_message(message)
#     alert.set_modal(True)
#     alert.set_buttons(["Cancel", "OK"])
#     alert.set_default_button(0)
#     alert.choose(parent, None, do_act)

