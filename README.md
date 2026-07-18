# Giljae's Digital Garden

Gollum 기반 Git 위키입니다. Markdown으로 페이지를 작성하고, GitHub Pages에 자동 배포됩니다.

**사이트 URL:** https://giljae.github.io/wiki/

## 구조

```
wiki/
├── Home.md              # 메인 페이지
├── _Sidebar.md          # 사이드바 (모든 페이지에 표시)
├── _Layout.html         # 정적 사이트 HTML 레이아웃
├── Getting-Started.md   # 예시 페이지
├── assets/style.css     # 스타일시트
├── scripts/build_site.rb # GitHub Pages용 정적 사이트 빌드
└── docker-compose.yml   # 로컬 Gollum 편집기
```

## 페이지 작성

1. `.md` 파일을 저장소 루트에 추가합니다
2. `[[다른-페이지]]` 형식으로 링크합니다
3. `main` 브랜치에 push하면 GitHub Actions가 자동으로 사이트를 배포합니다

`_`로 시작하는 파일(`_Sidebar.md` 등)은 서브페이지로, 위키 페이지 목록에 표시되지 않습니다.

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
BASE_PATH=/wiki bundle exec ruby scripts/build_site.rb

# 미리보기
cd _site && python3 -m http.server 8000
```

http://localhost:8000/wiki/ 에서 확인합니다.

## GitHub Pages 설정

> **최초 1회 필수:** 아래 설정을 하지 않으면 배포 워크플로가 실패합니다.

1. https://github.com/giljae/wiki/settings/pages
2. **Build and deployment** → **Source**를 **GitHub Actions**로 변경
3. 저장 후 Actions 탭에서 실패한 워크플로를 **Re-run** 하거나, 빈 커밋을 push합니다

`main` 브랜치에 push하면 `.github/workflows/deploy.yml`이 자동 실행됩니다.

## 커스터마이징

| 파일 | 역할 |
|------|------|
| `_Layout.html` | HTML 레이아웃 (ERB 템플릿) |
| `assets/style.css` | 기본 스타일 |
| `custom.css` | 추가 스타일 (선택) |
| `_Sidebar.md` | 사이드바 내용 |

## Gollum vs GitHub Pages

- **Gollum**은 Git 저장소를 위키로 편집하는 도구입니다 (로컬 Docker로 실행)
- **GitHub Pages**는 정적 호스팅이므로, `scripts/build_site.rb`가 Gollum 형식의 Markdown을 HTML로 변환합니다
- 두 방식 모두 같은 `.md` 파일을 사용합니다
