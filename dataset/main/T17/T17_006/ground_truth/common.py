"""Shared helpers for one question package (paths, instance loading, solver config, RSS)."""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import json
import os
from pathlib import Path

import gurobipy as gp


class _PMC(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def rss_mb():
    """Current process working set in MB (stage-boundary snapshot, not a continuous peak)."""
    try:
        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        k32 = ctypes.windll.kernel32
        fn = getattr(k32, "K32GetProcessMemoryInfo", None)
        if fn is None:
            fn = ctypes.windll.psapi.GetProcessMemoryInfo
        fn.argtypes = [wt.HANDLE, ctypes.POINTER(_PMC), wt.DWORD]
        fn.restype = wt.BOOL
        if not fn(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            return None
        return round(pmc.WorkingSetSize / (1024 * 1024), 1)
    except Exception:
        return None


def resolve_instance_path(filename: str = "instance.json") -> Path:
    """Find the item instance without relying on the caller's current directory."""
    here = Path(__file__).resolve().parent
    for candidate in (here / filename, here.parent / "public" / filename,
                      here.parent / filename, Path.cwd() / filename):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(filename)


def load_instance() -> dict:
    return json.loads(resolve_instance_path().read_text(encoding="utf-8"))


def configure(m: gp.Model) -> None:
    m.Params.OutputFlag = 0
    m.Params.Threads = 1
    m.Params.Seed = 0
    m.Params.TimeLimit = float(os.environ.get("BENCHMARK_TIME_LIMIT_S", "600"))
    m.Params.MIPGap = 0
