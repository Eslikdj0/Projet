"""Comparer les profils moyens sans confondre genre et popularité."""

import plotly.graph_objects as go
import streamlit as st

from data_utils import AUDIO_LABELS, genre_profiles
from ui import GREEN, show_header, style_chart

selection = st.session_state["selection"]
show_header(
    "Des genres différents peuvent partager une ambiance",
    "Repérez les proximités sonores pour varier les genres tout en conservant le profil musical recherché.",
    selection,
    st.session_state["catalogue"],
)

profiles = genre_profiles(selection, st.session_state["genre_associations"], st.session_state["genres"])
audio_feature = st.selectbox("Caractéristique audio à comparer", list(AUDIO_LABELS), format_func=AUDIO_LABELS.get)
sort_by = st.selectbox("Classer les genres par", ["effectif", *AUDIO_LABELS], format_func=lambda key: AUDIO_LABELS.get(key, "Nombre de titres"))
profiles = profiles.sort_values([sort_by], ascending=False, kind="stable")
shown = profiles.head(15)
st.subheader(f"{AUDIO_LABELS[audio_feature]} moyenne par genre")
st.caption("Jusqu'à 15 genres affichés. Choisissez les genres à comparer dans la barre latérale.")

values = shown[audio_feature] * 100
row_labels = [f"{genre} · {int(count)} titres" for genre, count in shown["effectif"].items()]
figure = go.Figure(go.Bar(
    x=values, y=row_labels, orientation="h", marker_color=GREEN,
    text=values, texttemplate="%{text:.1f}", textposition="auto",
    hovertemplate="%{y}<br>Score moyen : %{x:.1f} / 100<extra></extra>",
))
figure.update_xaxes(range=[0, 100], title=f"{AUDIO_LABELS[audio_feature]} moyenne / 100")
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
