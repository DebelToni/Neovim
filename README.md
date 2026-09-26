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
