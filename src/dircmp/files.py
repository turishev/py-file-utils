import pwd
import grp
from pathlib import Path
from shutil import rmtree
from collections import namedtuple

FileInfo = namedtuple('FileInfo', ['path', 'size', 'type', 'owner', 'time'])

class FileOps:
    file_types = {8 : 'file',
                  4 : 'dir',
                  10 : 'link',
                  12 : 'sock',
                  1 : 'pipe',
                  2 : 'char',
                  6 : 'block'}


    def __init__(self, dir_a, dir_b):
        self.break_walk = False
        self.eror_handler = None
        self.dir_a = Path(dir_a).absolute()
        if not self.dir_a.is_dir():
            self.dir_b = Path.cwd().absolute()
        self.dir_b = Path(dir_b).absolute()
        if not self.dir_b.is_dir():
            self.dir_b = Path.cwd().absolute()

    def set_error_handler(self, error_handler):
        self.eror_handler = error_handler

    def get_dir_a(self):
        return str(self.dir_a)

    def get_dir_b(self):
        return str(self.dir_b)

    def set_dir_a(self, dir):
        self.dir_a = Path(dir)

    def set_dir_b(self, dir):
        self.dir_b = Path(dir)

    def _get_dir_file_info(self, root_dir, on_iter_cb):
        result = {}
        for curr_dir, dirs, files in Path.walk(root_dir, follow_symlinks=False):
            if (not on_iter_cb is None): on_iter_cb()
            if self.break_walk: return result

            dir = Path(curr_dir)

            for f in files + dirs:
                path = (dir / f)
                st = path.stat()

                info = FileInfo(
                    path=path,
                    size=st.st_size,
                    time=st.st_mtime,
                    type=self.file_type(st.st_mode),
                    owner=self.owner(st.st_uid, st.st_gid),
                )
                print("info:" + str(info))
                result[str(path.absolute())] = info

        return result


    # def get_dir_size_list(self, on_item_cb=None, on_iter_cb=None):
    #     self.break_walk = False
    #     result = []
    #     try:
    #         dir = Path(self.root_dir)
    #         result.append(('.', self.file_size(dir), 'D'))
    #         # add root_dir size without files

    #         for file in dir.iterdir():
    #             if self.break_walk: return result

    #             try:
    #                 if file.is_file():
    #                     item = (file.name, self.file_size(file), 'F')
    #                 elif file.is_dir():
    #                     item = (file.name, self._get_dir_size(file, on_iter_cb), 'D')
    #                 else:
    #                     item = (file.name, self.file_size(file), '*')

    #                 result.append(item)
    #                 if (on_item_cb != None): on_item_cb(item)

    #             except Exception as e:
    #                 print(f'Error on check file or dir "{file.name}":{e}')

    #     except Exception as e:
    #         print(f'Error 2 on check dir "{self.root_dir}":{e}')
    #     return result

    def stop_calculation(self):
        self.break_walk = True

    # def delete(self, file_name):
    #     try:
    #         if not self.root_dir is None:
    #             file = self.root_dir / file_name
    #             if file.is_dir():
    #                 rmtree(file)
    #             else:
    #                 file.unlink()
    #     except Exception as e:
    #         info = 'delete file error:' + file_name
    #         print(info)
    #         print(e)
    #         if not self.eror_handler is None:
    #             self.eror_handler(info)


    # def file_path(self, file_name):
    #     if self.root_dir is None:
    #         raise Exception('file_ops: root_dir is not set')
    #     else:
    #         return str((self.root_dir / file_name).absolute())


    @staticmethod
    def abs_path(file_name):
        return str(Path(file_name).absolute())

    @staticmethod
    def file_size(file):
        if file.exists(follow_symlinks=False):
            return file.stat(follow_symlinks=False).st_size
        else:
            print(f'file {file} doesn\'t exist')
            return 0

    @staticmethod
    def file_type(mode):
        return FileOps.file_types[mode >> 12]

    @staticmethod
    def owner(uid, gid):
        uname = pwd.getpwuid(uid)[0]
        gname = grp.getgrgid(gid)[0]
        return uname + ":" + gname

    @staticmethod
    def perm(mode):
        return hex(mode & 0o7777)

