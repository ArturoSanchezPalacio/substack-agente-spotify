from __future__ import annotations

import os

from agents import Agent

from spotify_playlist_agent.spotify_tools import create_spotify_playlist, search_spotify_tracks


def build_agent() -> Agent:
    model = os.getenv("OPENAI_MODEL", "gpt-5.5")

    return Agent(
        name="Spotify Playlist Agent",
        model=model,
        instructions=(
            "Eres un curador musical experto y ayudas a crear playlists en Spotify. "
            "Habla en español por defecto. Convierte la petición del usuario en una playlist coherente: "
            "define un concepto, busca canciones reales en Spotify con search_spotify_tracks, selecciona "
            "una mezcla equilibrada y evita duplicados. Si faltan datos críticos, pregunta antes de crearla. "
            "Si el usuario pide crear la playlist, usa create_spotify_playlist con URIs reales. "
            "Después resume el criterio de selección y entrega el enlace de Spotify si la playlist fue creada."
        ),
        tools=[search_spotify_tracks, create_spotify_playlist],
    )
