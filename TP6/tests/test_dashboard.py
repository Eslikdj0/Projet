"""Vérifications des risques principaux : doublons, filtres et navigation."""

import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_utils import filter_tracks, genre_profiles, load_data, prepare_data

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


class DataTests(unittest.TestCase):
    def test_duplicate_ids_keep_all_genres_without_double_counting(self):
        raw = pd.DataFrame([
            dict(track_id="a", track_name="A", artists="X", album_name="Album", track_genre="pop", popularity=30, duration_ms=180000, danceability=0.8, energy=0.7, valence=0.6, acousticness=0.2, instrumentalness=0.0, explicit=False),
            dict(track_id="a", track_name="A", artists="X", album_name="Album", track_genre="dance", popularity=80, duration_ms=180000, danceability=0.8, energy=0.7, valence=0.6, acousticness=0.2, instrumentalness=0.0, explicit=False),
        ])
        tracks, genres, quality = prepare_data(pd.concat([raw, raw.iloc[:1]]))
        self.assertEqual(len(tracks), 1)
        self.assertEqual(len(genres), 2)
        self.assertEqual(tracks.iloc[0]["popularity"], 30)
        self.assertEqual(quality["strict_duplicates"], 1)
        self.assertEqual(quality["popularity_conflicts"], 1)
        profiles = genre_profiles(tracks, genres, ["pop", "dance"])
        self.assertEqual(profiles["effectif"].to_dict(), {"dance": 1, "pop": 1})

    def test_combined_filters_and_empty_genres(self):
        tracks, genres, _ = load_data()
        filters = dict(genres=["pop"], explicit="Sans contenu explicite", popularity=(26, 75), energy=(0.4, 0.8), danceability=(0.5, 1.0), valence=(0.0, 1.0))
        result = filter_tracks(tracks, genres, filters)
        expected_ids = set(genres.loc[genres.track_genre.eq("pop"), "track_id"])
        self.assertGreater(len(result), 0)
        self.assertTrue(result.track_id.is_unique)
        self.assertTrue(set(result.track_id).issubset(expected_ids))
        self.assertFalse(result.explicit.any())
        self.assertTrue(result.popularity.between(26, 75).all())
        self.assertTrue(result.energy.between(0.4, 0.8).all())
        self.assertTrue(result.danceability.between(0.5, 1).all())
        filters["genres"] = []
        self.assertTrue(filter_tracks(tracks, genres, filters).empty)


class InterfaceTests(unittest.TestCase):
    def test_navigation_shared_filters_search_and_reset(self):
        app = AppTest.from_file(str(APP), default_timeout=40).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 3)
        before = app.metric[0].value
        app.multiselect(key="genres").set_value(["classical"]).run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.metric[0].value, before)
        app.slider(key="energy").set_value((0.1, 0.6)).run()
        app.selectbox(key="explicit").select("Sans contenu explicite").run()
        expected_count = len(app.session_state["selection"])
        for page in ["app_pages/genres.py", "app_pages/titres.py"]:
            app.switch_page(page).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.multiselect(key="genres").value, ["classical"])
            self.assertEqual(len(app.session_state["selection"]), expected_count)
            self.assertEqual(len(app.metric), 3)

        app.text_input(key="track_query").input("__aucun_titre_123456__").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe[0].value), 0)
        app.multiselect(key="genres").set_value([]).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.info)
        self.assertEqual(len(app.metric), 0)
        app.button[0].click().run()
        self.assertEqual(app.multiselect(key="genres").value, ["pop", "hip-hop", "electronic"])
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
