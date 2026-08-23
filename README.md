# Agente Spotify

Agente en Python que usa OpenAI Agents SDK para buscar canciones y crear playlists en Spotify.

## Configuracion

1. Instala dependencias:

```bash
uv sync
```

2. Crea una app en el dashboard de Spotify Developer y configura este redirect URI:

```text
http://127.0.0.1:8888/callback
```

3. Copia `.env.example` a `.env` y rellena tus credenciales:

```bash
cp .env.example .env
```

Variables necesarias:

```text
OPENAI_API_KEY
SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI
```

## Uso

Con el entorno activo:

```bash
source .venv/bin/activate
spotify-agent "Crea una playlist de 20 canciones para entrenar, con pop latino y electronica"
```

Tambien puedes ejecutarlo como modulo:

```bash
python -m spotify_playlist_agent.cli "Crea una playlist tranquila para leer por la noche"
```

La primera vez que el agente use Spotify, el navegador pedira que autorices la app.

## Interfaz Streamlit

Puedes abrir un frontal web local con:

```bash
spotify-agent-ui
```

Tambien puedes lanzarlo directamente con Streamlit:

```bash
streamlit run src/spotify_playlist_agent/ui.py
```

## Notas

- `OPENAI_MODEL` se puede cambiar en `.env`; por defecto usa `gpt-5.5`.
- `SPOTIFY_PLAYLIST_PUBLIC=false` crea playlists privadas por defecto.
- El agente usa herramientas Python locales para buscar canciones y crear la playlist.
