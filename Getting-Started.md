# 시작 가이드

## 페이지 작성

위키 페이지는 저장소 루트(또는 하위 폴더)에 `.md` 파일로 작성합니다.

```markdown
# 페이지 제목

내용을 여기에 작성합니다.

[[다른-페이지]]로 링크할 수 있습니다.
[[notes/About]]처럼 하위 폴더 페이지도 링크할 수 있습니다.
```

## URL 경로

| 파일 | URL |
|------|-----|
| `Home.md` | `/wiki/` |
| `Getting-Started.md` | `/wiki/Getting-Started/` |
| `notes/About.md` | `/wiki/notes/About/` |

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

## 로컬에서 편집하기

### 방법 1: Gollum 웹 UI (Docker)

```bash
docker compose up
```

브라우저에서 http://localhost:4567 을 열어 위키를 편집합니다.

### 방법 2: 파일 직접 편집

Markdown 파일을 직접 수정한 뒤 Git에 커밋하면 GitHub Actions가 자동으로 사이트를 배포합니다.
