# Login-shell setup shared by the Mac and DGX.
if [[ "$OSTYPE" == darwin* ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
  export PATH="/opt/homebrew/bin:$PATH"
  export PATH="$(brew --prefix postgresql@17)/bin:$PATH"
elif [[ "$OSTYPE" == linux* ]]; then
  export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi

export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ]] && source "$SDKMAN_DIR/bin/sdkman-init.sh"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && source "$NVM_DIR/bash_completion"

if [[ "$OSTYPE" == darwin* ]] && command -v brew &>/dev/null; then
  eval "$(brew shellenv)"
fi
