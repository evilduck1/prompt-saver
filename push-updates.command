#!/bin/bash

cd "$(dirname "$0")"

echo "🔍 Checking git status..."
git status

echo ""
echo "📦 Adding all changes..."
git add -A

echo ""
read -p "✏️ Commit message: " msg

if [ -z "$msg" ]; then
  echo "❌ Commit message required"
  exit 1
fi

git commit -m "$msg"

echo ""
echo "🚀 Pushing to GitHub..."
git push

echo ""
echo "✅ Done. Press Enter to close."
read

