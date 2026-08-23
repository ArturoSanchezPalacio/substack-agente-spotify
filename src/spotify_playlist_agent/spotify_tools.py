from __future__ import annotations

import json
import os
from typing import Iterable

import spotipy
from agents import function_tool
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth


SPOTIFY_SCOPES = "playlist-modify-private playlist-modify-public user-read-private"


def _spotify_client() -> spotipy.Spotify:
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SPOTIFY_SCOPES,
            open_browser=True,
        )
    )


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _chunked(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _spotify_error_message(error: SpotifyException) -> str:
    reason = getattr(error, "reason", None) or str(error)
    status = getattr(error, "http_status", None)

    if status == 403:
        return (
            "Spotify ha devuelto 403 Forbidden. Revisa: "
            "1) que la app de Spotify este en Development Mode y tu usuario este en Users Management/allowlist; "
            "2) que el propietario de la app tenga Spotify Premium si la app esta en Development Mode; "
            "3) que hayas vuelto a autorizar tras pedir los scopes "
            f"`{SPOTIFY_SCOPES}`; "
            "4) que `SPOTIFY_PLAYLIST_PUBLIC=false` si quieres crear playlists privadas. "
            f"Detalle original: {reason}"
        )

    return f"Error de Spotify ({status or 'sin codigo'}): {reason}"


@function_tool
def search_spotify_tracks(query: str, limit: int = 10) -> str:
    """Search Spotify tracks.

    Args:
        query: Spotify search query. Include artist, track, genre, mood, decade, or other useful keywords.
        limit: Maximum number of tracks to return, between 1 and 20.
    """
    try:
        client = _spotify_client()
        safe_limit = max(1, min(limit, 20))
        results = client.search(q=query, type="track", limit=safe_limit, market="from_token")
    except SpotifyException as error:
        return _spotify_error_message(error)

    tracks = []
    for item in results.get("tracks", {}).get("items", []):
        tracks.append(
            {
                "name": item["name"],
                "artists": [artist["name"] for artist in item["artists"]],
                "album": item["album"]["name"],
                "uri": item["uri"],
                "popularity": item.get("popularity"),
                "explicit": item.get("explicit"),
                "duration_ms": item.get("duration_ms"),
                "preview_url": item.get("preview_url"),
            }
        )

    return json.dumps(tracks, ensure_ascii=False)


@function_tool
def create_spotify_playlist(
    name: str,
    description: str,
    track_uris: list[str],
    public: bool | None = None,
) -> str:
    """Create a Spotify playlist and add tracks to it.

    Args:
        name: Playlist name.
        description: Short playlist description.
        track_uris: Spotify track URIs to add, such as spotify:track:...
        public: Whether the playlist should be public. If omitted, SPOTIFY_PLAYLIST_PUBLIC is used.
    """
    if not track_uris:
        return "No se ha creado ninguna playlist porque no hay canciones seleccionadas."

    try:
        client = _spotify_client()
        playlist_public = _as_bool(os.getenv("SPOTIFY_PLAYLIST_PUBLIC"), default=False) if public is None else public

        playlist = client.current_user_playlist_create(
            name=name,
            public=playlist_public,
            description=description,
        )

        unique_track_uris = list(dict.fromkeys(track_uris))
        for chunk in _chunked(unique_track_uris, 100):
            client.playlist_add_items(playlist_id=playlist["id"], items=chunk)
    except SpotifyException as error:
        return _spotify_error_message(error)

    payload = {
        "name": playlist["name"],
        "url": playlist["external_urls"]["spotify"],
        "track_count": len(unique_track_uris),
        "public": playlist_public,
    }
    return json.dumps(payload, ensure_ascii=False)
