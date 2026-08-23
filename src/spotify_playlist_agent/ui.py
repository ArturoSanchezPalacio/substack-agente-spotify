from __future__ import annotations

import os
import re
from html import escape
from datetime import datetime

import streamlit as st
from agents import Runner
from dotenv import load_dotenv

from spotify_playlist_agent.agent import build_agent


EXAMPLES = [
    "Crea una playlist de 20 canciones para entrenar con pop latino y electronica.",
    "Crea una playlist tranquila para leer por la noche, sin canciones demasiado tristes.",
    "Quiero una playlist de indie rock de los 2000 para conducir, unas 25 canciones.",
]

APP_CSS = """
<style>
:root {
    --ink: #171421;
    --muted: #625c73;
    --paper: #fffdf9;
    --panel: #ffffff;
    --line: #ded6eb;
    --pink: #d8177f;
    --orange: #e96b1d;
    --yellow: #d2a900;
    --green: #0c8f62;
    --blue: #147cc2;
    --violet: #7252d4;
}

.stApp {
    color: var(--ink);
    background:
        radial-gradient(circle at 12% 6%, rgba(216, 23, 127, 0.12), transparent 28%),
        radial-gradient(circle at 84% 12%, rgba(20, 124, 194, 0.13), transparent 30%),
        linear-gradient(180deg, #fffaf7 0%, #faf7ff 48%, #ffffff 100%);
}

.block-container {
    max-width: 1040px;
    padding-top: 2.35rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e7dfef;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--ink);
}

.app-shell {
    border: 1px solid #eadff2;
    border-radius: 22px;
    padding: 0;
    background: var(--panel);
    box-shadow: 0 20px 60px rgba(44, 34, 69, 0.12);
    overflow: hidden;
}

.app-inner {
    position: relative;
    border-radius: 22px;
    padding: 2.5rem;
    background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(250, 245, 255, 0.94));
}

.app-inner::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 10px;
    background: linear-gradient(90deg, var(--pink), var(--orange), var(--yellow), var(--green), var(--blue), var(--violet));
}

.hero-title {
    margin: 0.7rem 0 0.55rem;
    font-size: clamp(2.15rem, 5vw, 4.15rem);
    line-height: 1.02;
    font-weight: 800;
    letter-spacing: 0;
}

.hero-copy {
    max-width: 680px;
    color: var(--muted);
    font-size: 1.08rem;
    line-height: 1.65;
    margin-bottom: 0.5rem;
}

.section-label {
    color: #4c415f;
    font-size: 0.84rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin: 1.7rem 0 0.55rem;
    text-transform: uppercase;
}

.result-card {
    border: 1px solid #e4dbea;
    border-radius: 16px;
    padding: 1.3rem;
    color: var(--ink);
    background: #ffffff;
    box-shadow: 0 12px 34px rgba(44, 34, 69, 0.08);
}

.history-card {
    border: 1px solid #e4dbea;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    color: var(--ink);
    background: #ffffff;
}

.history-time {
    color: #6c607a;
    font-size: 0.8rem;
    margin-bottom: 0.35rem;
}

.stTextArea label,
.stTextInput label,
.stToggle label {
    color: var(--ink) !important;
}

.stTextArea textarea {
    min-height: 176px;
    border: 2px solid #d9cfe4;
    border-radius: 16px;
    color: #171421 !important;
    caret-color: #171421;
    background: #ffffff !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9), 0 10px 30px rgba(44, 34, 69, 0.08);
}

.stTextArea textarea::placeholder {
    color: #786f86 !important;
}

.stTextArea textarea:focus {
    border-color: var(--pink);
    box-shadow: 0 0 0 3px rgba(216, 23, 127, 0.18), 0 10px 30px rgba(44, 34, 69, 0.08);
}

.stButton > button,
.stLinkButton > a {
    border-radius: 999px;
    border: 1px solid #d9cfe4;
    font-weight: 750;
    color: var(--ink);
    background: #ffffff;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    border: 0;
    color: #ffffff;
    background: linear-gradient(90deg, var(--pink), var(--orange), var(--green), var(--blue), var(--violet));
    box-shadow: 0 12px 28px rgba(216, 23, 127, 0.22);
}

.stLinkButton > a {
    color: #ffffff;
    background: linear-gradient(90deg, var(--green), var(--blue), var(--violet));
}

.stStatus {
    border-radius: 14px;
}

.stAlert {
    color: var(--ink);
}

@media (max-width: 760px) {
    .block-container {
        padding-top: 1.4rem;
    }

    .app-inner {
        padding: 1.25rem;
    }
}
</style>
"""


def _missing_env_vars() -> list[str]:
    required = [
        "OPENAI_API_KEY",
        "SPOTIPY_CLIENT_ID",
        "SPOTIPY_CLIENT_SECRET",
        "SPOTIPY_REDIRECT_URI",
    ]
    return [name for name in required if not os.getenv(name)]


def _spotify_links(markdown_text: str) -> list[str]:
    return sorted(set(re.findall(r"https://open\.spotify\.com/[^\s)]+", markdown_text)))


def _run_agent(prompt: str, playlist_public: bool) -> str:
    os.environ["SPOTIFY_PLAYLIST_PUBLIC"] = "true" if playlist_public else "false"
    agent = build_agent()
    result = Runner.run_sync(agent, prompt)
    return result.final_output


def _render_history() -> None:
    if not st.session_state.history:
        return

    st.markdown('<div class="section-label">Historial</div>', unsafe_allow_html=True)
    for item in reversed(st.session_state.history):
        safe_prompt = escape(item["prompt"])
        st.markdown(
            f"""
            <div class="history-card">
                <div class="history-time">{item["created_at"]}</div>
                <strong>Peticion</strong>
                <p>{safe_prompt}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(item["response"])


def main() -> None:
    load_dotenv()

    st.set_page_config(
        page_title="Agente Spotify",
        layout="centered",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    st.markdown(
        """
        <div class="app-shell">
            <div class="app-inner">
                <h1 class="hero-title">Agente Spotify</h1>
                <p class="hero-copy">
                    Cuéntame el mood, la ocasion o la persona para quien va la playlist.
                    El agente busca canciones reales, crea una seleccion con criterio y la guarda en Spotify.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    missing = _missing_env_vars()
    if missing:
        st.warning(
            "Faltan variables en `.env`: "
            + ", ".join(f"`{name}`" for name in missing)
            + "."
        )

    with st.sidebar:
        st.header("Ajustes")
        playlist_public = st.toggle(
            "Playlist publica",
            value=os.getenv("SPOTIFY_PLAYLIST_PUBLIC", "false").lower() == "true",
        )
        st.text_input("Modelo OpenAI", value=os.getenv("OPENAI_MODEL", "gpt-5.5"), disabled=True)

        st.divider()
        st.caption("Prompts rapidos")
        for example in EXAMPLES:
            if st.button(example, use_container_width=True):
                st.session_state.prompt = example

    st.markdown('<div class="section-label">Tu peticion</div>', unsafe_allow_html=True)
    prompt = st.text_area(
        "Peticion musical",
        key="prompt",
        height=150,
        placeholder="Ej: Crea una playlist de 20 canciones para una cena con amigos...",
        label_visibility="collapsed",
    )

    submitted = st.button(
        "Crear playlist",
        type="primary",
        disabled=not prompt.strip() or bool(missing),
        use_container_width=True,
    )

    if submitted:
        with st.status("El agente esta buscando canciones y creando la playlist...", expanded=True) as status:
            st.write("Consultando OpenAI y Spotify.")
            try:
                response = _run_agent(prompt.strip(), playlist_public)
            except Exception as error:
                status.update(label="No se pudo completar la peticion", state="error")
                st.error(str(error))
                return

            st.session_state.history.append(
                {
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "prompt": prompt.strip(),
                    "response": response,
                }
            )
            status.update(label="Playlist lista", state="complete")

        st.markdown('<div class="section-label">Resultado</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(response)
            st.markdown("</div>", unsafe_allow_html=True)

        links = _spotify_links(response)
        for link in links:
            st.link_button("Abrir en Spotify", link, use_container_width=True)

    _render_history()


if __name__ == "__main__":
    main()
