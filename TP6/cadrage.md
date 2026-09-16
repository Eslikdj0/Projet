# Cadrage du dashboard Atelier playlist

## Message clé

Les profils audio permettent de composer une sélection musicale cohérente entre plusieurs genres, sans garantir la popularité des titres.

## Audience et décision

Le dashboard s'adresse à un curateur de playlists. Il doit pouvoir préciser une ambiance, comparer les genres compatibles, puis identifier des titres à écouter. Il s'appuie sur l'AED de `Projet_B_Spotify.ipynb`, notamment les profils audio et l'analyse par genre. Les exigences de réalisation viennent de `brief_dashboard_projet.docx`.

## Trois KPI actionnables

| Indicateur | Contexte | Décision possible |
|---|---|---|
| Dansabilité moyenne | Écart en points avec le catalogue complet | Ajuster la sélection à un usage orienté danse |
| Énergie moyenne | Même référence | Renforcer ou calmer l'intensité musicale |
| Positivité moyenne (valence) | Même référence | Orienter l'ambiance vers des sons plus joyeux ou plus mélancoliques |

Ces scores sont convertis de 0–1 vers 0–100. Un score élevé n'est pas automatiquement meilleur. Ils sont actionnables lorsqu'ils aident à ajuster une ambiance recherchée ; ils ne mesurent pas la réussite d'une playlist. Le nombre de titres est un contexte de lecture, pas un KPI de performance. Il n'y a pas de tendance temporelle disponible.

## Structure et interactions

- **Profil de la sélection** : trois KPI en haut, puis un graphique de barres horizontales comparant les moyennes au catalogue. Les barres permettent une comparaison précise sur un axe commun qui commence à zéro.
- **Comparer les genres** : mêmes KPI, puis une matrice colorée des profils moyens, avec effectifs et valeurs affichées. Elle facilite le repérage des proximités entre genres ; l'échelle reste fixée de 0 à 100.
- **Explorer les titres** : mêmes KPI, puis un nuage énergie–dansabilité pour montrer la dispersion réelle des morceaux, accompagné d'une liste recherchable et exportable avec liens Spotify.

Les filtres communs sont dans la sidebar : genres, contenu explicite, popularité historique et plages audio. Ils persistent entre les pages. Le vert souligne la sélection, le gris indique la référence. Le thème sombre, la typographie simple et le petit logo limitent la charge visuelle. Une seule visualisation principale est présentée par page.

## Honnêteté et limites

Les KPI portent sur les identifiants uniques. Les associations multiples aux genres sont conservées, donc les effectifs par genre ne s'additionnent pas. Pour chaque identifiant, les valeurs de la première occurrence source sont retenues. La popularité n'est pas actualisée. Le catalogue échantillonné par genre ne représente pas toute la plateforme. Les moyennes ne remplacent pas l'écoute. Le nuage est limité à 2 000 points reproductibles, sans réduire les calculs ni les exports.

Le code a été préparé avec l'aide de Codex. Le README explique les calculs, les choix visuels et le parcours du code pour préparer la soutenance. Le déploiement est reporté à la demande de l'utilisateur.
