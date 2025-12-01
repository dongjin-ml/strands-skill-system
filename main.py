"""
Strands Skill System - Demo

Claude Code 스타일의 스킬 시스템을 Strands Agent SDK로 구현한 데모.

사용법:
    cd /home/ubuntu/projects/strands-skill-system
    uv run python main.py
"""

import asyncio
import itertools
import logging
import os
import readline  # 백스페이스, 화살표 키 등 터미널 입력 지원
import sys
import threading
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.tools import skill_tool  # import module, not function
from src.tools import bash_tool    # bash command execution
from strands_tools import file_read, file_write  # file operations from strands_tools package
from src.utils.skills.skill_utils import initialize_skills
from src.utils.strands_sdk_utils import strands_utils

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Spinner:
    """애니메이션 스피너 - LLM 응답 대기 중 표시"""
    def __init__(self, message="Thinking"):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}...")
            sys.stdout.flush()
            threading.Event().wait(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")  # 클리어
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


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
- IMPORTANT: When using file_read, only read specific files you need. Never read entire directories. Use bash_tool with "ls" or "tree -L 2" to explore directory structure first.
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
        tools=[skill_tool, bash_tool, file_read, file_write],
        streaming=True
    )

    # 4. 대화형 루프
    print("\n[Ready] Agent is ready. Type 'quit' or 'exit' to end.")
    print("-" * 60)

    async def run_streaming(query):
        async for event in strands_utils.process_streaming_response_yield(
            agent, query, agent_name="skill_agent"
        ):
            strands_utils.process_event_for_display(event)

    async def chat_loop():
        while True:
            try:
                # asyncio에서 blocking input을 처리하기 위해 executor 사용
                loop = asyncio.get_event_loop()
                user_input = await loop.run_in_executor(
                    None, lambda: input("\n👤 You: ").strip()
                )

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n" + "=" * 60)
                    print("Goodbye!")
                    print("=" * 60)
                    break

                print("\n🤖 Assistant:")
                print("-" * 60)

                # 스피너 시작 (별도 스레드에서 동작)
                spinner = Spinner("Thinking")
                spinner.start()

                try:
                    first_event = True
                    async for event in strands_utils.process_streaming_response_yield(
                        agent, user_input, agent_name="skill_agent"
                    ):
                        # 첫 이벤트가 오면 스피너 중지
                        if first_event:
                            spinner.stop()
                            first_event = False
                        strands_utils.process_event_for_display(event)
                finally:
                    spinner.stop()  # 에러 발생해도 스피너 정지

            except KeyboardInterrupt:
                print("\n\nInterrupted by user.")
                break
            except Exception as e:
                logger.error(f"Error during agent execution: {e}")
                print(f"Error: {e}")

    try:
        asyncio.run(chat_loop())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
