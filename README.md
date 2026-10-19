# my-vim-env

My terminal is my editor. These are the Neovim, tmux, zsh, Ghostty and iPad keyboard configs behind it.

There's a lot here, including experiments, old integrations and paths specific to my machines. Pick something useful from the catalogue below and steal that piece. Installing the entire setup will bring along assumptions you probably don't want.

## Things worth stealing

### tmux and remote work

| Idea | What it does | Implementation |
| --- | --- | --- |
| Catppuccin with a workspace that survives restarts | Rounded window tabs, session and clock modules, plus tmux-resurrect pane-content capture and tmux-continuum saves every 15 minutes with automatic restore. Process restoration is disabled: running jobs don't resume. | [Theme, TPM plugins and restore settings](tmux/.tmux.conf) |
| Navigate editor splits and terminal panes with the same keys | Ctrl+h/j/k/l bindings plus vim-tmux-navigator connect Neovim split navigation to tmux. Check the directional mappings when adapting: this config also contains custom tmux bindings. | [Navigator plugin](nvim/lua/plugins/vim-tmux-navigator.lua), [editor keys](nvim/lua/config/keybinds.lua), [tmux keys](tmux/.tmux.conf) |
| Resume where each device left off | Remembers the last tmux session used by each Tailscale SSH device, so reconnecting from an iPad doesn't inherit another device's choice. Linux-specific. | [Device tracking](tmux/dgx-device-session.py), [shell entry point](zsh/.zshrc) |
| Three-session muscle memory | Prefix+Tab returns to the previous session; Prefix+Shift+Tab jumps to the third-most-recent distinct session. History is per client. | [History helper](tmux/scripts/session-history.py), [bindings and hooks](tmux/.tmux.conf) |
| A dashboard for agent windows | Prefix+v opens an fzf picker grouped by running, question, done and idle, with pane previews and counts. Excluded windows stay out. | [Window picker](tmux/scripts/window-picker.sh) |
| Park a window without leaving your work | Prefix+b moves a window into background session `B`; Prefix+Shift+b moves it to the next session and follows it. | [tmux bindings](tmux/.tmux.conf) |
| Copy from a remote agent to your local clipboard | Pipe text to `clip`. It uses OSC 52 over SSH, including from captured subprocesses inside tmux, and the native clipboard on a local Mac. | [`clip`](bin/clip), [`osc52`](bin/osc52) |
| Open the current Git remote | Prefix+g opens the repository in a local browser, or copies its URL over SSH. | [tmux bindings](tmux/.tmux.conf) |
| Keep Mac and iPad shortcuts consistent | Command+number selects tmux windows; Command+Option+Up/Down switches sessions using explicit terminal key sequences. | [Ghostty keys](ghostty/config), [iPad keys](ipad/rootshell-blink-keybindings.conf), [tmux decoding](tmux/.tmux.conf) |

The agent picker consumes Pi window-title markers (`●`, `?`, `✓`, `○`) and the `@pi_title_state` option. The Pi integration that publishes them is outside this repo. Prefix+P also calls an external Pi session finder, not a bundled script.

### Neovim

| Idea | What it does | Implementation |
| --- | --- | --- |
| Catppuccin Mocha throughout the editor | A matching editor palette and lualine status with Git branch, diff, diagnostics and cursor position. | [Colorscheme](nvim/lua/plugins/catppuccin.lua), [status line](nvim/lua/plugins/lua-line.lua) |
| Switch from file search to text search without retyping | Ctrl+g and Ctrl+f switch Telescope between live grep and file search while preserving the query, in a nearly full-screen vertical layout with a large preview. Live grep needs ripgrep. | [Telescope setup](nvim/lua/plugins/telescope.lua) |
| Compile a document and open its PDF | Leader+ct builds Typst, Leader+cx builds LaTeX with Tectonic, and Leader+cp chooses from the current buffer. Saves changes, compiles asynchronously and reports failures. Disabled in the school profile. | [Document compiler bindings](nvim/lua/config/typst_compile_keybind.lua) |
| Return to the same place in a file | Saves and restores buffer views, including cursor and scroll position, without restoring hidden folds. | [View persistence](nvim/init.lua) |
| Vim keys on a Bulgarian layout | Translates Bulgarian-layout input for normal commands and mappings, including mappings added later. | [Bulgarian support](nvim/lua/config/bulgarian.lua) |
| Edit just one region | Opens a selected range in a separate buffer; writing it updates the original region using extmarks. | [Narrow buffer](nvim/lua/config/myscripts/narrow_buffer.lua) |
| See what changed on reload | Highlights lines changed by an external file reload, useful when an agent is editing alongside you. | [Reload highlights](nvim/lua/config/myscripts/reload_diff_highlight.lua) |
| Ask Pi about code, review its edits | Floating chat for the cursor or selection, follow-up questions, and proposed edits you can accept or reject. Requires the Pi CLI. | [Pi integration](nvim/lua/config/myscripts/pi_explain.lua) |
| Align by a pattern | Aligns the first regex match across a range, accounting for display columns and tabs. | [Alignment helper](nvim/lua/config/align.lua) |
| A reusable floating terminal | Toggle a terminal or send C, Python and Maven commands to it. | [Floating terminal](nvim/lua/config/myscripts/floating_terminal.lua) |
| Images inside tmux | Configures image rendering around editor focus and the active tmux window, with graphics cleanup on exit. Needs a compatible terminal and image dependencies. | [image.nvim setup](nvim/lua/plugins/image.lua), [tmux passthrough](tmux/.tmux.conf) |
| Read Markdown without hiding source | Markdown rendering with conceal disabled, so HTML comments and other source text remain visible. | [Renderer](nvim/lua/plugins/markdown-nvim.lua), [editor defaults](nvim/init.lua) |

Check [init.lua](nvim/init.lua) and [plugin loading](nvim/lua/config/lazy.lua) before borrowing a module. Some other files are disabled experiments; the school profile also changes what loads.

### Shell helpers and terminal toys

| Idea | What it does | Implementation |
| --- | --- | --- |
| A shell built around interactive navigation | Powerlevel10k prompt, autosuggestions, syntax highlighting, fzf-tab completion and zoxide-backed `cd`. Tools and plugins need installing separately. | [zsh setup](zsh/.zshrc), [prompt configuration](zsh/.p10k.zsh) |
| Fuzzy-pick your next destination | `cdf` changes to a picked file's directory; `openf` opens that directory in the host's file manager; `inv` picks files for Neovim with bat previews. | [fzf helpers](zsh/.zshrc) |
| Readable directory listings | `ls` uses eza with Git status, icons and relative modification times; passing a directory switches to a one-level tree view. | [`eza-ls`](zsh/.zshrc) |
| `cat` an image | Shows a single image at terminal width using Kitty graphics, wraps it for tmux, and clears the shell preview before the next command. | [`cat` and graphics hooks](zsh/.zshrc) |
| Recover an agent conversation from scrollback | `pic` resumes the last `pi --session` command found in the pane; `clippi` also captures a message and copies it to the clipboard. | [Pi shell helpers](zsh/.zshrc) |
| Ask for a shell command before running it | `how` asks Pi for a command, displays it and waits for confirmation. Model/provider settings are personal; review the output before approving execution. | [`how`](zsh/.zshrc) |
| Delayed clipboard | `clip10` accepts multiline text and copies it after ten seconds. | [`clip10`](zsh/.zshrc) |
| Read a paper's source | `arxiv-src` accepts an arXiv URL or ID, downloads its source bundle and identifies a likely main TeX file. | [`arxiv-src`](bin/arxiv-src) |
| Stack Ghostty visual modes | Combine base settings, transparency, lightsaber effects, hacker mode and a bouncing horse shader. | [Mode switcher](ghostty/modes/switch_mode.sh), [layers](ghostty/modes/), [horse shader](ghostty/horse_dvd.glsl) |
| Mac apps on Ctrl+number | Global shortcuts open Safari, Ghostty, Finder, Notes, Preview and chat apps without going through the Dock. Requires skhd on macOS. | [App shortcuts](skhd/skhdrc) |
| Send a clipboard image straight to Photos | Ctrl+Command+Shift+6 exports the clipboard image as PNG and imports it into Photos. macOS-only; adapt the helper path in the skhd binding. | [Clipboard importer](bin/clipboard-to-photos), [shortcut](skhd/skhdrc) |

## Bring your agent

Point your coding agent at this repository and tell it which idea you want. For example:

> Look up the Catppuccin, tmux-resurrect and continuum setup in DebelToni/Neovim. Adapt that combination to my existing tmux config. Explain what gets restored and what doesn't, identify the required plugins, preserve my bindings, and verify it on an isolated server before changing my live setup. Don't install the whole dotfiles repo.

Agents: follow the linked implementation through its callers, configuration and tests. Ask your owner about choices that affect their workflow. Replace my usernames, paths, hostnames, provider settings and external integrations with what actually fits their environment. Keep unrelated settings untouched and explain any behavior you leave out.

## Working on this setup

My checkout lives at `~/my-vim-env`, shared between a Linux DGX host and a Mac. [wirethings.sh](wirethings.sh) links host-appropriate files and refuses to replace conflicting files or directories. It does not install all dependencies or make the setup portable; read it before considering it for your own machine.

The tmux helpers have focused checks using mocks or isolated servers, without reloading the live configuration:

```sh
uv run --no-project python -m unittest discover -s tmux -p 'test_*.py'
```
