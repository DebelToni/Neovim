if [[ "$OSTYPE" == darwin* ]]; then
  if [[ -o interactive ]]; then
    source ~/.zshrc
  fi

  export PYTHONPYCACHEPREFIX="/Volumes/SSD/dev-artifacts/pycache"
  export PLAYWRIGHT_BROWSERS_PATH="/Volumes/SSD/dev-artifacts/ms-playwright"
  export HF_HOME="/Volumes/SSD/huggingface/huggingface"
  export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
elif [[ "$OSTYPE" == linux* ]]; then
  export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
  [[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"
fi
