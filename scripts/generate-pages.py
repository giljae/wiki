#!/usr/bin/env python3
"""
Jupyter Book 자동 생성 페이지: Recent, Index, Tags

빌드 시점에 실행되어 content/_generated/ 디렉토리에
최신 상태의 페이지를 생성합니다.
"""

import os
import re
import subprocess
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUT = CONTENT / "_generated"
OUTPUT.mkdir(parents=True, exist_ok=True)

# 제외할 파일들
EXCLUDE = {
    "404.md",
    "intro.md",
    "getting-started.md",
    "plugins.md",
    "README.md",
}


def get_git_date(filepath: str) -> str:
    """Git log에서 파일의 최근 커밋 날짜 조회 (rename 추적 포함)"""
    try:
        rel = os.path.relpath(filepath, str(ROOT))
        # --follow 로 rename 이력까지 추적
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ai", "--follow", "--", rel],
            capture_output=True, text=True, cwd=str(ROOT), timeout=5
        )
        date_str = result.stdout.strip()
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d")

        # fallback: 원본 경로 (Gollum 시절) 확인
        # content/ai-agent-architecture/architecture-overview.md → ai-agent-architecture/Home.md
        orig = rel.replace("content/", "").replace("_generated/", "")
        orig = orig.replace("architecture-overview.md", "Home.md")
        orig = orig.replace("engineering-overview.md", "Home.md")
        orig = orig.replace("evals-overview.md", "Home.md")
        orig = orig.replace("notes-overview.md", "Home.md")
        orig = orig.replace("notes/", "")
        if orig != rel.replace("content/", "").replace("_generated/", ""):
            result2 = subprocess.run(
                ["git", "log", "-1", "--format=%ai", "--follow", "--", orig],
                capture_output=True, text=True, cwd=str(ROOT), timeout=5
            )
            date_str2 = result2.stdout.strip()
            if date_str2:
                dt = datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S %z")
                return dt.strftime("%Y-%m-%d")

        return "1970-01-01"
    except Exception:
        return "1970-01-01"


def parse_front_matter(content: str):
    """YAML front matter 파싱 (PyYAML 사용)"""
    import yaml
    fm = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass
    return fm


def get_title(content: str) -> str:
    """Markdown에서 첫 번째 # 제목 추출"""
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return "Untitled"


def get_section(filepath: str) -> str:
    """파일 경로로부터 섹션명 추출"""
    rel = os.path.relpath(filepath, str(CONTENT))
    parts = rel.split(os.sep)
    if len(parts) > 1:
        return parts[0]
    return "General"


def parse_tags(fm: dict) -> list:
    """tags 필드 파싱"""
    tags = fm.get("tags", [])
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if t]
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    return []


def slugify(text: str) -> str:
    """URL slug 생성"""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9가-힣\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def generate_recent():
    """Recent 페이지 생성 — Git 최근 수정일 순"""
    pages = []
    for f in sorted(CONTENT.rglob("*.md")):
        if f.name in EXCLUDE or "_generated" in str(f):
            continue
        rel = os.path.relpath(f, str(CONTENT))
        content = f.read_text(encoding="utf-8")
        fm = parse_front_matter(content)
        title = fm.get("title") or get_title(content)
        date = get_git_date(str(f))
        section = get_section(str(f))
        pages.append({
            "title": title,
            "date": date,
            "path": rel.replace("\\", "/").replace(".md", ""),
            "section": section,
        })

    # 날짜 내림차순 정렬
    pages.sort(key=lambda p: p["date"], reverse=True)

    lines = [
        "---",
        "tags: [wiki, recent]",
        "description: 최근 변경된 문서 목록",
        "---",
        "",
        "# Recent Changes",
        "",
        "최근 수정된 문서 목록입니다.",
        "",
    ]
    for p in pages:
        display_date = p["date"]
        if display_date == "1970-01-01":
            display_date = "—"
        lines.append(f"- **{display_date}** — [{p['title']}](/{p['path']}.md) `{p['section']}`")

    lines.append("")
    (OUTPUT / "recent.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ _generated/recent.md ({len(pages)} pages)")


def generate_sitemap():
    """Index 페이지 생성 — 섹션별 전체 목차"""
    """Index 페이지 생성 — 섹션별 전체 목차"""
    pages = []
    for f in sorted(CONTENT.rglob("*.md")):
        if f.name in EXCLUDE or "_generated" in str(f):
            continue
        rel = os.path.relpath(f, str(CONTENT))
        content = f.read_text(encoding="utf-8")
        fm = parse_front_matter(content)
        title = fm.get("title") or get_title(content)
        section = get_section(str(f))
        pages.append({
            "title": title,
            "path": rel.replace("\\", "/").replace(".md", ""),
            "section": section,
        })

    # 섹션별 그룹화
    sections = {}
    for p in pages:
        sec = p["section"]
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(p)

    lines = [
        "---",
        "tags: [wiki, index]",
        "description: 전체 문서 목차",
        "---",
        "",
        "# Index",
        "",
        "전체 문서 목차입니다.",
        "",
    ]

    # 섹션 순서
    section_order = ["General", "ai-agent-architecture", "ai-agent", "ai-engineering", "evals-for-ai-agents", "notes"]
    for sec in section_order:
        if sec not in sections:
            continue
        display_name = {
            "General": "General",
            "ai-agent-architecture": "AI Agent Architecture",
            "ai-agent": "AI Agent",
            "ai-engineering": "AI Engineering",
            "evals-for-ai-agents": "Evals for AI Agents",
            "notes": "Notes",
        }.get(sec, sec)

        lines.append(f"## {display_name}")
        lines.append("")
        for p in sections[sec]:
            lines.append(f"- [{p['title']}](/{p['path']}.md)")
        lines.append("")

    (OUTPUT / "sitemap.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ _generated/sitemap.md ({len(pages)} pages)")


def generate_tags():
    """Tags 페이지 생성 — 태그별 문서 목록"""
    tag_map = {}
    for f in sorted(CONTENT.rglob("*.md")):
        if f.name in EXCLUDE or "_generated" in str(f):
            continue
        rel = os.path.relpath(f, str(CONTENT))
        content = f.read_text(encoding="utf-8")
        fm = parse_front_matter(content)
        title = fm.get("title") or get_title(content)
        tags = parse_tags(fm)
        for tag in tags:
            tag_clean = tag.strip().strip("[]\"'")
            if tag_clean:
                if tag_clean not in tag_map:
                    tag_map[tag_clean] = []
                tag_map[tag_clean].append({
                    "title": title,
                    "path": rel.replace("\\", "/").replace(".md", ""),
                })

    lines = [
        "---",
        "tags: [wiki, tags]",
        "description: 태그별 문서 모음",
        "---",
        "",
        "# Tags",
        "",
        "태그별로 문서를 모아볼 수 있습니다.",
        "",
    ]

    for tag in sorted(tag_map.keys()):
        pages = tag_map[tag]
        lines.append(f"## {tag}")
        lines.append("")
        for p in pages:
            lines.append(f"- [{p['title']}](/{p['path']}.md)")
        lines.append("")

    (OUTPUT / "tags.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ _generated/tags.md ({len(tag_map)} tags)")


def main():
    print("📄 Generating pages...")
    generate_recent()
    generate_sitemap()
    generate_tags()
    print("✅ Done!")


if __name__ == "__main__":
    main()
