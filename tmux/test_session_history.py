"""Test session history and keybindings on an isolated tmux server."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).parent


class SessionHistoryTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.socket = str(Path(directory.name) / "tmux.sock")
        self.env = {**os.environ, "TMUX": ""}
        self.tmux("-f", "/dev/null", "new-session", "-d", "-s", "alpha", "sleep 300")
        self.addCleanup(lambda: self.tmux("kill-server"))
        for name in ("beta", "gamma", "delta"):
            self.tmux("new-session", "-d", "-s", name, "sleep 300")
        self.ids = {name: self.tmux("display-message", "-p", "-t", name, "#{session_id}")
                    for name in ("alpha", "beta", "gamma", "delta")}
        config = (ROOT / ".tmux.conf").read_text()
        block = config.split("# Prefix+Tab returns", 1)[1].split("\n\n", 1)[0]
        self.config = Path(directory.name) / "history.conf"
        self.config.write_text(block[block.index("\n") + 1:].replace(
            "~/.tmux/scripts/session-history.py", str(ROOT / "scripts/session-history.py")))
        self.tmux("source-file", str(self.config))
        self.first = self.attach("alpha")
        self.wait_history(self.first, "alpha")

    def tmux(self, *args):
        return subprocess.check_output(["tmux", "-S", self.socket, *args],
                                       env=self.env, text=True, timeout=5).strip()

    def attach(self, session):
        process = subprocess.Popen(["tmux", "-S", self.socket, "-C", "attach-session",
                                    "-t", session], env=self.env, stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def close():
            process.stdin.close()
            process.wait(timeout=5)
        self.addCleanup(close)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            for line in self.tmux("list-clients", "-F", "#{client_pid}\t#{client_name}").splitlines():
                pid, name = line.split("\t")
                if pid == str(process.pid):
                    return pid, name
            time.sleep(0.02)
        self.fail("Client did not attach")

    def wait_history(self, client, *names):
        expected = " ".join(self.ids[name] for name in names)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            actual = self.tmux("show-options", "-gqv", f"@session-history-{client[0]}")
            if actual == expected:
                return
            time.sleep(0.02)
        self.assertEqual(actual, expected)

    def switch(self, client, name):
        self.tmux("switch-client", "-c", client[1], "-t", name)

    def key(self, client, key):
        self.tmux("send-keys", "-K", "-c", client[1], "C-b", key)

    def test_third_session_native_tab_deduplication_and_reload(self):
        self.key(self.first, "BTab")  # Insufficient history leaves the client alone.
        self.wait_history(self.first, "alpha")
        self.switch(self.first, "beta")
        self.wait_history(self.first, "beta", "alpha")
        self.switch(self.first, "gamma")
        self.wait_history(self.first, "gamma", "beta", "alpha")
        self.tmux("new-window", "-t", "gamma:", "sleep 300")
        self.wait_history(self.first, "gamma", "beta", "alpha")
        self.tmux("source-file", str(self.config))
        self.key(self.first, "BTab")
        self.wait_history(self.first, "alpha", "gamma", "beta")
        self.key(self.first, "Tab")
        self.wait_history(self.first, "gamma", "alpha", "beta")
        self.key(self.first, "BTab")
        self.wait_history(self.first, "beta", "gamma", "alpha")
        self.switch(self.first, "delta")
        self.wait_history(self.first, "delta", "beta", "gamma")

    def test_clients_are_independent_and_closed_target_is_safe(self):
        second = self.attach("delta")
        self.wait_history(second, "delta")
        self.switch(self.first, "beta")
        self.wait_history(self.first, "beta", "alpha")
        self.switch(self.first, "gamma")
        self.wait_history(self.first, "gamma", "beta", "alpha")
        self.wait_history(second, "delta")
        self.tmux("kill-session", "-t", "alpha")
        self.key(self.first, "BTab")
        self.wait_history(self.first, "gamma", "beta", "alpha")
        self.assertEqual(self.tmux("display-message", "-p", "-c", self.first[1],
                                   "#{session_name}"), "gamma")


if __name__ == "__main__":
    unittest.main()
