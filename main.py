"""
Strands Skill System - Demo

Claude Code 스타일의 스킬 시스템을 Strands Agent SDK로 구현한 데모.

사용법:
    cd /home/ubuntu/projects/strands-skill-system
    uv run python main.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.skill_tool import skill_tool
from src.utils.skills.skill_utils import initialize_skills
from src.utils.strands_sdk_utils import strands_utils

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""

    print("=" * 60)
    print("Strands Skill System Demo")
    print("=" * 60)

    # 1. 스킬 시스템 초기화 (디스커버리 + 로더 + 툴 설정)
    _, skill_prompt = initialize_skills(
        skill_dirs=["./skills"],
        verbose=True # If True, You can see tha available skills
    )

    # 2. 시스템 프롬프트 구성
    # 기존 에이전트의 base prompt (예시: coder, planner 등)
    base_prompt = """## Role
<role>
You are a helpful assistant specialized in data analysis and document processing.
</role>

## Instructions
<instructions>
- Analyze user requests and provide accurate, helpful responses
- When working with files, use appropriate tools and follow best practices
- Provide clear explanations and code examples when needed
</instructions>
"""

    # 스킬 프롬프트를 base prompt에 append
    system_prompt = base_prompt + skill_prompt

    print ("system_prompt")
    print (system_prompt)

    # 3. Agent 생성 (strands_utils.get_agent 사용)
    print("\n[Skill Init] Creating agent...")
    model_id = os.getenv("DEFAULT_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
    agent = strands_utils.get_agent(
        agent_name="skill_agent",
        system_prompts=system_prompt,
        model_id=model_id,
        enable_reasoning=False,
        prompt_cache_info=(True, "default"),  # 프롬프트 캐싱 활성화
        tool_cache=True,                       # 툴 캐싱 활성화
        tools=[skill_tool],
        streaming=True
    )

    # 4. 테스트 쿼리 실행
    print("\n[Test] Running test query...")
    print("-" * 60)

    test_query = "PDF 파일에서 테이블을 추출하는 Python 코드를 작성해줘. pdfplumber를 사용해서."

    print(f"Query: {test_query}\n")
    print("Response:")
    print("-" * 60)

    # 스트리밍 실행 (process_streaming_response_yield 직접 사용)
    async def run_streaming():
        async for event in strands_utils.process_streaming_response_yield(
            agent, test_query, agent_name="skill_agent"
        ):
            strands_utils.process_event_for_display(event)

    try:
        asyncio.run(run_streaming())
    except Exception as e:
        logger.error(f"Error during agent execution: {e}")
        raise

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
