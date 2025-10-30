from __future__ import annotations # for list annotations
from typing import TypeAlias
from collections.abc import Callable


import pwd
import grp
from pathlib import Path
#from shutil import rmtree
#from collections import namedtuple

from app_types import *

_file_types = {8 : 'file',
               4 : 'dir',
               10 : 'link',
               12 : 'sock',
               1 : 'pipe',
               2 : 'char',
               6 : 'block'}


_break_walk = False

def _get_file_info(path : Path):
    st = path.stat()

    return FileInfo(
        path=str(path),
        size=st.st_size,
        time=st.st_mtime,
        type=file_type(st.st_mode),
        owner=owner(st.st_uid, st.st_gid),
    )


def _compare_info(info_a : FileInfo | None, info_b : FileInfo | None) -> str:
    if info_a is None and info_b is None: return ''
    if info_a is None and info_b is not None: return 'B'
    if info_a is not None and info_b is None: return 'A'

    res = ''

    if info_a.size != info_b.size: res = res + 's'
    if info_a.type != info_b.type: res = res + 'f'
    if info_a.time != info_b.time: res = res + 't'
    # if info_a.owner != info_b.owner: res = res + 'o'
    return res


def _compare_dirs(dir_a : Path, dir_b : Path, reverse_dir=False, result={},
                  on_item : Callable[[CompareResultItem], None] | None =None):
    global _break_walk
    dir_a_len = len(str(dir_a))

    for pcur_dir, _, files in Path.walk(Path(dir_a), follow_symlinks=False):
        if _break_walk: return

        sub_dir = str(pcur_dir)[dir_a_len:]
        cur_dir_b = Path(str(dir_b) + sub_dir)

        for f in files:
            name = (sub_dir[1:] if sub_dir != '' and sub_dir[0] == '/' else sub_dir) + f

            if result.get(name) is None:
                path_a = pcur_dir / f
                path_b = (cur_dir_b / f).resolve()
                info_a = _get_file_info(path_a)
                info_b = _get_file_info(path_b) if path_b.exists() else None
                diff = _compare_info(info_b, info_a) if reverse_dir else _compare_info(info_a, info_b)
                file_a = info_a if not reverse_dir else info_b
                file_b = info_b if not reverse_dir else info_a
                item = CompareResultItem(name=name, diff=diff, file_a=file_a, file_b=file_b)
                result[name] = item
                if on_item is not None and diff != '': on_item(item)


def compare_dirs(dir_a : str, dir_b : str,
                 on_item : Callable[[CompareResultItem], None] | None =None
                 ) -> list[CompareResultItem]:
    global _break_walk

    adir_a = Path(dir_a).resolve()
    adir_b = Path(dir_b).resolve()
    _break_walk = False
    result={}
    _compare_dirs(adir_a, adir_b, False, result, on_item)
    _compare_dirs(adir_b, adir_a, True, result, on_item)
    return [v for v in result.values() if v.diff != ''] # return only different files


def stop_calculation():
    global _break_walk
    _break_walk = True

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


def file_size(file):
    if file.exists(follow_symlinks=False):
        return file.stat(follow_symlinks=False).st_size
    else:
        print(f'file {file} doesn\'t exist')
        return 0


def file_type(mode):
    return _file_types[mode >> 12]


def owner(uid, gid):
    uname = pwd.getpwuid(uid)[0]
    gname = grp.getgrgid(gid)[0]
    return uname + ":" + gname


def perm(mode):
    return hex(mode & 0o7777)
