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


@enum.unique
class DiffType(enum.Enum):
    EQ = 0
    A = 1
    B = 2
    TIME = 3
    SIZE = 4
    TYPE = 5
    OWNER = 6
    CONTENT = 7


@dataclass(frozen=True, slots=True)
class CompareResultItem:
    name : str
    diff : DiffType
    file_a : FileInfo
    file_b : FileInfo


@enum.unique
class OperType(enum.Enum):
    COPY = 0
    MOVE = 1

@dataclass(frozen=True, slots=True)
class Oper:
    type : OperType
    src : Path
    dst : Path
