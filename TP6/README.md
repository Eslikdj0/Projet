# Atelier playlist

Dashboard Streamlit pour un curateur de playlists : filtrer un catalogue Spotify par ambiance musicale, comparer les genres et retrouver des titres à écouter. L'application comporte trois pages, trois KPI contextualisés et des filtres communs. Le thème reprend les couleurs Spotify avec un petit logo officiel local.

Le brief de référence est `brief_dashboard_projet.docx`. Le TP5 fournit le principe de composition (KPI, détail, sidebar, cache) ; `Projet_B_Spotify.ipynb` fournit l'analyse exploratoire. Le notebook original est conservé intact.

## Installation et lancement

**Si l'environnement `(env)` du projet est déjà activé**, rester dans `TP6` et utiliser :

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

L'erreur « streamlit n'est pas reconnu » signifie que PowerShell ne trouve pas son exécutable dans le `PATH` actif. L'environnement `env` peut être différent du Python sur lequel Streamlit est installé. `python -m pip` installe les dépendances pour le même interpréteur que `python -m streamlit`. La présence du fichier `requirements.txt` ne suffit pas : il faut exécuter l'installation.

Depuis un terminal **dans le dossier TP6**, avec Python 3.12 ou plus récent en 64 bits :

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Si Python 3.14 n'est pas installé, remplacer `py -3.14` par `py -3.12` ou par le chemin de votre Python 64 bits. L'environnement virtuel n'a pas besoin d'être activé. Ne pas utiliser le Python 3.13 **32 bits** présent sur certaines machines : les dépendances de données nécessitent un environnement compatible.

Sur macOS ou Linux :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run streamlit_app.py
```

Ouvrir l'adresse indiquée par Streamlit, habituellement `http://localhost:8501`. Le lancement depuis `TP6` permet de charger `.streamlit/config.toml`. Le CSV compressé et le logo sont inclus : le dashboard ne télécharge rien au démarrage et fonctionne hors ligne, sauf les liens vers Spotify.

## Parcours de l'application

1. Choisir un ou plusieurs genres et le traitement du contenu explicite dans la sidebar.
2. Ouvrir **Affiner le profil musical** pour ajuster énergie, dansabilité et positivité. La popularité reste un critère historique secondaire.
3. Lire les trois KPI et les barres de la page **Profil de la sélection**.
4. Passer à **Comparer les genres** pour comparer les moyennes et vérifier les effectifs.
5. Ouvrir **Explorer les titres**, survoler les points, rechercher un artiste et ouvrir les liens Spotify. Le CSV exporte tous les résultats de la liste, pas seulement les lignes visibles.

Les filtres de la sidebar s'appliquent aux trois pages et persistent lors de la navigation. Aucun genre sélectionné signifie aucun résultat. Le bouton de réinitialisation restaure pop, hip-hop et electronic, tous les contenus explicites et toutes les plages numériques. La recherche textuelle est propre à la liste des titres : elle ne change pas les KPI ni le nuage. L'application prépare une liste de candidats ; elle ne crée pas de playlist sur un compte Spotify.

## Organisation du code

```text
TP6/
├── streamlit_app.py         # Navigation, filtres communs et état partagé
├── data_utils.py            # Chargement, dédoublonnage, filtres, moyennes par genre
├── ui.py                    # Titres, KPI, formatage et explications communes
├── app_pages/
│   ├── profil.py            # Barres sélection / catalogue
│   ├── genres.py            # Matrice des profils musicaux
│   └── titres.py            # Nuage, recherche, tableau, export CSV
├── data/
│   ├── dataset.csv.gz       # Fichier Kaggle original, compressé sans perte
│   └── provenance.json     # Source, date et empreintes des données
├── assets/spotify-logo.svg  # Logo officiel, non modifié
├── .streamlit/config.toml   # Thème sombre
├── tests/test_dashboard.py  # Tests de données et d'interaction
├── requirements.txt        # Trois dépendances directes du dashboard
├── cadrage.md               # Cadrage demandé dans le brief
└── README.md
```

À lire pour expliquer le fonctionnement : `load_data()` → `prepare_data()` → widgets de `streamlit_app.py` → `filter_tracks()` → page choisie. Chaque interaction relance le script ; `@st.cache_data` évite de relire et nettoyer le fichier. Les widgets sont créés dans le point d'entrée pour garder leur état lors des changements de page. Les pages lisent la sélection commune dans `st.session_state`.

Les fonctions de calcul sont séparées de l'affichage pour pouvoir les tester. Aucune classe applicative, API Spotify, base de données, régression ou ACP n'est nécessaire au fonctionnement du dashboard. Les dépendances du notebook (scikit-learn, seaborn, etc.) ne sont donc pas installées par `requirements.txt`.

## Données et règle de comptage

Source : [Spotify Tracks Dataset de Maharshi Pandya sur Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset), le même dataset que celui du notebook. Téléchargé le 16 septembre 2026 via l'endpoint public Kaggle. `provenance.json` consigne les empreintes pour identifier le fichier exact utilisé. Il ne s'agit pas de données Spotify en temps réel.

- 114 000 lignes brutes, dont 450 doublons stricts supprimés après retrait de la colonne d'index exportée.
- 89 741 identifiants `track_id` uniques, associés à 114 genres.
- Pour chaque identifiant, on garde les valeurs de sa **première occurrence dans l'ordre du fichier**. C'est une convention reproductible, pas une sélection du score maximal ni du score le plus récent.
- 720 identifiants ont plusieurs valeurs de popularité dans le fichier. Les trois variables des KPI ne présentent pas ce conflit.
- Toutes les associations distinctes `(track_id, track_genre)` sont conservées. Un titre compte une fois dans les KPI et une fois dans chacun de ses genres lors des comparaisons. Les effectifs par genre ne sont pas additifs.
- Les métadonnées textuelles absentes sont remplacées par « Non renseigné ». La durée en minutes vaut `duration_ms / 60000`.

Le fichier gzip est lisible directement par pandas. Pour le remplacer, télécharger `dataset.csv` sur la page Kaggle, le compresser en `dataset.csv.gz`, puis actualiser la provenance et redémarrer l'application pour vider le cache. Les fichiers utilisés doivent garder les colonnes d'origine.

## Définition des KPI

Pour chacune des variables `danceability`, `energy`, `valence` :

```text
KPI = moyenne de la variable sur les titres uniques filtrés × 100
Référence = moyenne sur tous les titres uniques du catalogue × 100
Écart affiché = KPI − référence, en points
```

Ces scores ne sont pas des pourcentages. La référence reste fixe, même lorsque les filtres changent. Une énergie ou une positivité plus forte n'est pas automatiquement souhaitable : le delta reste neutre. Les indicateurs servent à construire l'ambiance souhaitée, et non à maximiser un score.

## Justification des visualisations

| Page | Graphique | Pourquoi ce choix ? |
|---|---|---|
| Profil | Barres horizontales groupées | Comparaison précise à une référence fixe, noms lisibles, axe 0–100 |
| Genres | Matrice de moyennes colorées et chiffrées | Lecture des ressemblances entre plusieurs profils ; couleurs sur la même échelle 0–100 |
| Titres | Nuage énergie–dansabilité | Montre les différences entre morceaux que les moyennes masquent ; axes fixes 0–1 |

La matrice affiche au maximum 15 genres, classés selon le critère choisi ; les valeurs de tous les genres filtrés sont accessibles en dessous. Les variables de la matrice sont déjà sur la même échelle 0–1 : pas de standardisation qui changerait le sens des scores. Le nuage utilise un échantillon reproductible de 2 000 titres au maximum (`random_state=42`) pour rester fluide. Les KPI, tableaux et exports utilisent la sélection complète.

## Limites et honnêteté

Le dataset échantillonne les genres et ne représente pas toute la plateforme. Il ne permet pas d'étudier une évolution temporelle ou les performances réelles d'une playlist. Des profils moyens proches ne garantissent pas une bonne transition entre deux morceaux. Il faut écouter les titres.

Les sorties du notebook ont été privilégiées par rapport à ses interprétations lorsqu'elles divergent. Par exemple, les sorties donnent 38,8 % dans la catégorie « Faible », alors que le commentaire parle de plus de la moitié ; le R² multiple affiché est 0,0221. Le dashboard ne reprend donc pas les promesses de succès algorithmique ni les interprétations causales non démontrées. Les chiffres peuvent différer du notebook parce que les KPI sont désormais calculés sur des titres uniques.

Logo fourni par les [ressources officielles Spotify](https://developer.spotify.com/documentation/design), extrait de l'archive `2024-spotify-full-logo.zip` : `Full_Logo_White_RGB.svg`. Il est affiché sans modification. Ce projet pédagogique indépendant n'est pas affilié à Spotify.

## Vérifications

Depuis `TP6`, après installation :

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Les tests vérifient le dédoublonnage avec conservation des genres, les conflits de popularité, la combinaison des filtres, la navigation entre les trois pages, le recalcul des KPI, une recherche sans résultat, une sélection de genres vide et la réinitialisation. Ils utilisent `unittest` (bibliothèque standard) et `AppTest` (inclus dans Streamlit).

Résultat local du 16 septembre 2026 : **3 tests réussis**, avec Python 3.14 et les versions de `requirements.txt`, puis avec l'environnement existant `../env` (Python 3.12, Streamlit 1.64.0, pandas 2.2.3, Plotly 7.1.0). Les versions de l'environnement existant n'ont pas été modifiées. La vérification visuelle dans un navigateur reste à faire : aucun navigateur connecté n'était disponible pendant la réalisation.

## Préparer la soutenance

- Présenter le curateur, son besoin de cohérence musicale et le message central.
- Montrer la sélection initiale, puis changer un genre et observer les KPI.
- Ajuster l'énergie, comparer les genres et retrouver un titre dans la liste.
- Expliquer la référence des KPI, les doublons multi-genres et l'échantillon du nuage.
- Conclure sur les limites des données et l'importance de l'écoute.

Le projet a été développé avec l'aide de Codex. Il faut pouvoir expliquer les fonctions et leurs calculs ; le notebook n'a pas été réexécuté ni réécrit.

## Déploiement en ligne reporté

À la demande de l'utilisateur, aucun déploiement ni dépôt distant n'est créé pour le moment. Aucun lien `streamlit.app` n'est donc encore disponible.

Quand le déploiement sera souhaité :

1. Publier **le contenu de TP6 à la racine d'un dépôt GitHub**, notamment `.streamlit/config.toml`, `data/`, `assets/` et `requirements.txt`. Ne pas publier `.venv`, les journaux ni les secrets.
2. Dans [Streamlit Community Cloud](https://share.streamlit.io/), sélectionner ce dépôt, la branche et `streamlit_app.py` comme fichier d'entrée.
3. Choisir Python 3.14 (version utilisée pour les vérifications locales), puis déployer.
4. Vérifier les trois pages, les filtres et l'export sur le site ; ajouter ensuite le véritable lien dans ce README.

La racine du dépôt est importante pour charger le thème. Les dépendances se trouvent dans le `requirements.txt` voisin du point d'entrée. Voir la [documentation officielle de déploiement](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
