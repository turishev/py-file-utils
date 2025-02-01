import sys
from os import listdir, walk
from os.path import isfile, isdir, join, getsize


class FileSizeCalculator:
    def __init__(self):
        self.break_walk = False

    def _get_dir_size(self, dir):
        result_size = 0
        for curr_dir, subdirs, files in walk(dir):
            if self.break_walk: return result_size

            for filename in files:
                file_path = join(curr_dir, filename)
                file_size = getsize(file_path)
                # print("%s : %i" % (file_path, file_size))
                result_size += file_size

        return result_size


    def get_dir_size_list(self, root_dir, on_item_cb=None):
        self.break_walk = False
        result = []
        for file in listdir(root_dir):
            print(file)
            if not self.break_walk:
                path = join(root_dir, file)
                item = ()
                if (isfile(path)):
                    item = (file, getsize(path), 'f')
                elif (isdir(path)):
                    item = (file, self._get_dir_size(path), 'd')
                else:
                    item = (file, getsize(path), 's')

                result.append(item)
                if (on_item_cb != None): on_item_cb(item)

        return result


    def stop_calculation(self):
        self.break_walk = True

def file_size_test():
     c = FileSizeCalculator()
     print(c.get_dir_size_list("./"))
     print(c.get_dir_size_list("./", print))

