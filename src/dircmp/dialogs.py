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
        self.set_default_size(60, 150)
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



class ExcludeNamesDialog(Gtk.Dialog):
    def __init__(self, parent, on_done):
        super().__init__(title="Exclude files from list", transient_for=parent, modal=True)
        self.on_done = on_done
        self.set_default_size(0, 150)
        self.connect("response", self.on_response)

        content_area = self.get_content_area()
        content_area.set_vexpand(True)
        content_area.set_margin_top(8)
        content_area.set_margin_start(8)
        content_area.set_margin_end(8)

        rbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content_area.append(rbox)

        radio1 = Gtk.CheckButton(label="starts with..")
        radio1.connect("toggled", self.on_radio_toggled, "starts-with")
        rbox.append(radio1)
        radio1.set_active(True)

        radio2 = Gtk.CheckButton(label="ends with..")
        radio2.set_group(radio1)
        radio2.connect("toggled", self.on_radio_toggled, "ends-with")
        rbox.append(radio2)

        radio3 = Gtk.CheckButton(label="contains..")
        radio3.set_group(radio1)
        radio3.connect("toggled", self.on_radio_toggled, "contains")
        rbox.append(radio3)

        radio4 = Gtk.CheckButton(label="regexp")
        radio4.set_group(radio1)
        radio4.connect("toggled", self.on_radio_toggled, "regexp")
        rbox.append(radio4)

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(32)
        self.entry.set_text('.')
        content_area.append(self.entry)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("OK", Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

    def on_radio_toggled(self, button, name):
        if button.get_active():
            self.active_option = name
            print(f"Radio button {name} is active")

    def on_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            self.on_done((self.active_option, self.entry.get_text()))
        elif response_id == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
            self.on_done(('', ''))
        self.destroy()



class ExcludeOperFlagsDialog(Gtk.Dialog):
    def __init__(self, parent, path_list, on_done):
        super().__init__(title="Set flags for paths", transient_for=parent, modal=True)
        self.path_list = path_list
        self.on_done = on_done
        self.set_default_size(60, 150)
        self.connect("response", self.on_response)

        content_area = self.get_content_area()
        content_area.set_vexpand(True)
        content_area.set_margin_top(8)
        content_area.set_margin_bottom(16)
        content_area.set_margin_start(8)
        content_area.set_margin_end(8)
        content_area.set_spacing(16)

        self.selector = Gtk.DropDown.new_from_strings(path_list)
        content_area.append(self.selector)

        box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_1.set_spacing(16)
        content_area.append(box_1)

        self.a_to_b_cb = self.make_cb('A->B', box_1)
        self.del_a_cb = self.make_cb('del A', box_1)
        self.b_to_a_cb = self.make_cb('B->A', box_1)
        self.del_b_cb = self.make_cb('del B', box_1)
        
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("OK", Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

    def on_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            inx = self.selector.get_selected()
            self.on_done(path=self.path_list[inx],
                         a_to_b=self.a_to_b_cb.get_active(),
                         del_a=self.del_a_cb.get_active(),
                         b_to_a=self.b_to_a_cb.get_active(),
                         del_b=self.del_b_cb.get_active())

        elif response_id == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
            self.on_done()
        self.destroy()

    def make_cb(self, label, box):
        box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cb = Gtk.CheckButton()
        box_1.append(cb)
        box_1.append(Gtk.Label.new_with_mnemonic(label))
        box.append(box_1)
        return cb



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
