---
tags: [guide, wiki]
description: Jupyter Book 편집과 탐색 가이드
---

# 시작 가이드

## 페이지 작성

위키 페이지는 `content/` 폴더 아래에 `.md` 파일로 작성합니다.

```markdown
---
tags: [ruby, devops]
description: 짧은 페이지 설명 (선택)
---

# 페이지 제목

내용을 여기에 작성합니다.

[다른-페이지](other-page.md)로 링크할 수 있습니다.
[content/notes/about](notes/about.md)처럼 하위 폴더 페이지도 링크할 수 있습니다.
```

## Front matter

| 항목 | 설명 |
|------|------|
| `tags` | 문자열 배열. 예: `[guide, wiki]` |
| `description` | 검색·미리보기용 짧은 설명 (선택) |
| `title` | 페이지 제목 덮어쓰기 (선택) |

## URL 경로

| 경로 | 설명 |
|------|------|
| `/` | 홈 |
| `/content/getting-started/` | 이 페이지 |
| `/content/notes/about/` | 하위 폴더 문서 |

## MyST 문법

| 문법 | 설명 |
|------|------|
| `[Page](Page.md)` | 다른 페이지로 링크 |
| `[Page](Page.md#섹션)` | 특정 섹션으로 링크 |
| ` ```mermaid ` | Mermaid 다이어그램 |
| `$E=mc^2$` | 인라인 수식 (KaTeX) |
| `$$...$$` | 블록 수식 |
| `:::{note}` | 참고 박스 |
| `:::{warning}` | 경고 박스 |
| `:::{important}` | 중요 박스 |
| `:::{tip}` | 팁 박스 |

자세한 내용은 [Plugins](plugins.md) 페이지를 참고하세요.

## 사이트 기능

| 기능 | 설명 |
|------|------|
| **검색** — 상단 검색창에서 전체 페이지 검색 |
| **다크 모드** — 상단 🌙/☀️ 버튼으로 전환 |
| **목차 자동 생성** — 페이지 우측에 섹션별 목차 |
| **코드 하이라이트** — 구문 강조 |
| **수식 (KaTeX)** — LaTeX 문법 지원 |
| **Mermaid** — 다이어그램 코드 블록 |
| **알림 박스** — note, warning, important, tip |
| **페이지 탐색** — 이전/다음 페이지 링크 |

## 편집하기

### 방법 1: 로컬에서 편집 (권장)

```bash
# 의존성 설치
pip install -r requirements.txt

# 라이브 리로드 서버 시작
jupyter-book start

# 또는 정적 빌드
jupyter-book build --html
```

브라우저에서 http://localhost:3000 을 열어 결과를 확인합니다.

### 방법 2: GitHub 웹 에디터

GitHub에서 각 `.md` 파일을 직접 수정하고 커밋하면 GitHub Actions가 자동 배포합니다.

### 방법 3: VS Code / Cursor

에디터에서 `.md` 파일을 수정하고 Git에 push합니다.

## 폴더 정리 팁

```
content/
├── home.md                    # 메인 페이지
├── getting-started.md          # 시작 가이드
├── notes/
│   ├── intro.md                # notes 섹션 소개
│   └── about.md                # about 페이지
├── ai-agent-architecture/
│   ├── intro.md                # 섹션 소개
│   └── i-model-as-component.md
└── ...
```

- 섹션별로 폴더를 만들고, 섹션 소개는 `intro.md`로 작성합니다.
- `tags` front matter로 주제별로 묶어 둘 수 있습니다.

## 배포

`main` 브랜치에 push하면 `.github/workflows/deploy.yml`이 자동으로 Jupyter Book을 빌드하고 GitHub Pages에 배포합니다.

## 로컬에서 미리보기

```bash
# 의존성 설치
pip install -r requirements.txt

# 빌드
jupyter-book build --html

# 브라우저로 _build/html/index.html 열기
open _build/html/index.html
```
