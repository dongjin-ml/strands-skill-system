# Strands Skill System

Claude Code 스타일의 스킬 시스템을 Strands Agent SDK로 구현한 프로젝트입니다.

## 특징

- **Lazy Loading**: 시작 시 스킬 메타데이터만 로드하고, 실제 호출 시 전체 내용 로드
- **동적 Tool 생성**: 발견된 스킬 목록을 기반으로 skill_tool 자동 생성
- **캐싱 없음**: 매번 파일에서 읽어 항상 최신 내용 반영

## 설치

```bash
cd /home/ubuntu/projects/strands-skill-system
uv sync
```

## 사용법

```bash
uv run python main.py
```

## 프로젝트 구조

```
strands-skill-system/
├── main.py                     # 데모 실행 진입점
├── pyproject.toml              # 프로젝트 설정
├── src/
│   ├── __init__.py
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── discovery.py        # 스킬 디스커버리 (메타데이터 추출)
│   │   ├── loader.py           # 스킬 로더 (lazy loading)
│   │   └── skill_tool.py       # Skill Tool 정의
│   └── utils/
│       └── __init__.py
└── skills/                     # 스킬 디렉토리 (심볼릭 링크)
```

## 스킬 구조

각 스킬은 `SKILL.md` 파일을 포함한 폴더입니다:

```
my-skill/
├── SKILL.md          # 필수 - YAML frontmatter + Markdown 본문
├── scripts/          # 선택 - 실행 가능한 스크립트
├── references/       # 선택 - 참조 문서
└── assets/           # 선택 - 템플릿, 이미지 등
```

### SKILL.md 형식

```markdown
---
name: my-skill
description: 스킬에 대한 설명. 언제 이 스킬을 사용해야 하는지 포함.
license: MIT
allowed-tools:
  - Read
  - Write
---

# 스킬 제목

스킬의 상세 내용...
```

## 동작 흐름

1. **SkillDiscovery**: 지정된 디렉토리에서 `SKILL.md` 파일 스캔
2. YAML frontmatter에서 `name`, `description` 추출
3. **SkillLoader** 생성 (available_skills 전달)
4. **create_skill_tool()**: loader를 바인딩한 skill_tool 생성
5. Agent에 skill_tool 등록
6. 사용자 쿼리 → Agent가 skill_tool 호출 → SkillLoader가 전체 내용 로드 → 응답

## 라이선스

MIT
