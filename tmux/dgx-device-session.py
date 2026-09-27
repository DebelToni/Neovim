#!/usr/bin/env python3
"""Resume a DGX tmux session last used by this Tailscale SSH device."""

import hashlib
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).resolve()
STATE = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "tmux-devices"
HOOKS = ("client-attached", "client-session-changed", "client-detached")


def tmux(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(("tmux", *args), capture_output=True, text=True)


def device_ip(value: str) -> str | None:
    try:
        address = ipaddress.ip_address(value.split()[0])
    except (ValueError, IndexError):
        return None
    if address in ipaddress.ip_network("100.64.0.0/10") or address in ipaddress.ip_network("fd7a:115c:a1e0::/48"):
        return address.compressed
    return None


def state_path(ip: str) -> Path:
    return STATE / (hashlib.sha256(ip.encode()).hexdigest() + ".json")


def session(target: str) -> tuple[str, str, str] | None:
    result = tmux("display-message", "-p", "-t", target, "#{session_id}\t#{session_name}\t#{session_created}")
    fields = result.stdout.rstrip("\n").split("\t")
    if result.returncode or len(fields) != 3 or not fields[0].startswith("$") or not fields[1] or not fields[2].isdigit():
        return None
    if target.startswith("$") and fields[0] != target:
        return None
    if target.startswith("=") and fields[1] != target[1:]:
        return None
    return tuple(fields)


def saved_target(ip: str) -> str | None:
    try:
        saved = json.loads(state_path(ip).read_text())
        identifier, name, created = (saved[key] for key in ("id", "name", "created"))
    except (OSError, ValueError, KeyError, TypeError):
        return None
    current = session(identifier)
    if current and current[2] == created:
        return identifier
    # Server restart changes session IDs; tmux-resurrect retains named sessions.
    return "=" + name if session("=" + name) else None


def install_hooks() -> None:
    current = tmux("show-hooks", "-g")
    if current.returncode:
        raise RuntimeError(current.stderr.strip())
    for hook in HOOKS:
        indexed = f"{hook}[91]"
        command = f"run-shell '{SCRIPT} record #{{client_pid}} #{{q:session_id}}'"
        present = next((line for line in current.stdout.splitlines() if line.startswith(indexed + " ")), None)
        if present:
            if f"{SCRIPT} record #{{client_pid}} #{{q:session_id}}" not in present:
                raise RuntimeError(f"refusing to replace existing tmux hook {indexed}")
            continue
        result = tmux("set-hook", "-g", indexed, command)
        if result.returncode:
            raise RuntimeError(result.stderr.strip())


def attach() -> None:
    ip = device_ip(os.environ.get("SSH_CONNECTION", ""))
    if not ip:
        print("Per-device tmux needs direct Tailscale SSH; use tmux manually.", file=sys.stderr)
        return
    if tmux("list-sessions").returncode:
        result = tmux("new-session", "-d")
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
    install_hooks()
    target = saved_target(ip)
    result = subprocess.run(("tmux", "attach", "-t", target) if target else ("tmux", "attach"))
    if result.returncode:
        print("tmux attach failed; use tmux manually.", file=sys.stderr)


def record(pid: str, identifier: str) -> None:
    if not pid.isdecimal() or not identifier.startswith("$"):
        return
    try:
        environment = (Path("/proc") / pid / "environ").read_bytes().split(b"\0")
        connection = next(value.split(b"=", 1)[1].decode("ascii") for value in environment if value.startswith(b"SSH_CONNECTION="))
    except (OSError, StopIteration, UnicodeError):
        return
    ip = device_ip(connection)
    details = session(identifier)
    if not ip or not details or details[0] != identifier:
        return
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, pending = tempfile.mkstemp(dir=STATE)
    try:
        with os.fdopen(fd, "w") as output:
            json.dump(dict(zip(("id", "name", "created"), details)), output)
            output.write("\n")
        os.replace(pending, state_path(ip))
    finally:
        if os.path.exists(pending):
            os.unlink(pending)


if __name__ == "__main__":
    os.umask(0o077)
    try:
        if sys.argv[1:] == ["attach"]:
            attach()
        elif len(sys.argv) == 4 and sys.argv[1] == "record":
            record(sys.argv[2], sys.argv[3])
        else:
            raise ValueError("usage: dgx-device-session.py attach|record PID SESSION_ID")
    except (RuntimeError, ValueError) as exc:
        print(f"Per-device tmux: {exc}", file=sys.stderr)
        sys.exit(1)
