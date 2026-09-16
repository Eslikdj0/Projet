"""Comparer les profils moyens sans confondre genre et popularité."""

import plotly.graph_objects as go
import streamlit as st

from data_utils import AUDIO_LABELS, genre_profiles
from ui import show_header, style_chart

selection = st.session_state["selection"]
show_header(
    "Des genres différents peuvent partager une ambiance",
    "Repérez les proximités sonores pour varier les genres tout en conservant le profil musical recherché.",
    selection,
    st.session_state["catalogue"],
)

profiles = genre_profiles(selection, st.session_state["genre_associations"], st.session_state["genres"])
sort_by = st.selectbox("Classer les genres par", ["effectif", *AUDIO_LABELS], format_func=lambda key: AUDIO_LABELS.get(key, "Nombre de titres"))
profiles = profiles.sort_values([sort_by], ascending=False, kind="stable")
shown = profiles.head(15)
st.subheader("Profils audio par genre")
st.caption("Jusqu'à 15 genres affichés. Choisissez les genres à comparer dans la barre latérale.")

values = shown[list(AUDIO_LABELS)] * 100
row_labels = [f"{genre} · {int(count)} titres" for genre, count in shown["effectif"].items()]
figure = go.Figure(go.Heatmap(
    z=values.values, x=list(AUDIO_LABELS.values()), y=row_labels,
    zmin=0, zmax=100, colorscale=[[0, "#17251D"], [0.5, "#39734D"], [1, "#1ED760"]],
    text=values.round(0).values, texttemplate="%{text:.0f}", textfont=dict(color="white"),
    colorbar=dict(title="Score / 100"),
    hovertemplate="%{y}<br>%{x} : %{z:.1f} / 100<extra></extra>",
))
figure.update_yaxes(autorange="reversed")
st.plotly_chart(style_chart(figure, max(320, len(shown) * 36)), width="stretch")
st.caption(
    "Moyennes sur une échelle commune de 0 à 100, sans standardisation. "
    "Un titre peut contribuer à plusieurs genres ; une moyenne masque les différences entre morceaux."
)
if (shown["effectif"] < 30).any():
    st.info("Certains genres comptent moins de 30 titres après filtrage : leurs moyennes reposent sur de petits effectifs.")
with st.expander("Voir les valeurs de tous les genres filtrés"):
    st.dataframe(profiles.rename(columns=AUDIO_LABELS).round(3), width="stretch")
