# Giljae's Digital Garden

Gollum 기반 Git 위키입니다. Markdown으로 페이지를 작성하고, GitHub Pages에 자동 배포됩니다.

**사이트 URL:** https://wiki.giljae.com

## 구조

```
wiki/
├── Home.md              # 메인 페이지
├── _Layout.html         # 정적 사이트 HTML 레이아웃
├── Getting-Started.md   # 예시 페이지
├── assets/style.css     # 스타일시트
├── scripts/build_site.rb # GitHub Pages용 정적 사이트 빌드
└── docker-compose.yml   # 로컬 Gollum 편집기
```

## URL 경로

| 파일 | URL |
|------|-----|
| `Home.md` | `/` |
| `Getting-Started.md` | `/Getting-Started/` |
| `notes/About.md` | `/notes/About/` |

`.html` 없이 깔끔한 URL을 사용합니다. 하위 폴더 구조가 URL에 반영됩니다.

## 인프라

| 파일 | 역할 |
|------|------|
| `404.md` | 없는 페이지 안내 (`404.html`로 빌드) |
| `_Footer.md` | 사이트 하단 (모든 페이지) |
| `sitemap.xml` | 검색엔진용 (빌드 시 자동 생성) |
| `robots.txt` | 크롤러 안내 (빌드 시 자동 생성) |
| `search-index.json` | 클라이언트 검색 인덱스 |

사이드바 **문서 목록**은 빌드 시 모든 페이지를 폴더 구조대로 자동 생성됩니다.

## 로컬에서 편집하기

### Gollum 웹 UI (권장)

Docker가 설치되어 있다면:

```bash
docker compose up
```

http://localhost:4567 에서 위키를 브라우저로 편집할 수 있습니다.

### 파일 직접 편집

에디터로 `.md` 파일을 수정한 뒤 Git에 커밋합니다.

## 로컬에서 사이트 미리보기

```bash
# 의존성 설치 (최초 1회)
sudo apt install libgit2-dev pkg-config  # Debian/Ubuntu
bundle install

# 빌드 (커밋된 파일 기준으로 생성됩니다)
bundle exec ruby scripts/build_site.rb

# 미리보기
cd _site && python3 -m http.server 8000
```

http://localhost:8000/ 에서 확인합니다.

## GitHub Pages & 커스텀 도메인

**사이트:** https://wiki.giljae.com

1. https://github.com/giljae/wiki/settings/pages
2. **Build and deployment** → **Source**를 **GitHub Actions**로 변경
3. **Custom domain**에 `wiki.giljae.com` 입력 (DNS CNAME → `giljae.github.io`)

`main` 브랜치에 push하면 `.github/workflows/deploy.yml`이 자동 실행됩니다.

## 커스터마이징

| 파일 | 역할 |
|------|------|
| `_Layout.html` | HTML 레이아웃 (ERB 템플릿) |
| `assets/style.css` | 테마 (라이트/다크 모드 CSS 변수) |
| `assets/wiki.js` | 플러그인 (검색, Mermaid, KaTeX, 코드 복사) |
| `assets/rouge.css` | 코드 하이라이트 색상 |
| `custom.css` | 추가 스타일 (선택) |
| `_Footer.md` | 사이트 하단 |

## 플러그인

- **검색** — 헤더 검색창 (클라이언트 사이드)
- **Mermaid** — ` ```mermaid ` 코드 블록
- **KaTeX** — `$수식$` 또는 `$$블록$$`
- **TOC** — `[[_TOC_]]` 매크로
- **알림 박스** — `<<Note("내용")>>`, `<<Warn("내용")>>`
- **다크 모드** — 헤더 🌙/☀️ 버튼
- **코드 복사** — 코드 블록 hover 시 Copy 버튼

자세한 사용법은 [[Plugins]] 페이지를 참고하세요.

## Gollum vs GitHub Pages

- **Gollum**은 Git 저장소를 위키로 편집하는 도구입니다 (로컬 Docker로 실행)
- **GitHub Pages**는 정적 호스팅이므로, `scripts/build_site.rb`가 Gollum 형식의 Markdown을 HTML로 변환합니다
- 두 방식 모두 같은 `.md` 파일을 사용합니다
