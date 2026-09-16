"""
Bac à sable Streamlit — HETIC MD4, Dashboards & Data Visualisation.

Objectif : découvrir les composants Streamlit en les touchant, pas en
lisant une slide. Chaque exemple montre son code ET son résultat rendu.
Modifiez les valeurs, cassez des choses, relancez — rien n'est noté ici.

Lancer avec : streamlit run bac_a_sable.py
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bac à sable Streamlit", layout="wide")

st.title("🏖️ Bac à sable Streamlit")
st.caption("Un terrain de jeu pour découvrir les composants avant le TP. Rien n'est noté ici.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Texte & mise en page", "🎛️ Widgets", "📊 Graphiques", "⚡ Cache & session_state",
])

# petit dataset Vélib pour les exemples de graphiques
df = pd.read_csv("data/velib_meteo.csv")


def demo(code, render_fn):
    """Affiche le code d'un côté, son résultat rendu de l'autre."""
    c1, c2 = st.columns([1, 1])
    with c1:
        st.code(code, language="python")
    with c2:
        render_fn()
    st.divider()


def _pyplot_demo(par_heure):
    fig, ax = plt.subplots()
    ax.plot(par_heure.index, par_heure.values, color="#00634B", linewidth=2)
    ax.set_xlabel("Heure")
    ax.set_ylabel("Trajets moyens")
    st.pyplot(fig)


# ============================================================
# TAB 1 — Texte & mise en page
# ============================================================
with tab1:
    st.header("Texte & mise en page")

    demo(
        'st.title("Un titre")\nst.header("Un header")\nst.subheader("Un subheader")',
        lambda: (st.title("Un titre"), st.header("Un header"), st.subheader("Un subheader")),
    )

    demo(
        'st.write("Du texte simple")\nst.markdown("**Du gras**, *de l\'italique*")',
        lambda: (st.write("Du texte simple"), st.markdown("**Du gras**, *de l'italique*")),
    )

    demo(
        'col1, col2 = st.columns(2)\ncol1.write("Colonne 1")\ncol2.write("Colonne 2")',
        lambda: (lambda c: (c[0].write("Colonne 1"), c[1].write("Colonne 2")))(st.columns(2)),
    )

    demo(
        'st.divider()  # juste une ligne de separation',
        lambda: (st.write("Avant"), st.divider(), st.write("Après")),
    )

# ============================================================
# TAB 2 — Widgets
# ============================================================
with tab2:
    st.header("Widgets")
    st.markdown("Chaque widget **renvoie sa valeur** — pas de gestion d'événement à écrire.")

    demo(
        'valeur = st.slider("Choisir une heure", 0, 23, 12)\nst.write("Heure choisie :", valeur)',
        lambda: st.write("Heure choisie :", st.slider("Choisir une heure", 0, 23, 12, key="s1")),
    )

    demo(
        'quartier = st.selectbox("Quartier", ["Centre", "Nord", "Sud"])\nst.write("Sélectionné :", quartier)',
        lambda: st.write("Sélectionné :", st.selectbox("Quartier", sorted(df["quartier"].unique()), key="s2")),
    )

    demo(
        'quartiers = st.multiselect("Quartiers", ["Centre", "Nord", "Sud", "Est", "Ouest"])\nst.write(quartiers)',
        lambda: st.write(st.multiselect("Quartiers", sorted(df["quartier"].unique()), key="s3")),
    )

    demo(
        'pluie = st.checkbox("Exclure les jours de pluie")\nst.write("Coché :", pluie)',
        lambda: st.write("Coché :", st.checkbox("Exclure les jours de pluie", key="s4")),
    )

    demo(
        'if st.button("Cliquez-moi"):\n    st.write("Vous avez cliqué !")',
        lambda: st.write("Vous avez cliqué !") if st.button("Cliquez-moi", key="s5") else None,
    )

    demo(
        'st.metric("Trajets aujourd\'hui", "1 284", delta="+8%")',
        lambda: st.metric("Trajets aujourd'hui", "1 284", delta="+8%"),
    )

# ============================================================
# TAB 3 — Graphiques
# ============================================================
with tab3:
    st.header("Graphiques")

    par_heure = df.groupby("heure")["trajets"].mean()

    demo(
        'st.line_chart(par_heure)  # graphique rapide, a partir d\'une Series/DataFrame',
        lambda: st.line_chart(par_heure),
    )

    demo(
        'st.bar_chart(df.groupby("quartier")["trajets"].sum())',
        lambda: st.bar_chart(df.groupby("quartier")["trajets"].sum()),
    )

    demo(
        'fig, ax = plt.subplots()\nax.plot(par_heure.index, par_heure.values)\nst.pyplot(fig)  '
        '# pour un controle total (couleurs, annotations...)',
        lambda: _pyplot_demo(par_heure),
    )

    demo(
        'st.dataframe(df.head())  # tableau interactif (tri, scroll)',
        lambda: st.dataframe(df.head()),
    )


# ============================================================
# TAB 4 — Cache & session_state
# ============================================================
with tab4:
    st.header("Cache & session_state")

    st.markdown("#### @st.cache_data")
    st.code(
        '@st.cache_data\ndef charger_donnees():\n    return pd.read_csv("data/velib_meteo.csv")\n\n'
        'df = charger_donnees()  # rechargé seulement si le fichier/les arguments changent',
        language="python",
    )
    st.info("Sans ce décorateur, le CSV serait relu à chaque interaction — même si rien n'a changé.")
    st.divider()

    st.markdown("#### st.session_state")
    st.write("Cliquez plusieurs fois : le compteur persiste grâce à `st.session_state`, "
             "contrairement à une simple variable Python qui repartirait de 0 à chaque clic.")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.code(
            'if "compteur" not in st.session_state:\n    st.session_state.compteur = 0\n\n'
            'if st.button("Incrémenter"):\n    st.session_state.compteur += 1\n\n'
            'st.metric("Compteur", st.session_state.compteur)',
            language="python",
        )
    with c2:
        if "compteur" not in st.session_state:
            st.session_state.compteur = 0
        if st.button("Incrémenter", key="s6"):
            st.session_state.compteur += 1
        st.metric("Compteur", st.session_state.compteur)
