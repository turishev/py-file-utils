from pathlib import Path
from shutil import rmtree;


class FileOps:
    def __init__(self, root_dir):
        self.break_walk = False
        self.eror_handler = None
        self.root_dir = Path(root_dir).absolute()
        if not self.root_dir.is_dir():
            self.root_dir = Path.cwd().absolute()



    def set_error_handler(self, error_handler):
        self.eror_handler = error_handler


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
        self.root_dir = Path(root_dir)
        self.break_walk = False
        result = []

        for file in Path(root_dir).iterdir():
            # print(file)
            if not self.break_walk:
                item = ()
                if (file.is_file()):
                    item = (file.name, file.stat().st_size, 'F')
                elif (file.is_dir()):
                    item = (file.name, self._get_dir_size(file), 'D')
                else:
                    item = (file.name, file.stat().st_size, '*')

                print(item)
                result.append(item)
                if (on_item_cb != None): on_item_cb(item)

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
