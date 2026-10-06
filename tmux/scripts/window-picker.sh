#!/bin/sh

# Pick a marked window across all tmux sessions. Keep its active pane ID as
# the target so duplicate window names and session renames are unambiguous.
group=0
query=
nl='
'
while :; do
  windows=$(tmux list-windows -a -F '#{pane_id}	#{session_name}:#{window_index} #{window_name}	#{window_name}')
  counts=$(printf '%s\n' "$windows" | awk -F '\t' '
    index($3, "●") == 1 { a++ }
    index($3, "?") == 1 { b++ }
    index($3, "✓") == 1 { c++ }
    index($3, "○") == 1 { d++ }
    END { print a+0, b+0, c+0, d+0 }
  ')
  set -- $counts
  case $group in
    0) marker=●; first='[●]'; second=' ? '; third=' ✓ '; fourth=' ○ ' ;;
    1) marker=?; first=' ● '; second='[?]'; third=' ✓ '; fourth=' ○ ' ;;
    2) marker=✓; first=' ● '; second=' ? '; third='[✓]'; fourth=' ○ ' ;;
    3) marker=○; first=' ● '; second=' ? '; third=' ✓ '; fourth='[○]' ;;
  esac
  header=$(printf ' %-3s %-3s %-3s %s\n%s %s %s %s' "$1" "$2" "$3" "$4" "$first" "$second" "$third" "$fourth")

  result=$(
    printf '%s\n' "$windows" |
      awk -F '\t' -v marker="$marker" 'index($3, marker) == 1 { print $1 "\t" $2 }' |
      fzf --delimiter "$(printf '\t')" --with-nth 2 --nth 2 \
        --layout reverse --header-first --header "$header" \
        --prompt '←→ tab > ' --query "$query" \
        --expect=left,right --print-query \
        --bind 'alt-up:preview-up,alt-down:preview-down' \
        --preview 'tmux capture-pane -p -e -t {1} -S -500' \
        --preview-window 'right:75%:wrap:follow:border-top' \
        --preview-label '⌥↑↓ scroll'
  )
  status=$?
  query=${result%%"$nl"*}
  rest=${result#*"$nl"}
  key=${rest%%"$nl"*}
  case $key in
    left)  group=$(((group + 3) % 4)); continue ;;
    right) group=$(((group + 1) % 4)); continue ;;
  esac
  [ "$status" -eq 0 ] || exit 0
  selected=${rest#*"$nl"}
  [ "$selected" != "$rest" ] && [ -n "$selected" ] || exit 0
  tmux switch-client -t "$(printf '%s\n' "$selected" | cut -f1)"
  exit
done
