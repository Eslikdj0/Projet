"""Point d'entrée : navigation et filtres partagés entre les pages."""

import streamlit as st

from data_utils import ROOT, filter_tracks, load_data
from ui import number, show_method

st.set_page_config(page_title="Atelier playlist", page_icon=":material/graphic_eq:", layout="wide")

try:
    catalogue, genres, quality = load_data()
except FileNotFoundError:
    st.error("Le fichier data/dataset.csv.gz est absent. Consultez le README pour le récupérer.")
    st.stop()

page = st.navigation(
    [
        st.Page("app_pages/profil.py", title="Profil de la sélection", icon=":material/tune:", default=True),
        st.Page("app_pages/genres.py", title="Comparer les genres", icon=":material/grid_view:"),
        st.Page("app_pages/titres.py", title="Explorer les titres", icon=":material/queue_music:"),
    ],
    position="top",
)

defaults = {
    "genres": ["pop", "hip-hop", "electronic"],
    "explicit": "Tous",
    "popularity": (0, 100),
    "energy": (0.0, 1.0),
    "danceability": (0.0, 1.0),
    "valence": (0.0, 1.0),
}


def reset_filters():
    for key, value in defaults.items():
        st.session_state[key] = value


for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.image(str(ROOT / "assets" / "spotify-logo.svg"), width=110)
    st.header("Votre sélection")
    st.caption("Choisissez les genres, puis ajustez l'ambiance musicale.")
    st.multiselect("Genres musicaux", sorted(genres["track_genre"].unique()), key="genres")
    st.caption("Une sélection vide ne renvoie aucun titre.")
    st.selectbox("Contenu explicite", ["Tous", "Sans contenu explicite", "Explicites uniquement"], key="explicit")
    st.slider("Popularité historique", 0, 100, key="popularity", help="Score du fichier, pas le score Spotify actuel.")
    with st.expander("Affiner le profil musical"):
        st.slider("Énergie", 0.0, 1.0, step=0.05, key="energy")
        st.slider("Dansabilité", 0.0, 1.0, step=0.05, key="danceability")
        st.slider("Positivité", 0.0, 1.0, step=0.05, key="valence")
    st.button("Réinitialiser les filtres", on_click=reset_filters, width="stretch")

filters = {key: st.session_state[key] for key in defaults}
selection = filter_tracks(catalogue, genres, filters)
st.sidebar.caption(f"{number(len(selection))} titres uniques disponibles")

# Les pages partagent les mêmes données filtrées et les mêmes widgets.
st.session_state["catalogue"] = catalogue
st.session_state["genre_associations"] = genres
st.session_state["selection"] = selection
page.run()
show_method(quality)
