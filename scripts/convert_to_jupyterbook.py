#!/usr/bin/env python3
"""
Gollum Wiki → Jupyter Book 변환 스크립트 (v2)

1. content/ 디렉토리로 파일 복사 (Home.md → intro.md)
2. Gollum 문법 → MyST 문법 변환 (코드 블록/인라인 코드 보호)
3. 불필요한 Gollum 파일 제거
4. _config.yml, _toc.yml 생성
"""

import re
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# 매핑: 원본 파일 → 목적지 파일
FILE_MAP = {
    "Home.md": "content/intro.md",
    "Getting-Started.md": "content/getting-started.md",
    "Plugins.md": "content/plugins.md",
    "404.md": "content/404.md",
    "ai-agent-architecture/Home.md": "content/ai-agent-architecture/intro.md",
    "ai-agent-architecture/I-model-as-component.md": "content/ai-agent-architecture/i-model-as-component.md",
    "ai-engineering/Home.md": "content/ai-engineering/intro.md",
    "ai-engineering/learning-path.md": "content/ai-engineering/learning-path.md",
    "ai-engineering/role/01-role.md": "content/ai-engineering/role/01-role.md",
    "ai-engineering/role/02-skills.md": "content/ai-engineering/role/02-skills.md",
    "ai-engineering/role/03-responsibilities.md": "content/ai-engineering/role/03-responsibilities.md",
    "ai-engineering/role/04-use-cases.md": "content/ai-engineering/role/04-use-cases.md",
    "evals-for-ai-agents/Home.md": "content/evals-for-ai-agents/intro.md",
    "evals-for-ai-agents/1-introduction-to-evals.md": "content/evals-for-ai-agents/1-introduction-to-evals.md",
    "evals-for-ai-agents/2-human-in-the-loop-evaluation.md": "content/evals-for-ai-agents/2-human-in-the-loop-evaluation.md",
    "evals-for-ai-agents/3-llm-as-a-judge.md": "content/evals-for-ai-agents/3-llm-as-a-judge.md",
    "evals-for-ai-agents/4-programmatic-rule-evaluations.md": "content/evals-for-ai-agents/4-programmatic-rule-evaluations.md",
    "notes/Home.md": "content/notes/intro.md",
    "notes/About.md": "content/notes/about.md",
}

# Gollum 링크 대상 → content/ 내 상대 경로 매핑
# (Gollum 참조명 → content/ 기준 경로)
LINK_TARGET_MAP = {
    "Home": "intro",
    "Getting-Started": "getting-started",
    "Plugins": "plugins",
    "404": "404",
    "notes/About": "notes/about",
    "notes/Home": "notes/intro",
    "About": "notes/about",
    "ai-agent-architecture/Home": "ai-agent-architecture/intro",
    "I-model-as-component": "ai-agent-architecture/i-model-as-component",
    "ai-engineering/Home": "ai-engineering/intro",
    "learning-path": "ai-engineering/learning-path",
    "ai-engineering/role/01-role": "ai-engineering/role/01-role",
    "ai-engineering/role/02-skills": "ai-engineering/role/02-skills",
    "ai-engineering/role/03-responsibilities": "ai-engineering/role/03-responsibilities",
    "ai-engineering/role/04-use-cases": "ai-engineering/role/04-use-cases",
    "evals-for-ai-agents/Home": "evals-for-ai-agents/intro",
    "1-introduction-to-evals": "evals-for-ai-agents/1-introduction-to-evals",
    "2-human-in-the-loop-evaluation": "evals-for-ai-agents/2-human-in-the-loop-evaluation",
    "3-llm-as-a-judge": "evals-for-ai-agents/3-llm-as-a-judge",
    "4-programmatic-rule-evaluations": "evals-for-ai-agents/4-programmatic-rule-evaluations",
    "다른-페이지": "other-page",  # 예시용 — 실제 파일 없음
}


def protect_code_spans(text: str) -> tuple[str, list]:
    """
    코드 블록(```)과 인라인 코드(`)를 보호.
    returns (보호된 텍스트, 복원 리스트)
    """
    placeholders = []

    # 1. 펜스 코드 블록 보호 (```...```)
    def fence_replacer(m):
        idx = len(placeholders)
        ph = f"__CODE_BLOCK_{idx}__"
        placeholders.append(m.group(0))
        return ph

    text = re.sub(r'```[\s\S]*?```', fence_replacer, text)

    # 2. 인라인 코드 보호 (`...`)
    def inline_replacer(m):
        idx = len(placeholders)
        ph = f"__CODE_INLINE_{idx}__"
        placeholders.append(m.group(0))
        return ph

    text = re.sub(r'`[^`]+`', inline_replacer, text)

    return text, placeholders


def restore_code_spans(text: str, placeholders: list) -> str:
    """보호된 코드 복원"""
    for idx, original in enumerate(placeholders):
        text = text.replace(f"__CODE_BLOCK_{idx}__", original)
        text = text.replace(f"__CODE_INLINE_{idx}__", original)
    return text


def convert_wikilinks(text: str, file_path: str) -> str:
    """
    [[Page]] → [Page](path.md)
    [[Page|텍스트]] → [텍스트](path.md)
    코드 블록/인라인 코드는 보호된 상태이므로 안전.
    """

    def replace_fn(m):
        target = m.group(1)
        parts = target.split('|', 1)
        if len(parts) == 2:
            link_target = parts[0].strip()
            display_text = parts[1].strip()
        else:
            link_target = parts[0].strip()
            display_text = link_target

        md_path = resolve_target(link_target, file_path)
        return f'[{display_text}]({md_path})'

    return re.sub(r'\[\[([^\]]+)\]\]', replace_fn, text)


def resolve_target(target: str, from_file: str) -> str:
    """Gollum 참조 → content/ 기준 상대 마크다운 경로"""
    # 이미 .md 확장자 제거
    target_clean = target[:-3] if target.endswith('.md') else target
    target_clean = target_clean.replace('\\', '/')

    # 링크 매핑에서 찾기
    content_path = LINK_TARGET_MAP.get(target_clean)
    if not content_path:
        # 부분 일치 시도 (끝부분 매칭)
        for key, val in LINK_TARGET_MAP.items():
            if key.endswith(target_clean) or target_clean.endswith(key):
                content_path = val
                break
    if not content_path:
        # 모든 키에서 마지막 세그먼트 비교
        target_last = target_clean.split('/')[-1]
        for key, val in LINK_TARGET_MAP.items():
            key_last = key.split('/')[-1]
            if key_last == target_last:
                content_path = val
                break
    if not content_path:
        # 못 찾으면 동일 디렉토리 가정
        return target_clean + ".md"

    # 현재 파일 디렉토리 기준 상대 경로 계산
    from_dir = os.path.dirname(from_file)
    if not from_dir or from_dir == '.':
        return content_path + ".md"

    try:
        rel = os.path.relpath(content_path, from_dir)
        return rel + ".md"
    except ValueError:
        return content_path + ".md"


def convert_admonitions(text: str) -> str:
    """
    <<Note("내용")>> → ```{note}\n내용\n```
    <<Warn("내용")>> → ```{warning}\n내용\n```
    """
    text = re.sub(
        r'<<Note\("([^"]*)"\)>>',
        r'```{note}\n\1\n```',
        text
    )
    text = re.sub(
        r'<<Warn\("([^"]*)"\)>>',
        r'```{warning}\n\1\n```',
        text
    )
    return text


def remove_toc_macro(text: str) -> str:
    """[[_TOC_]] 매크로 제거 (Jupyter Book이 자동 생성)"""
    return re.sub(r'\[\[_TOC_\]\]\s*\n?', '', text)


def convert_file(src_rel: str, dst_rel: str):
    """단일 파일 변환"""
    src_path = ROOT / src_rel
    dst_path = ROOT / dst_rel

    if not src_path.exists():
        print(f"  ⚠️  원본 없음: {src_rel}")
        return

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    raw = src_path.read_text(encoding='utf-8')

    # content/ 기준 상대 경로
    content_rel = dst_rel[len("content/"):] if dst_rel.startswith("content/") else dst_rel

    # 1. 코드 보호
    protected, placeholders = protect_code_spans(raw)

    # 2. Gollum 문법 변환
    protected = remove_toc_macro(protected)
    protected = convert_admonitions(protected)
    protected = convert_wikilinks(protected, content_rel)

    # 3. 코드 복원
    result = restore_code_spans(protected, placeholders)

    dst_path.write_text(result, encoding='utf-8')
    print(f"  ✅ {src_rel} → {dst_rel}")


def create_toc():
    """_toc.yml 생성"""
    print("📋 _toc.yml 생성 중...")
    toc = """# Table of Contents
format: jb-book
root: intro
parts:
  - caption: Getting Started
    chapters:
    - file: content/getting-started
    - file: content/plugins
  - caption: AI Agent Architecture
    chapters:
    - file: content/ai-agent-architecture/intro
      sections:
      - file: content/ai-agent-architecture/i-model-as-component
  - caption: AI Engineering
    chapters:
    - file: content/ai-engineering/intro
      sections:
      - file: content/ai-engineering/learning-path
      - file: content/ai-engineering/role/01-role
      - file: content/ai-engineering/role/02-skills
      - file: content/ai-engineering/role/03-responsibilities
      - file: content/ai-engineering/role/04-use-cases
  - caption: Evals for AI Agents
    chapters:
    - file: content/evals-for-ai-agents/intro
      sections:
      - file: content/evals-for-ai-agents/1-introduction-to-evals
      - file: content/evals-for-ai-agents/2-human-in-the-loop-evaluation
      - file: content/evals-for-ai-agents/3-llm-as-a-judge
      - file: content/evals-for-ai-agents/4-programmatic-rule-evaluations
  - caption: Notes
    chapters:
    - file: content/notes/intro
      sections:
      - file: content/notes/about
"""
    (ROOT / "_toc.yml").write_text(toc, encoding='utf-8')
    print("  ✅ _toc.yml 생성 완료")


def create_config():
    """_config.yml 생성"""
    print("⚙️  _config.yml 생성 중...")
    config = r"""# Jupyter Book configuration
# https://jupyterbook.org/en/stable/customize/config.html

# Book settings
title: "Giljae's Digital Garden"
author: Giljae
copyright: "2024"
logo: assets/favicon.svg
exclude_patterns:
  - ".github/**"
  - "_build/**"
  - "*.py"
  - "scripts/**"
  - "requirements.txt"
  - ".gitignore"

parse:
  myst_enable_extensions:
    - colon_fence
    - deflist
    - dollarmath
    - html_admonition
    - linkify
    - replacements
    - smartquotes
    - substitution
    - tasklist

# HTML-specific settings
html:
  favicon: assets/favicon.svg
  home_page_in_navbar: true
  use_edit_page_button: false
  use_repository_button: true
  use_issues_button: true
  baseurl: "https://wiki.giljae.com"
  extra_navbar: ""
  navbar_number_sections: false

# Repository for edit button
repository:
  url: https://github.com/giljae/wiki
  path_to_book: ""
  branch: main

# Sphinx configuration
sphinx:
  extra_extensions:
    - sphinx_external_toc
    - sphinxcontrib.mermaid
  config:
    myst_heading_anchors: 3
    html_show_copyright: false
    suppress_warnings:
      - myst.strikethrough
"""
    (ROOT / "_config.yml").write_text(config, encoding='utf-8')
    print("  ✅ _config.yml 생성 완료")


def remove_gollum_files():
    """Gollum 전용 파일 제거"""
    print("🗑️  Gollum 전용 파일 제거 중...")
    to_remove = [
        "_Footer.md",
        "_Layout.html",
        "Gemfile",
        "Gemfile.lock",
        "docker-compose.yml",
        ".gollumignore",
        "scripts/build_site.rb",
        "giscus.yml",
        "assets/wiki.js",
        "assets/rouge.css",
    ]
    for f in to_remove:
        p = ROOT / f
        if p.exists():
            p.unlink()
            print(f"  ❌ {f} 제거")
        else:
            print(f"  - {f} 없음 (skip)")

    # 원본 .md 파일 (content/로 이동했으니 제거)
    for src_rel in FILE_MAP:
        p = ROOT / src_rel
        if p.exists():
            p.unlink()
            print(f"  ❌ {src_rel} 제거 (→ content/로 이동)")

    # 빈 디렉토리 정리
    for d in ["ai-agent-architecture", "ai-engineering/role", "ai-engineering",
               "evals-for-ai-agents", "notes", "scripts"]:
        p = ROOT / d
        if p.exists() and not any(p.iterdir()):
            p.rmdir()
            print(f"  ❌ {d}/ (빈 디렉토리 제거)")


def create_requirements():
    """requirements.txt 생성"""
    print("📦 requirements.txt 생성 중...")
    (ROOT / "requirements.txt").write_text(
        "jupyter-book>=2.0\nsphinxcontrib-mermaid\n", encoding='utf-8'
    )
    print("  ✅ requirements.txt 생성 완료")


def update_gitignore():
    """.gitignore 업데이트"""
    print("🔒 .gitignore 업데이트 중...")
    gitignore = ROOT / ".gitignore"
    extra = "\n# Jupyter Book\n_build/\n"
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8')
        if "_build/" not in content:
            content += extra
            gitignore.write_text(content, encoding='utf-8')
            print("  ✅ .gitignore 업데이트 완료")
    else:
        gitignore.write_text(extra, encoding='utf-8')
        print("  ✅ .gitignore 생성 완료")


def main():
    print("=" * 50)
    print("  Gollum Wiki → Jupyter Book 변환")
    print("=" * 50)
    print()

    print("📁 파일 복사 및 변환 중...")
    for src_rel, dst_rel in FILE_MAP.items():
        convert_file(src_rel, dst_rel)
    print()

    create_toc()
    print()
    create_config()
    print()
    remove_gollum_files()
    print()
    create_requirements()
    print()
    update_gitignore()
    print()

    print("=" * 50)
    print("  ✅ 변환 완료!")
    print("  다음 명령으로 빌드 테스트:")
    print("    jupyter-book build .")
    print("=" * 50)


if __name__ == "__main__":
    main()
