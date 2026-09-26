#!/usr/bin/env bash
set -euo pipefail

DOTDIR="$HOME/my-vim-env"
declare -A links=(
  ["$DOTDIR/zsh/.zshrc"]="$HOME/.zshrc"
  ["$DOTDIR/zsh/.zshenv"]="$HOME/.zshenv"
  ["$DOTDIR/zsh/.zprofile"]="$HOME/.zprofile"
  ["$DOTDIR/zsh/.p10k.zsh"]="$HOME/.p10k.zsh"
  ["$DOTDIR/tmux/.tmux.conf"]="$HOME/.tmux.conf"
  ["$DOTDIR/tmux"]="$HOME/.tmux"
  ["$DOTDIR/nvim"]="$HOME/.config/nvim"
  ["$DOTDIR/bin/osc52"]="$HOME/bin/osc52"
  ["$DOTDIR/bin/clip"]="$HOME/bin/clip"
)

case "$(uname)" in
  Darwin)
    links["$DOTDIR/ghostty"]="$HOME/.config/ghostty"
    # Keep an existing independent Mac skhd directory untouched.
    if [[ ! -e "$HOME/.config/skhd" || -L "$HOME/.config/skhd" ]]; then
      links["$DOTDIR/skhd"]="$HOME/.config/skhd"
    fi
    for name in fast fastc arxiv-src opencode ghostty-switch-mode clipboard-to-photos; do
      links["$DOTDIR/bin/$name"]="$HOME/bin/$name"
    done
    links["$DOTDIR/bin/opencode"]="$HOME/.opencode/bin/opencode"
    ;;
  Linux) ;;
  *) printf 'Unsupported host: %s\n' "$(uname)" >&2; exit 1 ;;
esac

# Refuse conflicts before changing anything; never delete another host's data.
for src in "${!links[@]}"; do
  dest=${links[$src]}
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ ! -L "$dest" || "$(readlink "$dest")" != "$src" ]]; then
      printf 'Refusing to replace %s\n' "$dest" >&2
      exit 1
    fi
  fi
done

for src in "${!links[@]}"; do
  dest=${links[$src]}
  if [[ ! -L "$dest" ]]; then
    mkdir -p "$(dirname "$dest")"
    ln -sv "$src" "$dest"
  fi
done
