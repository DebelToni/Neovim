#!/usr/bin/env python3
"""Track each tmux client's three most recently visited distinct sessions."""
import subprocess
import sys


def tmux(*args):
    return subprocess.check_output(["tmux", *args], text=True).strip()


def option(pid):
    return f"@session-history-{pid}"


def record():
    clients = tmux("list-clients", "-F", "#{client_pid}\t#{session_id}")
    for line in clients.splitlines():
        pid, current = line.split("\t")
        history = tmux("show-options", "-gqv", option(pid)).split()
        if not history or history[0] != current:
            history = [current, *(session for session in history if session != current)]
            tmux("set-option", "-g", option(pid), " ".join(history[:3]))


def jump(client, pid):
    history = tmux("show-options", "-gqv", option(pid)).split()
    if len(history) < 3:
        tmux("display-message", "-c", client, "Visit three different sessions first")
        return
    target = history[2]
    if target not in tmux("list-sessions", "-F", "#{session_id}").splitlines():
        tmux("display-message", "-c", client, "Third-most-recent session no longer exists")
        return
    tmux("switch-client", "-c", client, "-t", target)


if __name__ == "__main__":
    if sys.argv[1] == "record":
        record()
    elif sys.argv[1] == "jump":
        jump(*sys.argv[2:])
    else:
        raise SystemExit("Expected record or jump CLIENT PID")
