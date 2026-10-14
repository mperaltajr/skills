#!/usr/bin/env python3
"""_procs.py: read the process list, and end only processes Slide Lab started.

Owner's rules (2026-10-13): Slide Lab never ends a program by its name, and
never ends one on its own except the browser a render started itself and
recorded. Everything else is listed, read-only, and the user decides.

  table()                  every process: pid, parent pid, start time (and the
                           command line when asked; slower, Windows asks WMI)
  descendants(pid)         processes started by pid (children, grandchildren),
                           never one older than pid itself (a reused number)
  mentioning(path)         processes whose command line contains path
  end(records)             end exactly these (pid, start time) records; a pid
                           whose start time differs is a different program
                           now and is left alone

From a shell (what a locked-folder message tells you to run):
  py -3 scripts/_procs.py --mentioning "<folder>"                 list, read-only
  py -3 scripts/_procs.py --mentioning "<folder>" --end 123 456   end ONLY these,
      and only while each one's command line still contains <folder>. Run it
      only after the user said yes to ending exactly those PIDs.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

WINDOWS = sys.platform == "win32"


# ---------------------------------------------------------------- Windows
def _win_fast_table() -> list[dict]:
    """pid, ppid and start time of every process, in a few milliseconds."""
    import ctypes
    from ctypes import wintypes

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_void_p),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                    ("szExeFile", ctypes.c_wchar * 260)]

    k32 = ctypes.windll.kernel32
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    snap = k32.CreateToolhelp32Snapshot(0x2, 0)          # TH32CS_SNAPPROCESS
    rows = []
    if not snap or snap == wintypes.HANDLE(-1).value:
        return rows
    try:
        e = PROCESSENTRY32W()
        e.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            rows.append({"pid": int(e.th32ProcessID), "ppid": int(e.th32ParentProcessID),
                         "name": e.szExeFile, "started": _win_start(int(e.th32ProcessID)),
                         "command": ""})
            ok = k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    return rows


def _win_start(pid: int) -> float | None:
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x1000, False, pid)              # QUERY_LIMITED_INFORMATION
    if not h:
        return None
    try:
        c, x, k, u = (wintypes.FILETIME() for _ in range(4))
        if not k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(x),
                                   ctypes.byref(k), ctypes.byref(u)):
            return None
        ft = (c.dwHighDateTime << 32) | c.dwLowDateTime
        return (ft - 116444736000000000) / 1e7
    finally:
        k32.CloseHandle(h)


_PS = ("Get-CimInstance Win32_Process | ForEach-Object { "
       "$t = ''; if ($_.CreationDate) { $t = ([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds() }; "
       "\"$($_.ProcessId)`t$($_.ParentProcessId)`t$t`t$($_.Name)`t$($_.CommandLine)\" }")


def _win_full_table() -> list[dict]:
    """The same, plus each command line (asks WMI; about a second). Read-only."""
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS],
                             capture_output=True, text=True, timeout=60,
                             encoding="utf-8", errors="replace").stdout
    except Exception:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("\t", 4)
        if len(parts) < 5 or not parts[0].strip().isdigit():
            continue
        try:
            started = int(parts[2]) / 1000.0 if parts[2].strip() else None
        except ValueError:
            started = None
        rows.append({"pid": int(parts[0]), "ppid": int(parts[1] or 0), "started": started,
                     "name": parts[3], "command": parts[4].strip()})
    return rows


# ---------------------------------------------------------------- POSIX
def _posix_table() -> list[dict]:
    try:
        out = subprocess.run(["ps", "-axo", "pid=,ppid=,lstart=,command="],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split(None, 7)
        if len(parts) < 7:
            continue
        try:
            started = time.mktime(time.strptime(" ".join(parts[2:7]), "%a %b %d %H:%M:%S %Y"))
        except ValueError:
            started = None
        cmd = parts[7] if len(parts) > 7 else ""
        rows.append({"pid": int(parts[0]), "ppid": int(parts[1]), "started": started,
                     "name": os.path.basename(cmd.split(" ")[0]) if cmd else "",
                     "command": cmd})
    return rows


# ---------------------------------------------------------------- shared
def table(with_command: bool = False) -> list[dict]:
    if WINDOWS:
        return _win_full_table() if with_command else _win_fast_table()
    return _posix_table()


def descendants(root_pid: int, rows: list[dict] | None = None) -> list[dict]:
    """Processes root_pid started (any depth). A child must have started after
    its parent: Windows reuses process numbers, and an orphan's parent number
    can point at an unrelated newer process."""
    rows = rows if rows is not None else table()
    by_pid = {r["pid"]: r for r in rows}
    kids: dict[int, list[dict]] = {}
    for r in rows:
        kids.setdefault(r["ppid"], []).append(r)
    out, todo, seen = [], [root_pid], {root_pid}
    while todo:
        p = todo.pop()
        p_start = (by_pid.get(p) or {}).get("started")
        for c in kids.get(p, []):
            if c["pid"] in seen:
                continue
            if p_start is not None and c.get("started") is not None and c["started"] + 1 < p_start:
                continue
            seen.add(c["pid"])
            out.append(c)
            todo.append(c["pid"])
    return out


def _variants(path) -> list[str]:
    s = str(path)
    try:
        s2 = os.path.realpath(s)
    except OSError:
        s2 = s
    out = set()
    for v in (s, s2):
        v = v.rstrip("\\/")
        out |= {v.casefold(), v.replace("\\", "/").casefold(), v.replace("/", "\\").casefold()}
    return [v for v in out if v]


def mentioning(path, rows: list[dict] | None = None) -> list[dict]:
    """Processes (not this one, nor what started it) whose command line
    contains path (or any of several, given a list)."""
    rows = rows if rows is not None else table(with_command=True)
    paths = path if isinstance(path, (list, tuple)) else [path]
    vs = [v for p in paths for v in _variants(p)]
    by_pid = {r["pid"]: r for r in rows}
    me, p = set(), os.getpid()                 # this process and what started it
    while p and p not in me:
        me.add(p)
        p = (by_pid.get(p) or {}).get("ppid") or 0
    return [r for r in rows if r["pid"] not in me and r.get("command")
            and any(v in r["command"].casefold() for v in vs)]


def when(started: float | None) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(started)) if started else "unknown"


def describe(rows: list[dict], width: int = 160) -> list[str]:
    lines = []
    for r in rows:
        cmd = r.get("command") or r.get("name") or ""
        if len(cmd) > width:
            cmd = cmd[: width - 3] + "..."
        lines.append(f"    PID {r['pid']}  started {when(r.get('started'))}  {cmd}")
    return lines


def end(records) -> list[tuple[int, bool, str]]:
    """End exactly these processes. records: (pid, start time) pairs; a process
    whose start time no longer matches is a different program and is skipped."""
    now = {r["pid"]: r for r in table()}
    results = []
    for pid, started in records:
        r = now.get(pid)
        if r is None:
            results.append((pid, True, "already gone"))
            continue
        if started is not None and r.get("started") is not None and abs(r["started"] - started) > 2:
            results.append((pid, False, "that number now belongs to a different program; left alone"))
            continue
        try:
            if WINDOWS:
                import ctypes
                k32 = ctypes.windll.kernel32
                h = k32.OpenProcess(0x0001, False, pid)      # PROCESS_TERMINATE
                if not h:
                    results.append((pid, False, "no permission to end it"))
                    continue
                try:
                    ok = bool(k32.TerminateProcess(h, 1))
                finally:
                    k32.CloseHandle(h)
                if not ok:                       # it may have ended on its own meanwhile
                    time.sleep(0.3)
                    if pid not in {x["pid"] for x in table()}:
                        results.append((pid, True, "already gone"))
                        continue
                results.append((pid, ok, "ended" if ok else "could not end it"))
            else:
                import signal
                os.kill(pid, signal.SIGKILL)
                results.append((pid, True, "ended"))
        except Exception as exc:
            results.append((pid, False, f"could not end it ({exc})"))
    return results


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=(
        "List (read-only) the processes whose command line mentions a folder; with "
        "--end, end ONLY the PIDs named, and only while they still mention it. Use "
        "--end only after the user said yes to ending exactly those PIDs."))
    ap.add_argument("--mentioning", required=True, nargs="+",
                    help="A folder (or any text) to look for; several are allowed.")
    ap.add_argument("--end", nargs="+", type=int, default=None, metavar="PID",
                    help="End only these PIDs (each must still mention the folder).")
    a = ap.parse_args(argv)
    rows = mentioning(a.mentioning)
    what = " or ".join(a.mentioning)
    if a.end is None:
        if not rows:
            print(f"No process has {what} in its command line. A File Explorer "
                  "window or a program that only has the folder open can still hold it: "
                  "close those and try again.")
            return 0
        print(f"Processes whose command line mentions {what} (nothing was ended):")
        print("\n".join(describe(rows)))
        return 0
    listed = {r["pid"]: r for r in rows}
    bad = [p for p in a.end if p not in listed]
    if bad:
        print("Not ended (they do not mention that folder, or are gone): "
              + ", ".join(str(p) for p in bad))
    todo = [(p, listed[p].get("started")) for p in a.end if p in listed]
    results = end(todo)
    for pid, ok, why in results:
        print(f"  PID {pid}: {why}")
    return 0 if not bad and all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
