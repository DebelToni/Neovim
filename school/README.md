# School profile

The school-shell image sets `SCHOOL_SHELL=1` and uses the same tracked Neovim configuration with a curated plugin list from `nvim/lua/school.lua`. Daily Mac/DGX startup stays unchanged when that variable is absent.

Retained: Catppuccin, Telescope and its mappings, Oil, mini, Git signs, status line, indent guides, smooth scrolling, matching highlights, which-key, Noice, OSC52 yanks, tmux navigation, Bulgarian mappings, alignment, narrowing, reload diffs and a floating terminal. C/C++ compilation uses the current file's absolute, shell-escaped path. C/C++, Bash and Lua have native LSP completion, diagnostics, definitions, references, renaming, formatting and inlay hints.

Omitted: AI/Copilot/Pi integration, graphics, Markdown/LaTeX rendering, browser preview, SQL UI, Java/Python/Typst run bindings, host services, personal credentials and SSH session auto-attach. Tree-sitter parsers and plugins are preinstalled in the image; editor startup does not install or update dependencies.

`lazy-lock.json` records the selected plugins from the current local dependency snapshot. The image pins this entire repository's commit. `zshrc` carries the portable shell behavior and an ASCII Powerlevel10k prompt. `tmux.conf` preserves the main prefix, pane, copy, popup and split behavior without host-specific paths or plugin bootstrapping.

Container dotfiles load this read-only profile. On an image upgrade, managed dotfiles are refreshed and any replaced custom content is retained under `~/.school-config-backups/`; other home files remain untouched.
