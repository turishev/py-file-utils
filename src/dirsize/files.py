import sys
from os import listdir, walk
from os.path import isfile, isdir, join, getsize


def get_dir_size(root_dir):
    result_size = 0
    for curr_dir, subdirs, files in walk(root_dir):
        print('curr_dir: ' + curr_dir)
        print("subdirs: " + str(subdirs))
        print("files: " + str(files))

        for filename in files:
            file_path = join(curr_dir, filename)
            file_size = getsize(file_path)
            print("%s : %i" % (file_path, file_size))
            result_size += file_size

    return result_size

def dummy_on_item_cb(item): pass

def get_dir_sizes_list(root_dir, on_item_cb = dummy_on_item_cb):
    result = []
    for file in listdir(root_dir):
        path = join(root_dir, file)
        item = ()
        if (isfile(path)):
            item = (path, getsize(path), 'f')
        elif (isdir(path)):
            item = (path, get_dir_size(path), 'd')
        else:
            item = (path, getsize(path), 's')

        result.append(item)
        on_item_cb(item)

    return result
