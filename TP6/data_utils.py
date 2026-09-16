"""Chargement, dédoublonnage et filtres du catalogue Spotify."""

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "dataset.csv.gz"
AUDIO_LABELS = {
    "danceability": "Dansabilité",
    "energy": "Énergie",
    "valence": "Positivité",
    "acousticness": "Caractère acoustique",
    "instrumentalness": "Caractère instrumental",
}


def prepare_data(raw):
    """Sépare les titres uniques de leurs associations à plusieurs genres.

    La première occurrence du CSV sert de référence pour chaque identifiant.
    Cela évite de choisir arbitrairement le score de popularité le plus élevé.
    Les genres sont conservés dans une table séparée, sans perte d'association.
    """
    clean = raw.drop(columns=["Unnamed: 0"], errors="ignore").drop_duplicates()
    clean = clean.copy()
    for column in ["artists", "track_name", "album_name", "track_genre"]:
        clean[column] = clean[column].fillna("Non renseigné")

    genres = clean[["track_id", "track_genre"]].drop_duplicates()
    tracks = clean.drop_duplicates("track_id").drop(columns="track_genre").copy()
    tracks["duration_min"] = tracks["duration_ms"] / 60_000
    genre_names = genres.groupby("track_id")["track_genre"].agg(
        lambda values: ", ".join(sorted(values))
    )
    tracks["genres"] = tracks["track_id"].map(genre_names)
    tracks["spotify_url"] = "https://open.spotify.com/track/" + tracks["track_id"]
    quality = {
        "raw_rows": len(raw),
        "strict_duplicates": len(raw) - len(clean),
        "unique_tracks": len(tracks),
        "genres": genres["track_genre"].nunique(),
        "popularity_conflicts": int(
            (clean.groupby("track_id")["popularity"].nunique() > 1).sum()
        ),
    }
    return tracks.reset_index(drop=True), genres, quality


@st.cache_data(show_spinner="Chargement du catalogue…")
def load_data():
    """Pandas lit directement le CSV compressé livré avec le projet."""
    raw = pd.read_csv(DATA_PATH)
    return prepare_data(raw)


def filter_tracks(tracks, genres, filters):
    """Applique tous les filtres aux titres uniques ; les bornes sont incluses."""
    matching_ids = genres.loc[
        genres["track_genre"].isin(filters["genres"]), "track_id"
    ]
    mask = tracks["track_id"].isin(matching_ids)
    if filters["explicit"] != "Tous":
        mask &= tracks["explicit"].eq(filters["explicit"] == "Explicites uniquement")
    for column in ["popularity", "energy", "danceability", "valence"]:
        low, high = filters[column]
        mask &= tracks[column].between(low, high)
    return tracks.loc[mask].copy()


def genre_profiles(selection, genres, chosen_genres):
    """Un titre compte une fois dans chacun de ses genres sélectionnés."""
    associations = genres[genres["track_genre"].isin(chosen_genres)]
    joined = associations.merge(selection, on="track_id", how="inner", validate="many_to_one")
    averages = joined.groupby("track_genre")[list(AUDIO_LABELS)].mean()
    averages["effectif"] = joined.groupby("track_genre")["track_id"].nunique()
    return averages
