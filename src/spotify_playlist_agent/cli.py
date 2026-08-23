from __future__ import annotations

import argparse

from dotenv import load_dotenv
from agents import Runner

from spotify_playlist_agent.agent import build_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agente de OpenAI para buscar canciones y crear playlists en Spotify."
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help='Petición para el agente, por ejemplo: "Crea una playlist indie para cocinar".',
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    user_prompt = " ".join(args.prompt).strip()
    if not user_prompt:
        user_prompt = input("Que playlist quieres crear? ").strip()

    agent = build_agent()
    result = Runner.run_sync(agent, user_prompt)
    print(result.final_output)


if __name__ == "__main__":
    main()
