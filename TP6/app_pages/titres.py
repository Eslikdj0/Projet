"""Explorer les titres, ouvrir Spotify et exporter une liste de candidats."""

import plotly.express as px
import streamlit as st

from ui import GREEN, number, show_header, style_chart

selection = st.session_state["selection"]
show_header(
    "Quels morceaux sont les plus dansants et les plus énergiques ?",
    "Explorez les nuances d'énergie et de danse, puis retrouvez les morceaux à écouter dans Spotify.",
    selection,
    st.session_state["catalogue"],
)

# L'échantillonnage ne concerne que le graphique : KPI, recherche et export restent complets.
sample = selection.sample(n=min(2000, len(selection)), random_state=42)
figure = px.scatter(
    sample, x="danceability", y="energy", hover_name="track_name",
    hover_data={"artists": True, "popularity": True, "valence": ":.2f"},
    labels={"danceability": "Dansabilité", "energy": "Énergie", "artists": "Artistes", "popularity": "Popularité historique", "valence": "Positivité"},
    color_discrete_sequence=[GREEN], opacity=0.45,
)
figure.update_traces(marker=dict(size=6))
figure.update_xaxes(range=[0, 1])
figure.update_yaxes(range=[0, 1])
st.plotly_chart(style_chart(figure, 330), width="stretch")
st.caption(f"{number(len(sample))} titres affichés sur {number(len(selection))} · Échantillon reproductible si la sélection dépasse 2 000 titres. Survolez les points pour les détails.")

st.subheader("Titres à écouter")
search_col, sort_col, limit_col = st.columns([2, 2, 1])
query = search_col.text_input("Rechercher un titre ou un artiste", key="track_query").strip()
sort_options = {"popularity": "Popularité décroissante", "danceability": "Dansabilité décroissante", "energy": "Énergie décroissante", "valence": "Positivité décroissante"}
sort_by = sort_col.selectbox("Trier la liste", list(sort_options), format_func=sort_options.get)
limit = limit_col.selectbox("Lignes affichées", [25, 50, 100, 200], index=1)
candidates = selection
if query:
    mask = candidates["track_name"].str.contains(query, case=False, regex=False)
    mask |= candidates["artists"].str.contains(query, case=False, regex=False)
    candidates = candidates.loc[mask]
candidates = candidates.sort_values([sort_by, "track_id"], ascending=[False, True])

columns = ["track_name", "artists", "genres", "explicit", "duration_min", "danceability", "energy", "valence", "popularity", "spotify_url"]
st.dataframe(
    candidates[columns].head(limit), hide_index=True, width="stretch",
    column_config={
        "track_name": st.column_config.TextColumn("Titre", pinned=True),
        "artists": "Artistes", "genres": "Genres", "explicit": "Explicite",
        "duration_min": st.column_config.NumberColumn("Durée (min)", format="%.2f"),
        "danceability": st.column_config.NumberColumn("Dansabilité", format="%.2f"),
        "energy": st.column_config.NumberColumn("Énergie", format="%.2f"),
        "valence": st.column_config.NumberColumn("Positivité", format="%.2f"),
        "popularity": "Popularité / 100",
        "spotify_url": st.column_config.LinkColumn("Spotify", display_text="Écouter"),
    },
)
st.caption(f"{number(min(limit, len(candidates)))} lignes affichées sur {number(len(candidates))} résultats. La recherche agit sur la liste et son export ; les KPI et le graphique conservent les filtres de la sidebar.")
if candidates.empty:
    st.info("Aucun résultat pour cette recherche. Essayez un autre nom de titre ou d'artiste.")
st.download_button(
    "Télécharger tous les résultats (CSV)",
    data=candidates[["track_id", *columns]].to_csv(index=False).encode("utf-8-sig"),
    file_name="selection_playlist.csv", mime="text/csv", disabled=candidates.empty,
)
