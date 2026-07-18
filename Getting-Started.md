---
tags: [guide, wiki]
description: 위키 편집과 탐색 가이드
---

# 시작 가이드

## 페이지 작성

위키 페이지는 저장소 루트(또는 하위 폴더)에 `.md` 파일로 작성합니다.

```markdown
---
tags: [ruby, devops]
description: 짧은 페이지 설명 (선택)
---

# 페이지 제목

내용을 여기에 작성합니다.

[[다른-페이지]]로 링크할 수 있습니다.
[[notes/About]]처럼 하위 폴더 페이지도 링크할 수 있습니다.
```

## 태그

페이지 맨 위에 YAML front matter로 `tags`를 추가합니다.

| 항목 | 설명 |
|------|------|
| `tags` | 문자열 배열. 예: `[guide, wiki]` |
| `description` | 검색·미리보기용 짧은 설명 (선택) |

- 문서 본문 위에 태그 pill이 표시됩니다
- [모든 태그](/wiki/tags/) 페이지에서 전체 태그 목록을 볼 수 있습니다
- 각 태그를 클릭하면 해당 태그 문서만 모아 봅니다 (`/wiki/tags/guide/`)

## URL 경로

| 파일 | URL |
|------|-----|
| `Home.md` | `/wiki/` |
| `Getting-Started.md` | `/wiki/Getting-Started/` |
| `notes/About.md` | `/wiki/notes/About/` |
| (태그 목록) | `/wiki/tags/` |
| (태그별) | `/wiki/tags/guide/` |

페이지 상단 **breadcrumb**(Home / notes / About)에서 각 단계를 클릭해 이동할 수 있습니다.

## 편집하기

- **읽기 | 편집 | 역사** 탭 — Wikipedia 스타일
- **편집** → GitHub에서 해당 `.md` 파일 수정
- **역사** → 커밋 기록 확인
- 로컬: `docker compose up` (Gollum 웹 UI)

## 폴더 페이지

하위 폴더에 `Home.md`를 두면 폴더 목록 페이지가 됩니다 (`notes/Home.md` → `/wiki/notes/Home/`).

사이드바에서 폴더 이름을 클릭하면 해당 `Home.md`로 이동합니다. 폴더에 `Home.md`가 없으면 링크 없이 표시됩니다.

## Gollum 문법

| 문법 | 설명 |
|------|------|
| `[[Page]]` | 다른 페이지로 링크 |
| `[[Page\|표시이름]]` | 링크 텍스트 지정 |
| `[[_TOC_]]` | 페이지 목차 자동 생성 |
| ```` ```ruby ```` | 코드 블록 (언어 하이라이트) |
| ```` ```mermaid ```` | Mermaid 다이어그램 |
| `$E=mc^2$` | 인라인 수식 (KaTeX) |
| `<<Note("내용")>>` | 참고 박스 |
| `<<Warn("내용")>>` | 경고 박스 |

자세한 내용은 [[Plugins]] 페이지를 참고하세요.

## 사이트 기능

| 기능 | 설명 |
|------|------|
| **홈 대시보드** | 최근 편집, 태그, 바로가기, 통계 |
| **사이드바 문서 목록** | 폴더 구조를 자동으로 반영합니다. `▸` 버튼으로 하위 문서를 접거나 펼칠 수 있습니다. |
| **최근 편집** | Git 커밋 날짜 기준으로 최근 수정된 페이지를 사이드바에 표시합니다. |
| **역링크** | `[[페이지]]`로 이 문서를 링크한 다른 페이지가 본문 아래에 표시됩니다. |
| **검색** | 헤더 검색창에서 전체 페이지를 검색합니다. |

## 다른 사람들은 어떻게 쓰나요?

Git 기반 위키는 크게 세 가지 방식으로 쓰입니다.

### 1. Obsidian + Git (개인 지식 관리)

[Obsidian](https://obsidian.md)으로 Markdown을 쓰고, 이 저장소를 vault로 열어 Git에 push합니다. `[[링크]]`, 그래프 뷰, 백링크가 Obsidian에서 잘 맞습니다. 이 사이트는 **읽기용 웹 출판** 역할을 합니다.

### 2. VS Code / Cursor로 직접 편집

에디터에서 `.md` 파일을 수정하고 커밋·push하면 GitHub Actions가 자동 배포합니다. Wikipedia 스타일 **편집** 탭으로 GitHub 웹 에디터에서도 바로 수정할 수 있습니다.

### 3. Gollum Docker (브라우저 편집)

`docker compose up`으로 로컬 Gollum UI를 띄우면 Wikipedia처럼 브라우저에서 바로 저장할 수 있습니다. 미리보기·문법 검사에 유용합니다.

### 폴더 정리 팁

```
Home.md                 # 메인 대시보드
notes/Home.md           # notes 섹션 소개
notes/주제A/개념1.md    # 깊은 폴더도 URL에 반영됨
```

- 폴더마다 `Home.md`를 두면 섹션 인덱스 페이지가 됩니다.
- `tags` front matter로 주제별로 묶어 두면 태그 페이지에서 한눈에 볼 수 있습니다.
- 하위 폴더에서 루트 `Home`으로 가려면 `[[Home]]` 대신 `[위키 메인](/wiki/)`을 사용하세요.

## 로컬에서 편집하기

### 방법 1: Gollum 웹 UI (Docker)

```bash
docker compose up
```

브라우저에서 http://localhost:4567 을 열어 위키를 편집합니다.

### 방법 2: 파일 직접 편집

Markdown 파일을 직접 수정한 뒤 Git에 커밋하면 GitHub Actions가 자동으로 사이트를 배포합니다.
