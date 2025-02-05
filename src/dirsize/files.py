from pathlib import Path


class FileSizeCalculator:
    def __init__(self):
        self.break_walk = False

    def _get_dir_size(self, dir):
        result_size = 0
        for curr_dir, _, files in Path.walk(dir):
            if self.break_walk: return result_size
            # print(curr_dir);
            dir = Path(curr_dir)
            for filename in files:
                result_size += (dir / filename).stat().st_size

        return result_size


    def get_dir_size_list(self, root_dir, on_item_cb=None):
        self.break_walk = False
        result = []
        for file in Path(root_dir).iterdir():
            # print(file)
            if not self.break_walk:
                item = ()
                if (file.is_file()):
                    item = (file.name, file.stat().st_size, 'f')
                elif (file.is_dir()):
                    item = (file.name, self._get_dir_size(file), 'd')
                else:
                    item = (file.name, file.stat().st_size, 's')

                print(item)
                result.append(item)
                if (on_item_cb != None): on_item_cb(item)

        return result


    def stop_calculation(self):
        self.break_walk = True

def file_size_test():
     c = FileSizeCalculator()
     print(c.get_dir_size_list("./"))
     print(c.get_dir_size_list("./", print))

