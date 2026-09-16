"""Vue de synthèse : comparer l'ambiance sélectionnée au catalogue."""

import plotly.graph_objects as go
import streamlit as st

from data_utils import AUDIO_LABELS
from ui import GREEN, GREY, show_header, style_chart

selection = st.session_state["selection"]
catalogue = st.session_state["catalogue"]

show_header(
    "Le profil sonore guide votre sélection",
    "Comparez l'ambiance de vos titres au catalogue, puis ajustez les filtres pour préparer une playlist cohérente.",
    selection,
    catalogue,
)

st.subheader("Ce qui distingue votre sélection")
figure = go.Figure()
for data, name, color in [(catalogue, "Catalogue complet", GREY), (selection, "Votre sélection", GREEN)]:
    values = data[list(AUDIO_LABELS)].mean() * 100
    figure.add_trace(go.Bar(
        y=list(AUDIO_LABELS.values()), x=values, name=name, orientation="h",
        marker_color=color, text=values.round(1), textposition="auto",
        hovertemplate="%{y} : %{x:.1f} / 100<extra>%{fullData.name}</extra>",
    ))
figure.update_layout(barmode="group")
figure.update_xaxes(range=[0, 100], title="Score audio moyen / 100")
figure.update_yaxes(autorange="reversed")
st.plotly_chart(style_chart(figure, 410), width="stretch")
st.caption("Les barres partent de zéro. Le vert repère votre sélection ; le gris sert de référence stable.")

with st.container(border=True):
    st.markdown("**Comment utiliser cette vue ?**")
    st.write(
        "Pour une ambiance plus calme, réduisez la plage d'énergie. Pour une sélection orientée danse, "
        "augmentez la dansabilité minimale. Vérifiez ensuite les genres et écoutez les titres avant de décider."
    )
