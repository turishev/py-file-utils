from __future__ import annotations # for list annotations
from typing import TypeAlias

import enum
from dataclasses import dataclass
from collections import namedtuple

from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileInfo:
    path : str
    size : int
    type : str
    owner : str
    time : float

@dataclass(frozen=True, slots=True)
class CompareResultItem:
    name : str
    diff : str
    file_a : FileInfo | None
    file_b : FileInfo | None


@enum.unique
class OperType(enum.Enum):
    NOTHING = 0
    COPY_AB = 1
    COPY_BA = 2
    MOVE_AB = 3
    MOVE_BA = 4
    DEL_A = 5
    DEL_B = 6
    DEL_AB = 7

@dataclass(frozen=True, slots=True)
class Oper:
    type : OperType
    path_a : str
    path_b : str

@enum.unique
class SyncDirection(enum.Enum):
    BOTH = 0
    A_TO_B = 1
    B_TO_A = 2
    
@dataclass(frozen=True, slots=True)
class SyncOptions:
    sync_direction : SyncDirection
    check_size : bool
    check_time : bool
    check_content : bool
