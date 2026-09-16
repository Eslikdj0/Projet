"""
v2 — Version polie (séance 4 : règle des 5 secondes, KPIs contextualisés,
charge cognitive, canal préattentif).

Structure en zones : KPIs contextualisés en haut (visibles en < 5 secondes),
UN graphique principal en dessous, filtres en sidebar. La couleur (canal
préattentif) isole la série "Semaine" — la plus importante pour le message —
du reste, plutôt que de donner le même poids visuel à tout.

Lancer avec : streamlit run v2_poli_final.py
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Vélib — usage", layout="wide")

HETIC_GREEN_DARK = "#00634B"
HETIC_GREEN_LIGHT = "#00C19D"
HETIC_PURPLE = "#332A7B"
HETIC_GREY = "#B0B0B0"

@st.cache_data
def load_data():
    return pd.read_csv("data/velib_synth.csv")


@st.cache_data
def compute_kpis(df):
    """Calculs coûteux isolés dans une fonction cachée : recalculés seulement
    si les données filtrées changent, pas à chaque interaction."""
    par_heure = df.groupby("heure")["trajets"].mean()
    pic = par_heure.max()
    creux = par_heure.min()
    ratio_pointe = pic / creux if creux > 0 else 0

    moy_sec = df.loc[~df["pluie"], "trajets"].mean()
    moy_pluie = df.loc[df["pluie"], "trajets"].mean()
    ecart_pluie = (moy_pluie / moy_sec - 1) * 100 if moy_sec else 0

    moy_semaine = df.loc[~df["is_weekend"], "trajets"].mean()
    moy_weekend = df.loc[df["is_weekend"], "trajets"].mean()
    ecart_weekend = (moy_weekend / moy_semaine - 1) * 100 if moy_semaine else 0

    return ratio_pointe, moy_pluie, ecart_pluie, ecart_weekend


df = load_data()

# --- Sidebar : filtres ---
st.sidebar.header("Filtres")
quartiers = st.sidebar.multiselect(
    "Quartier", options=sorted(df["quartier"].unique()),
    default=sorted(df["quartier"].unique()),
)
df_filtre = df[df["quartier"].isin(quartiers)] if quartiers else df

# --- Titre qui porte le message (Minto) ---
st.markdown("<h1 style='color:#332A7B;'>Titre 1 : Vélib suit un rythme hebdomadaire net, et la pluie fait chuter l'usage</h1>", 
            unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script&display=swap');

.mon-titre {
    font-family: 'Dancing Script', cursive;
    font-size: 3rem;
    color: #332A7B;
}
</style>
<p class="mon-titre">Ceci n'est pas un titre.</p>
""", unsafe_allow_html=True)

st.title("Titre 2 : Vélib suit un rythme hebdomadaire net, et la pluie fait chuter l'usage")
st.caption("Deux pics en semaine (8h / 18h), un profil en cloche le week-end — "
           "et un usage nettement réduit les jours de pluie.")

# --- Zone KPIs : contextualisés, visibles en < 5 secondes (règle de Few) ---
ratio_pointe, moy_pluie, ecart_pluie, ecart_weekend = compute_kpis(df_filtre)

col1, col2, col3 = st.columns(3)
col1.metric("Ratio heure de pointe / creuse", f"×{ratio_pointe:.1f}")
col2.metric("Trajets/h en moyenne, jours de pluie", f"{moy_pluie:.0f}",
            delta=f"{ecart_pluie:.0f}% vs jours secs", delta_color="off")
col3.metric("Usage le week-end vs semaine", f"{ecart_weekend:+.0f}%")

st.divider()


# --- Zone détail : UN graphique, avec canal préattentif (couleur) ---
profil = df_filtre.groupby(["is_weekend", "heure"])["trajets"].mean().unstack(level=0)
profil.columns = ["Semaine", "Week-end"]



fig = go.Figure()

fig.add_trace(go.Scatter(
    x=profil.index, y=profil["Week-end"],
    name="Week-end", line=dict(color=HETIC_GREY, width=2),
))
fig.add_trace(go.Scatter(
    x=profil.index, y=profil["Semaine"],
    name="Semaine", line=dict(color=HETIC_GREEN_DARK, width=3),
))

fig.add_annotation(
    x=8, y=profil["Semaine"].iloc[8],
    text="Pic du matin<br>(8h)",
    showarrow=True, arrowhead=2, ax=-40, ay=-40,
    font=dict(color=HETIC_PURPLE, size=12, weight="bold"),
)
fig.add_annotation(
    x=18, y=profil["Semaine"].iloc[18],
    text="Pic du soir<br>(18h)",
    showarrow=True, arrowhead=2, ax=40, ay=-40,
    font=dict(color=HETIC_PURPLE, size=12, weight="bold"),
)

fig.update_layout(
    xaxis_title="Heure de la journée",
    yaxis_title="Trajets moyens par heure",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    margin=dict(l=10, r=10, t=30, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.2)")

st.plotly_chart(fig, use_container_width=True)

st.caption(f"{len(quartiers) if quartiers else len(df['quartier'].unique())} "
           f"quartier(s) sélectionné(s). Données synthétiques à but pédagogique.")
