import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent import DeepSeekMCPAgent


def get_api_key() -> str:
    # First, check environment variable
    import os

    env_key = os.getenv("DEEPSEEK_API_KEY")
    if env_key:
        return env_key.strip()

    # Second, check api_key.txt file
    key_path = Path(__file__).parent / "api_key.txt"
    if key_path.exists():
        return key_path.read_text(encoding="utf-8").strip()

    # Finally, prompt the user
    print(f"API Key file not found at {key_path}")
    key = input("Please enter your DeepSeek API Key: ").strip()
    if not key:
        print("Error: API Key is required.")
        sys.exit(1)

    key_path.write_text(key, encoding="utf-8")
    print(f"API Key saved to {key_path}")
    return key


async def main():
    load_dotenv()

    # 1. Setup Agent
    api_key = get_api_key()
    agent = DeepSeekMCPAgent(api_key=api_key)

    # 2. Setup Servers
    current_dir = Path(__file__).parent
    servers_dir = current_dir / "servers"

    # Scan for servers
    if servers_dir.exists():
        for item in servers_dir.iterdir():
            if item.is_dir():
                skill_path = item / "SKILL.md"
                server_path = item / "server.py"

                if skill_path.exists() and server_path.exists():
                    print(f"Loading server: {item.name}")
                    agent.add_server(
                        name=item.name,
                        skill_md_path=skill_path,
                        command=sys.executable,
                        args=[str(server_path)],
                    )

    # 3. Start Chat Loop
    try:
        await agent.chat_loop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
