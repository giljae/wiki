---
tags: [ai-engineer, skills]
description: AI 엔지니어에게 필요한 기술 분석
---

# AI 엔지니어 기술 분석
* GenAI 기술 외에도 다른 기술이 필요. Fullstack 개발자 역할
* AI 엔지니어링 직무는 ML 지식을 요구함

## AI 엔지니어링 직종
다음과 같은 범주로 분류됨
* AI-first
* AI-support

### AI-first
AI 시스템 개발에 직접 참여.

만드는 것:
* RAG(Retrieval-Augmented Generation) 시스템
* AI 에이전트 및 에이전트 기반 워크플로우
* 특정 영역에 맞춘 정밀 조정된 LLM
* 모델 서빙 및 추론 파이프라인
* 신속한 엔지니어링 및 최적화

담당 업무:
* 지식 검색을 위한 RAG 시스템 구축
* 자동화를 위한 에이전트 워크플로우 구현
* 특정 도메인에 맞춰 모델 미세 조정(fine-tuning)
* AI 모델을 실제 운영 환경에 배포
* 프롬프트 및 모델 성능 최적화

### AI-support
AI 분야를 직접적으로 연구하는 것이 아니라, AI와 밀접한 관련이 있는 분야에서 업무 수행.
이 역할은 AI-first 엔지니어들이 사용하는 플랫폼, 인프라 및 도구를 구축함으로써 AI 작업을 가능하게 함.

만드는 것:
* AI 플랙폼 및 내부 도구
* GPU 클러스터 및 추론 인프라
* 학습/미세 조정을 위한 데이터 파이프라인
* AI 제품용 프론트엔드
* 배포 및 모니터링 시스템

담당 업무:
* RAG 시스템용 플랫폼 구축
* 미세 조정을 위한 파이프라인 데이터
* 배포 인프라 구축
* 프롬프트 관리 UI 구축
* AI 실험을 위한 내부 도구 개발

### 구별하는 방법
이 직무가 AI 시스템내에서 일하는 것인지, 아니면 AI 시스템과 가까운 곳에서 일하는 것인지가 핵심이다.

AI-first:
* RAG 시스템을 구축
* 모델을 미세 조정
* 에이전트 워크플로우를 구현
* 프롬프트를 최적화
* AI 기능 배포

AI-support:
* 타인을 위한 플랫폼을 구축
* GPU 인프라 관리
* 데이터 파이프라인 구축
* 배포 도구를 생성
* AI 제품용 사용자 인터페이스(UI) 개발

## GenAI 생태계
프레임워크 인기도:
* LangChain
* LangGraph
* LiamaIndex
* CrewAI
* AutoGen

## GenAI외에 AI 엔지니어에게 필요한 것
AI 기술 그 이상의 역량이 필요함.

AI 엔지니어 직무에 필요한 기술 조합:
* GenAI + Ops(Docker, K8S, CI/CD)
* GenAI + ML Skill
* GenAI + Web 기술
* GenAI + 기타 기술

AI 직무는 생산/운영 관련 기술을 알고 있어야 함. AI 엔지니어는 AI를 전문으로 하는 Fullstack 엔지니어임. 대부분 클라우드 배포, 컨테이너화, CI/CD, 웹 개발(React, FastAPI 등) 경험을 필요로 함.

## 파인 튜닝
AI 업무에서는 파인 튜닝도 포함됨

* 전문 지식 - 의료, 법률, 금융, 산업별 응용 분야
* 회사 데이터 - 내부 문서, 기밀 데이터
* 성능 - 더 작고 빠른 모델, 지연 시간 최적화
* 언어 - 다국어 지원
* 개인정보 보호 - 온프레미스, 클라우드, 보안 환경

대부분 AI 엔지니어는 파인 튜닝을 하지 않음. 이유는 파인 튜닝 역할이 드뭄. 대부분의 AI 엔지니어에게 파인 튜닝은 선택 사항임.
RAG와 에이전트에 집중을 해야함. 그 다음 필요 시 파인 튜닝 고려

## 평가
모델 평가, 모니터링, 관찰, 테스트, 품질 관리 등 평가 관련 기술이 필요함.
RAG와 에이전트는 이제 기본이 되고 있고, LLM을 평가자로 활용하거나, 골든 데이터 셋을 사용하거나, 환각 탐지 및 드리프트 모니터링을 통해 AI 시스템이 잘 작동하는지 측정할 수 있는 능력이 핵심.

## AI 엔지니어를 위한 학습 경로
* 기초 - 파이썬, API, 기본 웹 개발
* LLM 기초 - 프롬프트 엔지니어링, LLM
* RAG - 벡터 데이터베이스, 임베딩, 검색 패턴
* 프레임워크 - LangChain or LiamaIndex, CrewAI
* 에이전트 - LangGraph, 에이전트 오케스트레이션
* 운영 환경 - Docker, Kubernetes, CI/CD, 모니터링

AI 엔지니어링 스택:
* 애플리케이션 레이어 - React, Next.js, FastAPI
* AI 오케스트레이션 레이어 - LangChain, LangGraph, LIamaIndex
* LLM 레이어 - OpenAI, Anthropic, Local Model
* 벡터 데이터베이스 레이어 - pgvector, Pinecone, Weaviate
* 인프라 레이어 - Docker, Kubernetes, AWS/GCP/Azure
