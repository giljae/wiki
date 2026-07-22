#!/bin/bash
# Jupyter Book 빌드 스크립트
# 1. 자동 생성 페이지 (Recent, Index, Tags) 생성
# 2. myst.yml의 {{ year }}를 현재 연도로 치환
# 3. Jupyter Book 빌드
# 4. myst.yml 원복

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

echo "🔄 Restoring myst.yml..."
git checkout myst.yml 2>/dev/null || true

echo "✅ Done!"
