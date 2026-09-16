"""Éléments communs aux trois pages, sans CSS personnalisé."""

import streamlit as st

from data_utils import AUDIO_LABELS

GREEN = "#1DB954"
GREY = "#A7A7A7"


def number(value, decimals=0):
    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def show_header(title, description, selection, catalogue):
    st.caption("ATELIER PLAYLIST · EXPLORATION DU CATALOGUE SPOTIFY")
    st.title(title)
    st.write(description)
    st.caption(
        f"{number(len(selection))} titres uniques sélectionnés sur {number(len(catalogue))}"
        " · Données historiques, non actualisées en direct"
    )
    if selection.empty:
        st.info("Aucun titre ne correspond à ces critères. Élargissez les filtres ou réinitialisez-les.")
        st.stop()

    with st.container(horizontal=True):
        for column in ["danceability", "energy", "valence"]:
            average = selection[column].mean() * 100
            reference = catalogue[column].mean() * 100
            st.metric(
                f"{AUDIO_LABELS[column]} moyenne / 100",
                number(average, 1),
                delta=f"{average - reference:+.1f} pts vs catalogue".replace(".", ","),
                delta_color="off",
                border=True,
                help="Moyenne sur les titres uniques. Un score plus élevé n'est pas forcément meilleur : il dépend de l'ambiance recherchée.",
            )


def style_chart(figure, height=380):
    """Même typographie, mêmes marges et mêmes couleurs sur toutes les pages."""
    figure.update_layout(
        height=height,
        font=dict(family="Arial, sans-serif", size=13, color="#F5F5F5"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=20, b=20),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    figure.update_xaxes(gridcolor="#303030", zeroline=False)
    figure.update_yaxes(gridcolor="#303030", zeroline=False)
    return figure


def show_method(quality):
    with st.expander("Comprendre les indicateurs et les données"):
        st.markdown(
            "**Dansabilité** : adéquation estimée à la danse. **Énergie** : intensité perçue. "
            "**Positivité (valence)** : caractère joyeux estimé du son. "
            "Les scores audio de 0 à 1 sont affichés de 0 à 100 pour faciliter la lecture. "
            "Ce ne sont ni des pourcentages de réussite ni des mesures de qualité."
        )
        st.write(
            f"Le fichier contient {number(quality['raw_rows'])} lignes, dont "
            f"{number(quality['strict_duplicates'])} doublons stricts retirés. "
            f"Il reste {number(quality['unique_tracks'])} identifiants de titres uniques "
            f"et {quality['genres']} genres."
        )
        st.write(
            "Chaque titre compte une fois dans les KPI. Pour chaque identifiant, nous conservons "
            "les valeurs de sa première ligne dans le fichier source. "
            f"{number(quality['popularity_conflicts'])} identifiants ont plusieurs scores de popularité dans la source. "
            "Leurs genres sont tous conservés : les effectifs par genre ne doivent donc pas être additionnés."
        )
        st.markdown(
            "La comparaison utilise toujours **le catalogue complet dédoublonné**, sans filtres. "
            "Le nombre de titres décrit la sélection, pas la qualité d'une playlist. "
            "Les scores de popularité sont historiques. Ces données ne démontrent pas "
            "qu'un profil sonore cause le succès d'un titre.\n\n"
            "[Dataset de Maharshi Pandya sur Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)"
            " · Projet pédagogique indépendant, sans affiliation à Spotify."
        )
