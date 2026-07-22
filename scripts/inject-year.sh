#!/bin/bash
# myst.yml의 {{ year }} 플레이스홀더를 현재 연도로 치환
YEAR=$(date +%Y)
sed -i '' "s/{{ year }}/$YEAR/g" myst.yml
