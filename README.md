# Giljae's Digital Garden

Jupyter Book 기반 디지털 가든입니다. Markdown으로 페이지를 작성하고, GitHub Pages에 자동 배포됩니다.

**사이트 URL:** https://wiki.giljae.com

## 구조

```
wiki/
├── myst.yml              # Jupyter Book 설정
├── intro.md              # 메인 페이지
├── content/              # 문서들
│   ├── getting-started.md
│   ├── plugins.md
│   ├── ai-agent-architecture/
│   ├── ai-engineering/
│   ├── evals-for-ai-agents/
│   └── notes/
├── assets/               # 스타일시트, 파비콘 등
├── _build/               # 빌드 결과물 (gitignore)
├── .github/workflows/deploy.yml
└── requirements.txt      # Python 의존성
```

## URL 경로

Jupyter Book은 파일 구조를 따라 URL이 생성됩니다.

| 파일 | URL |
|------|-----|
| `intro.md` | `/` |
| `content/getting-started.md` | `/content/getting-started/` |
| `content/notes/about.md` | `/content/notes/about/` |

## 로컬에서 미리보기

### 사전 준비

```bash
pip install -r requirements.txt
```

### 빌드 & 서버 시작

```bash
jupyter-book start
# 또는 정적 HTML 빌드
jupyter-book build --html
```

`http://localhost:3000`에서 확인합니다.

## 배포

`main` 브랜치에 push하면 `.github/workflows/deploy.yml`이 자동 실행됩니다.

## 기능

- **MyST Markdown** — CommonMark + 확장 문법
- **수식 (KaTeX)** — `$E=mc^2$` (인라인), `$$...$$` (블록)
- **다이어그램** — ` ```mermaid` 코드 블록
- **알림 박스** — `:::{note}`, `:::{warning}`, `:::{important}`
- **코드 하이라이트**
- **목차 자동 생성** — 페이지 우측 섹션별 목차
- **검색** — 전체 페이지 검색
- **다크 모드** — 🌙/☀️ 버튼

자세한 사용법은 [Getting Started](content/getting-started.md) 페이지를 참고하세요.
