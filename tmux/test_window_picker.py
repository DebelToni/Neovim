"""Exercise the marked-window picker without touching the live tmux server."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


PICKER = Path(__file__).parent / "scripts/window-picker.sh"


class WindowPickerTest(unittest.TestCase):
    def test_questionnaire_group_count_navigation_and_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tmux = root / "tmux"
            tmux.write_text("""#!/bin/sh
case "$1" in
  list-windows) printf '%%1\\tDemo:1 ● Running\\t● Running\\n%%2\\tDemo:2 ✓ Done\\t✓ Done\\n%%3\\tDemo:3 ○ Idle\\t○ Idle\\n%%4\\tDemo:4 ? Review\\t? Review\\n' ;;
  switch-client) printf '%s\\n' "$3" > "$PICKER_SELECTION" ;;
  *) exit 1 ;;
esac
""")
            fzf = root / "fzf"
            fzf.write_text("""#!/bin/sh
call=0
[ ! -f "$PICKER_CALLS" ] || read -r call < "$PICKER_CALLS"
call=$((call + 1))
printf '%s\\n' "$call" > "$PICKER_CALLS"
printf '%s\\n' "$@" > "$PICKER_ROOT/args$call"
cat > "$PICKER_ROOT/items$call"
if [ "$call" -lt 2 ]; then printf '\\nright\\n'; else printf '\\n\\n%%4\\tDemo:4 ? Review\\n'; fi
""")
            tmux.chmod(0o755)
            fzf.chmod(0o755)
            env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}",
                   "PICKER_CALLS": str(root / "calls"), "PICKER_ROOT": str(root),
                   "PICKER_SELECTION": str(root / "selection")}
            result = subprocess.run(["sh", str(PICKER)], env=env, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / "selection").read_text(), "%4\n")
            self.assertIn("[?]", (root / "args2").read_text())
            self.assertIn("? Review", (root / "items2").read_text())
            self.assertNotIn("● Running", (root / "items2").read_text())
            self.assertRegex((root / "args2").read_text(), r"1\s+1\s+1\s+1")


if __name__ == "__main__":
    unittest.main()
