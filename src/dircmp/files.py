from __future__ import annotations # for list annotations
from typing import TypeAlias
from collections.abc import Callable


import pwd
import grp
from pathlib import Path, PurePath
# from hashlib import file_digest
import hashlib


from app_types import *

_file_types = {8 : 'file',
               4 : 'dir',
               10 : 'link',
               12 : 'sock',
               1 : 'pipe',
               2 : 'char',
               6 : 'block'}


_break_operations = False
_dummy_file_info  = FileInfo(path='', type='', size=0, owner='', time=0)

def file_size(file):
    if file.exists(follow_symlinks=False):
        return file.stat(follow_symlinks=False).st_size
    else:
        print(f'file {file} doesn\'t exist')
        return 0


def file_type(mode):
    return _file_types.get(mode >> 12, '?')


def owner(uid, gid):
    uname = pwd.getpwuid(uid)[0]
    gname = grp.getgrgid(gid)[0]
    return uname + ":" + gname


def perm(mode):
    return hex(mode & 0o7777)


def _get_file_info(path : Path):
    if path.exists():
        st = path.stat()

        return FileInfo(
            path=str(path),
            size=st.st_size,
            time=st.st_mtime,
            type=file_type(st.st_mode),
            owner=owner(st.st_uid, st.st_gid),
        )
    else:
        print(f"file '{str(path)}' doesn't exists")
        return _dummy_file_info

def break_operations():
    global _break_operations
    _break_operations = True


def calculate_file_hash(file_path: Path, algorithm="md5"):
    if file_path.exists():
        hasher = hashlib.new(algorithm)
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    else: return ''

def _compare_content(path_a : str, path_b : str):
    d1 = calculate_file_hash(Path(path_a))
    d2 = calculate_file_hash(Path(path_b))
    return d1 == d2


def _compare_info(info_a : FileInfo | None, info_b : FileInfo | None, opts : SyncOptions) -> str:
    if info_a.type == ''  and info_b == '': return ''
    if info_a.type == '' and info_b.type != '': return 'B'
    if info_a.type != '' and info_b.type == '': return 'A'

    res = ''

    if info_a.type != info_b.type: res = res + 'f'
    if opts.check_size and info_a.size != info_b.size: res = res + 's'
    if opts.check_time and info_a.time != info_b.time: res = res + 't'
    if opts.check_content and (info_a.size != info_b.size or not _compare_content(info_a.path, info_b.path)): res = res + 'c'
    # if info_a.owner != info_b.owner: res = res + 'o'
    return res



def _compare_dirs(dir_a : Path, dir_b : Path, opts : SyncOptions, reverse_dir=False, result={},
                  on_item : Callable[[CompareResultItem], None] | None =None) -> None:
    global _break_operations
    dir_a_len = len(str(dir_a))

    for pcur_dir, _, files in Path.walk(dir_a, follow_symlinks=False):
        sub_dir = str(pcur_dir)[dir_a_len:]
        cur_dir_b = Path(str(dir_b) + sub_dir)

        for f in files:
           if _break_operations:
               _break_operations = False
               return

           name = f if sub_dir == '' else str(PurePath(sub_dir[1:], f))

           if result.get(name) is None:
               path_a = pcur_dir / f
               path_b = (cur_dir_b / f).resolve()
               info_a = _get_file_info(path_a)
               info_b = _get_file_info(path_b) if path_b.exists() else FileInfo(path=str(path_b), type='', size=0, owner='', time=0)
               diff = _compare_info(info_b, info_a, opts) if reverse_dir else _compare_info(info_a, info_b, opts)
               file_a = info_a if not reverse_dir else info_b
               file_b = info_b if not reverse_dir else info_a
               item = CompareResultItem(name=name, diff=diff, file_a=file_a, file_b=file_b)
               result[name] = item
               if on_item is not None and diff != '': on_item(item)


def compare_dirs(dir_a : str, dir_b : str, opts : SyncOptions,
                 on_item : Callable[[CompareResultItem], None] | None =None
                 ) -> list[CompareResultItem]:
    global _break_operations
    _break_operations = False

    adir_a = Path(dir_a).resolve()
    adir_b = Path(dir_b).resolve()
    result={}

    if opts.sync_direction != SyncDirection.B_TO_A:
        _compare_dirs(adir_a, adir_b, opts, False, result, on_item)
    if opts.sync_direction != SyncDirection.A_TO_B and not _break_operations:
        _compare_dirs(adir_b, adir_a, opts, True, result, on_item)
    return [v for v in result.values() if v.diff != ''] # return only different files


def execute_operations(oper_list : list[Oper], logger : Callable[[str], None]) -> None:
    global _break_operations
    _break_operations = False

    for oper in oper_list:
        if _break_operations:
            _break_operations = False
            return
        print(oper)
        if oper.type == OperType.COPY_AB:
            logger(f"CP: {oper.path_a} -> {oper.path_b}")
        elif oper.type == OperType.COPY_BA:
            logger(f"CP: {oper.path_b} -> {oper.path_a}")
        elif oper.type == OperType.MOVE_AB:
            logger(f"MV: {oper.path_a} -> {oper.path_b}")
        elif oper.type == OperType.MOVE_BA:
            logger(f"MV: {oper.path_b} -> {oper.path_a}")
        elif oper.type == OperType.DEL_A:
            logger(f"RM: {oper.path_a}")
        elif oper.type == OperType.DEL_B:
            logger(f"RM: {oper.path_b}")
        elif oper.type == OperType.DEL_AB:
            logger(f"RM: {oper.path_a}")
            logger(f"RM: {oper.path_b}")
        


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


def make_path_list(path : str) -> list[str]:
    '''split a path into list of partial paths'''
    path_list = []
    for s in PurePath(path).parts:
        if path_list == []: path_list.append(s)
        else: path_list.append(str(PurePath(path_list[-1], s)))
    path_list.reverse()
    return path_list
