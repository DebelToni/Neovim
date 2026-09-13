if [[ -o interactive ]]; then
  source ~/.zshrc
fi

export PYTHONPYCACHEPREFIX="/Volumes/SSD/dev-artifacts/pycache"
export PLAYWRIGHT_BROWSERS_PATH="/Volumes/SSD/dev-artifacts/ms-playwright"
export HF_HOME="/Volumes/SSD/huggingface/huggingface"

if [[ "$(uname)" == "Darwin" ]]; then
	export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
else
	. "$HOME/.cargo/env"
	export PATH="$HOME/bin:$PATH"
fi
