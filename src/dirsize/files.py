from pathlib import Path
from shutil import rmtree


class FileOps:
    def __init__(self, root_dir):
        self.break_walk = False
        self.eror_handler = None
        self.root_dir = Path(root_dir).absolute()
        if not self.root_dir.is_dir():
            self.root_dir = Path.cwd().absolute()

    def set_error_handler(self, error_handler):
        self.eror_handler = error_handler

    def get_root_dir(self):
        return str(self.root_dir)

    def set_root_dir(self, dir):
        self.root_dir = Path(dir)

    def _get_dir_size(self, dir, on_iter_cb):
        result_size = Path(dir).stat(follow_symlinks=False).st_size
        for curr_dir, dirs, files in Path.walk(dir, follow_symlinks=False):
            if (not on_iter_cb is None): on_iter_cb()
            if self.break_walk: return result_size

            dir = Path(curr_dir)
            for f in files + dirs:
                path = (dir / f)
                result_size += self.file_size(path)

        return result_size


    def get_dir_size_list(self, on_item_cb=None, on_iter_cb=None):
        self.break_walk = False
        result = []
        try:
            dir = Path(self.root_dir)
            result.append(('.', self.file_size(dir), 'D'))
            # add root_dir size without files

            for file in dir.iterdir():
                if self.break_walk: return result

                try:
                    if file.is_file():
                        item = (file.name, self.file_size(file), 'F')
                    elif file.is_dir():
                        item = (file.name, self._get_dir_size(file, on_iter_cb), 'D')
                    else:
                        item = (file.name, self.file_size(file), '*')

                    result.append(item)
                    if (on_item_cb != None): on_item_cb(item)

                except Exception as e:
                    print(f'Error on check file or dir "{file.name}":{e}')

        except Exception as e:
            print(f'Error 2 on check dir "{self.root_dir}":{e}')
        return result

    def stop_calculation(self):
        self.break_walk = True

    def delete(self, file_name):
        try:
            if not self.root_dir is None:
                file = self.root_dir / file_name
                if file.is_dir():
                    rmtree(file)
                else:
                    file.unlink()
        except Exception as e:
            info = 'delete file error:' + file_name
            print(info)
            print(e)
            if not self.eror_handler is None:
                self.eror_handler(info)


    def file_path(self, file_name):
        if self.root_dir is None:
            raise Exception('file_ops: root_dir is not set')
        else:
            return str((self.root_dir / file_name).absolute())


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
