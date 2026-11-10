#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

[[ "$(git branch --show-current)" == "main" ]] || { echo "Not on main."; exit 1; }
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "Working tree dirty. Commit first."; exit 1; }

LAST=$(git describe --tags --abbrev=0)
CUR=$(node -p "require('./package.json').version")
IFS=. read -r MA MI PA <<< "$CUR"

echo "Current version: $CUR"
read -rp "What changed? " NOTES
[[ -n "$NOTES" ]] || { echo "Notes required."; exit 1; }
echo "  1) patch   2) minor   3) major"
read -rp "Bump [1]: " B
B="${B:-1}"

case "$B" in
  1) PA=$((PA+1)) ;;
  2) MI=$((MI+1)); PA=0 ;;
  3) MA=$((MA+1)); MI=0; PA=0 ;;
  *) echo "Bad choice"; exit 1 ;;
esac
NEW="$MA.$MI.$PA"; TAG="v$NEW"

echo; echo "About to release $TAG"; read -rp "Continue? [y/N] " ok
[[ "$ok" == "y" ]] || exit 1

perl -pi -e 's/^(\s*"version":\s*")[^"]+(")/${1}'"$NEW"'${2}/' package.json
perl -pi -e 's/^(\s*"version":\s*")[^"]+(")/${1}'"$NEW"'${2}/' src-tauri/tauri.conf.json
perl -0pi -e 's/(\[package\][\s\S]*?version = ")[^"]+/${1}'"$NEW"'/' src-tauri/Cargo.toml
npm install --package-lock-only >/dev/null 2>&1 || true

echo "Building $TAG..."
if ! npm run tauri build; then
  echo "Build failed — reverting version files."
  git checkout -- package.json src-tauri/tauri.conf.json src-tauri/Cargo.toml
  exit 1
fi

BODY=$(git log --pretty='- %s' "$LAST"..HEAD | grep -v '^- release:' || true)
FULL=$(printf '%s\n\n%s\n' "$NOTES" "$BODY")

git add -A
git commit -m "release: $TAG"
git tag -a "$TAG" -m "$TAG"
git push origin main --follow-tags

DMG=$(ls src-tauri/target/release/bundle/dmg/*"$NEW"*.dmg 2>/dev/null | head -1 || true)
[[ -n "$DMG" ]] || DMG=$(ls src-tauri/target/release/bundle/dmg/*.dmg 2>/dev/null | head -1 || true)

if command -v gh >/dev/null 2>&1; then
  if [[ -n "$DMG" ]]; then
    gh release create "$TAG" "$DMG" --title "$TAG" --notes "$FULL"
  else
    gh release create "$TAG" --title "$TAG" --notes "$FULL"
  fi
  echo "Released $TAG."
else
  echo "gh not installed. Tag pushed; finish manually:"
  echo "  https://github.com/evilduck1/prompt-saver/releases/new?tag=$TAG"
fi
