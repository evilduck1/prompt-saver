#!/usr/bin/env bash
set -uo pipefail
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1
cd "$(dirname "$0")" || exit 1
[[ -f .gitignore ]] || { echo "No .gitignore here"; exit 1; }
echo "Repo: $(pwd)"; echo
if grep -qE '^/?node_modules/?$' .gitignore; then
  echo "[ignore] node_modules already ignored"
else
  echo "[ignore] node_modules NOT ignored"
  if (( APPLY )); then printf '\nnode_modules/\n' >> .gitignore; echo "[ignore] appended"; else echo "[ignore] would append"; fi
fi
if git ls-files --error-unmatch node_modules >/dev/null 2>&1; then
  echo "[tracked] node_modules IS tracked"
  if (( APPLY )); then git rm -r --cached node_modules >/dev/null; echo "[tracked] untracked"; else echo "[tracked] would untrack"; fi
else
  echo "[tracked] node_modules not tracked"
fi
if [[ -f src/main.js.bak ]]; then
  if git ls-files --error-unmatch src/main.js.bak >/dev/null 2>&1; then
    echo "[backup] main.js.bak tracked"
    if (( APPLY )); then git rm --cached src/main.js.bak >/dev/null; rm -f src/main.js.bak; echo "[backup] untracked + deleted"; else echo "[backup] would untrack + delete"; fi
  else
    echo "[backup] main.js.bak exists, untracked"
    if (( APPLY )); then rm -f src/main.js.bak; echo "[backup] deleted"; fi
  fi
else
  echo "[backup] no main.js.bak"
fi
echo
grep -q '"vite"' package.json 2>/dev/null && echo "[vite] package.json: $(grep -oE '"vite": *"[^"]+"' package.json | head -1)" || echo "[vite] not pinned"
echo "[vite] installed: $(node -p "require('./node_modules/vite/package.json').version" 2>/dev/null || echo none)"
[[ -d "$HOME/node_modules/vite" ]] && echo "[vite] ALSO in ~/node_modules (can shadow local)"
echo
(( APPLY )) && { echo "Done. Review: git status --short"; echo "Then: git add -A && git commit -m \"repo hygiene\" && git push"; } || echo "Report only. Run again with --apply."
