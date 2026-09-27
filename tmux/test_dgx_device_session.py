"""Isolated DGX tmux device tracking checks; never touches the default server."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name("dgx-device-session.py")
spec = importlib.util.spec_from_file_location("device_session", SCRIPT)
device = importlib.util.module_from_spec(spec)
spec.loader.exec_module(device)


class DeviceSessionTests(unittest.TestCase):
    def test_peer_identity(self):
        self.assertEqual(device.device_ip("100.101.102.103 50000 100.91.66.24 22"), "100.101.102.103")
        self.assertIsNone(device.device_ip("192.168.1.2 50000 192.168.1.3 22"))
        self.assertIsNone(device.device_ip(""))

    @unittest.skipUnless(sys.platform == "linux" and shutil.which("script"), "requires Linux PTY utility")
    def test_isolated_attach_switch_and_resume(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            socket = f"dgx-device-test-{os.getpid()}"
            tmux = bin_dir / "tmux"
            tmux.write_text(f"#!/bin/sh\nexec {shutil.which('tmux')} -L {socket} -f /dev/null \"$@\"\n")
            tmux.chmod(0o755)
            env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}",
                       XDG_STATE_HOME=str(root / "state"), SHELL="/bin/sh", TERM="xterm-256color")
            for key in ("TMUX", "TMUX_PANE", "SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY"):
                env.pop(key, None)

            def run(*args):
                return subprocess.run((str(tmux), *args), env=env, text=True,
                                      capture_output=True, check=True).stdout

            processes = []

            def connect(ip, expected=None):
                before = set(run("list-clients", "-F", "#{client_name}").splitlines())
                client_env = dict(env, SSH_CONNECTION=f"{ip} 50000 100.91.66.24 22")
                process = subprocess.Popen(("script", "-q", "-e", "-c", f"{SCRIPT} attach", "/dev/null"),
                                           env=client_env, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                processes.append(process)
                rows = []
                try:
                    for _ in range(50):
                        rows = [row.split("|") for row in run("list-clients", "-F", "#{client_name}|#{client_session}").splitlines()]
                        added = [row for row in rows if row[0] not in before]
                        if added:
                            name, selected = added[0]
                            if expected:
                                self.assertEqual(selected, expected)
                            return process, name
                        if process.poll() is not None:
                            self.fail("isolated tmux attach exited before connecting: " + process.stdout.read().decode(errors="replace")[-500:])
                        time.sleep(0.1)
                    self.fail("isolated tmux attach timed out")
                finally:
                    if not any(row[0] not in before for row in rows):
                        process.terminate()
                        process.wait(timeout=3)
                        process.stdin.close()
                        process.stdout.close()
                        process.stderr.close()

            def detach(process, name):
                run("detach-client", "-t", name)
                process.stdin.close()
                self.assertEqual(process.wait(timeout=5), 0)
                process.stdout.close()
                process.stderr.close()

            try:
                run("new-session", "-d", "-s", "A", "sleep 30")
                run("new-session", "-d", "-s", "B", "sleep 30")
                first, client = connect("100.101.102.103")
                run("switch-client", "-c", client, "-t", "B")
                state = root / "state/tmux-devices" / (hashlib.sha256(b"100.101.102.103").hexdigest() + ".json")
                self.assertEqual(json.loads(state.read_text())["name"], "B")
                detach(first, client)
                other, client = connect("100.110.120.130", "B")
                run("switch-client", "-c", client, "-t", "A")
                detach(other, client)
                returning, client = connect("100.101.102.103", "B")
                detach(returning, client)
                run("kill-session", "-t", "B")
                self.assertEqual(run("list-sessions", "-F", "#{session_name}").strip(), "A")
                stale, client = connect("100.101.102.103", "A")
                detach(stale, client)
                self.assertEqual(state.stat().st_mode & 0o777, 0o600)
                self.assertEqual(state.parent.stat().st_mode & 0o777, 0o700)
            finally:
                subprocess.run((str(tmux), "kill-server"), env=env, capture_output=True)
                for process in processes:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=3)
                    if not process.stdin.closed:
                        process.stdin.close()
                    if not process.stdout.closed:
                        process.stdout.close()
                    if not process.stderr.closed:
                        process.stderr.close()


if __name__ == "__main__":
    unittest.main()
