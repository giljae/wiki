---
tags: [wiki, features]
description: Mermaid, KaTeX, 알림 박스 등 Jupyter Book 기능 안내
---

# 플러그인 & 기능

이 Jupyter Book에서 사용할 수 있는 기능들입니다.

## Mermaid 다이어그램

```mermaid
graph LR
  A[아이디어] --> B[메모]
  B --> C[위키 페이지]
  C --> D[Digital Garden]
```

## 수학 (KaTeX)

인라인: $E = mc^2$

블록:

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$

## 알림 박스 (Admonitions)

Jupyter Book에서는 다양한 알림 박스를 지원합니다.

:::{note}
이것은 참고 사항입니다.
:::

:::{warning}
주의가 필요한 내용입니다.
:::

:::{important}
중요한 정보입니다.
:::

:::{tip}
유용한 팁입니다.
:::

## 목차 (Table of Contents)

Jupyter Book은 페이지 우측에 자동으로 섹션 목차를 생성합니다. `_toc.yml` 파일로 전체 사이트 구조를 정의합니다.

## 검색

상단 검색창에서 모든 페이지를 검색할 수 있습니다.

## 다크 모드

상단 오른쪽의 🌙/☀️ 버튼으로 테마를 전환합니다. 설정은 브라우저에 저장됩니다.

## 코드 블록

```ruby
def hello
  puts "Hello, Garden!"
end
```

## 페이지 링크

| 문법 | 결과 |
|------|------|
| `[Page](Page.md)` | 같은 디렉토리의 다른 페이지로 링크 |
| `[Page](../section/Page.md)` | 다른 섹션 페이지로 링크 |
| `[Page](Page.md#섹션)` | 특정 섹션으로 링크 |
