#!/bin/bash
# Jupyter Book 빌드 스크립트
set -e

echo "📄 Running page generator..."
python3 scripts/generate-pages.py

YEAR=$(date +%Y)
echo "🔧 Injecting year: $YEAR"

if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/{{ year }}/$YEAR/g" myst.yml
else
  sed -i "s/{{ year }}/$YEAR/g" myst.yml
fi

echo "🏗️  Building Jupyter Book..."
BASE_URL=${BASE_URL:-https://wiki.giljae.com} jupyter-book build --html

echo "🔧 Post-processing: injecting missing route module imports..."
python3 scripts/post-build.py

echo "🔄 Restoring myst.yml..."
git checkout myst.yml 2>/dev/null || true

echo "✅ Done!"
