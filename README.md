# my-vim-env

In this repo I have all the configs for all the tools I use in my favorite code edtior - the temrinal.

This repo includes My setup for:
- Neovim
- Tmux
- my zshrc 
- Ghostty shaders 
- custom bash scripts automating my life

## Mac and DGX

Both hosts use the same Git-tracked `zsh/`, `tmux/`, and `nvim/` files.
Keep the checkout at `~/my-vim-env`; `bash wirethings.sh` links the
host's dotfiles without deleting existing files or directories. Ghostty,
skhd, and Mac-only helper links are installed only on macOS. On DGX the
script links the shell, tmux, Neovim, `clip`, and `osc52` configurations.
An existing separate Mac `~/.config/skhd` directory remains untouched.

The Mac keeps Homebrew and `/Volumes/SSD` paths; DGX uses
`~/.local/bin` and avoids the retired WSL/Linuxbrew setup. Tmux selects
the appropriate zsh binary per host. Changing DGX's account login shell
is a separate step. Linux-only plugins and tools such as Oh My Zsh, fzf,
eza, zoxide, and Neovim's external build tools may still need installing;
this repo does not migrate their caches or executable binaries.

## Pi marked-window picker

Tmux leader+v runs `tmux/scripts/window-picker.sh`. It groups marked Pi windows by running, question, done and idle status. Windows with explicit `@pi_title_state=excluded` are omitted from items and counts, even if their names contain a marker.

Native Pi's `--unlisted` or `/unlisted` sets exclusion; `/unlisted off` restores it. This is not a tmux-session filter. Titles remain window-level, while the phone app uses the separate pane-local `@pi_unlisted` flag. Prefix+P and saved-session catalogs remain historical retrieval tools.

Verify the picker with `uv run --no-project python -m unittest tmux/test_window_picker.py`. The test mocks tmux/fzf rather than opening a popup in a live session.
