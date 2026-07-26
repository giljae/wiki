---
tags: [ai-engineer, learning-path]
description: AI 엔지니어 학습 로드맵
---

# AI 엔지니어를 위한 학습 경로
## LLM 기초
* LLM은 어떻게 동작하며, 무엇을 할 수 있고 무엇을 할 수 없는가? LLM의 특징과 한계는 무엇인가?
* OpenAI/Anthropic API - LLM 호출 및 응답 수신
* 구조화된 출력 - 일관성 있고 형식화된 답변 얻기
* 프롬프트 엔지니어링 - 다양한 작업에 효과적인 프롬프트 작성하기

## RAG 및 검색
* RAG - 자체 데이터를 사용하여 LLM을 강화
* 텍스트 검색 및 벡터 검색
* 문서 유형별 Chunking 전략
* PDF 파일, 유투브 자막, 웹페이지 등 다양한 데이터 소스 처리

## AI 에이전트
* 함수 호출 및 도구 사용 - 작업을 수행할 수 있는 LLM
* 에이전트의 도구 호출 루프 - 에이전트가 추론하고 행동하는 방식
* 에이전트 프레임워크 - PydanticAUI, OpenAI Agent SDK, LangChain, Google ADK 등
* 모델 컨텍스트 프로토콜(MCP) - 다른 에이전트를 위한 도구 생성
* 다중 에이전트 시스템 - 라우팅, 파이프라인, 조정

## 테스트
* 에이전트 테스트 작성 - 도구 호출 테스트, 출력 품질 테스트
* LLM을 심사위원으로 활용하기 - 한 LLM이 다른 LLM을 평가하는데 활용

## 모니터링 및 관찰 가능성
* 로깅 및 추적 에이전트 실행 - OpenTelemetry, Logfire, Jaeger 등
* 비용 모니터링 및 사용량 추적
* 사용자 피드백 추적
* Grafana와 같은 모니터링 대시보드 구축

## 평가
* 오프라인 평가 - 평가 데이터 생성, 에이전트 검증
* 검색 품질 평가
* 평가를 위한 합성 데이터 생성
* 평가 결과를 기반으로 한 즉각적인 최적화

## 생산
* 노트북을 실제 프로젝트로 전환하기
* 배포 - 프로토타입 제작을 위한 도구
* AWS, GCP, Azure와 같은 프로덕션용 클라우드 플랫폼
* 안전장치 - 에이전트를 위한 안전 제약 조건
* 대규모 데이터셋을 위한 병렬 처리

## 기타 기술
### 파이썬과 소프트웨어 엔지니어링
* Python은 필수
* 테스팅, CI/CD, 코드 품질 - 모든 엔지니어에게 요구되는 사항
* Git 워크플로우 및 코드 검토

### 웹 개발
* FastAPI - AI 개발에 가장 많이 쓰이는 파이썬 웹 프레임워크
* React, Next.js - 풀스택 AI 제품 개발
* REST API, GraphQL, 마이크로서비스

### 클라우드 및 인프라
* AWS, Azure, GCP - 최소 하나 이상의 클라우드 플랫폼
* Docker와 Kubernetes - 컨테이너화 및 오케스트레이션
* Terraform - 코드로 관리하는 인프라

### 데이터베이스
* PostgreSQL - 기본 데이터베이스
* 벡터 데이터베이스 - Pinecone, Weaviate, Qdrant, pgvector
* Redis - 캐싱 및 세션 관리

### 머신러닝 기초
* PyTorch 기초 - AI 우선 직무의 22.0%
* 임베딩 - 벡터 표현 이해하기
* 미세 조정 - API 기반 모델만으로는 충분하지 않을 때
* 모델 평가 - 기존 머신러닝 지표

### 데이터 엔지니어링
* 데이터 파이프라인 - Airflow, Spark, Kafka
* ETL 및 데이터 처리
* 데이터브릭스, 스노우플레이크

### 추가 언어
* 타입스크립트 - AI 엔지니어링 분야에서 두 번째로 인기 있는 언어
* Java, Go - 백엔드 개발 비중이 높은 직무에 적합
* SQL - 데이터 접근 및 분석을 위한 도구

## 일반적인 AI 엔지니어링 스택
* 애플리케이션 - React, Next.js, FastAPI
* AI 오케스트레이션 - LangChain, LangGraph, PydanticAI
* LLM API - OpenAI, Anthropic, Groq, Local Model
* 벡터 데이터베이스 - PineCone, Weaviate, Qdrant, pgventor
* 인프라 - Docker, Kubernetes, AWS/GCP/Azure
* 모니터링 - Logfire, Grafana, OpenTelemetry
* 평가 - LLM 심사위원

## 우선 순위에 따른 기술
### 필수
* 파이썬
* 신속한 엔지니어링
* RAG 패턴
* AWS, Azure, GCP 중 하나 이상의 클라우드 플랫폼
* Docker

  ## 높은 가치
  * LangChain, PydanticAI
  * Typescript
  * FastAPI
  * Kubernetes
  * CI/CD
  * PyTorch
 
  ## 차별화 요소
  * 에이전트 프레임워크 - LangGraph, CrewAI
  * 파인 튜닝
  * 평가 프레임워크
  * 벡터 데이터베이스
  * 다중 에이전트 패턴
 
