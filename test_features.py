import unittest
from main import (
    extract_features,
    extract_personal_info_features,
    score_rules,
    label_from_score,
    generate_feedback,
    estimate_strength_rules,
    estimate_strength,
)


# helper used across test classes
def get_all_features(password, first_name="", last_name="", birthday=""):
    pw_features = extract_features(password)
    personal_features = extract_personal_info_features(
        password, first_name, last_name, birthday
    )
    return {**pw_features, **personal_features}


class TestExtractFeatures(unittest.TestCase):

    def test_length_and_char_counts(self):
        features = extract_features("Ab1!")
        self.assertEqual(features['length'], 4)
        self.assertEqual(features['num_lower'], 1)
        self.assertEqual(features['num_upper'], 1)
        self.assertEqual(features['num_digits'], 1)
        self.assertEqual(features['num_symbols'], 1)

    def test_uniqueness(self):
        features = extract_features("aabbcc")
        self.assertEqual(features['num_unique_chars'], 3)
        self.assertAlmostEqual(features['unique_ratio'], 0.5)

    def test_patterns(self):
        # sequence + dictionary word
        features = extract_features("password123")
        self.assertTrue(features['has_sequence'])
        self.assertTrue(features['has_dictionary_word'])

        # run length
        features = extract_features("aaabbaaa")
        self.assertEqual(features['max_run_length'], 3)

        # ends with year
        self.assertTrue(extract_features("MyPass1990")['ends_with_year'])
        self.assertFalse(extract_features("Pass1850")['ends_with_year'])

    def test_empty_password(self):
        features = extract_features("")
        self.assertEqual(features['length'], 0)
        self.assertEqual(features['max_run_length'], 0)


class TestExtractPersonalInfoFeatures(unittest.TestCase):

    def test_name_detection(self):
        # full name (case-insensitive)
        features = extract_personal_info_features(
            "JohnSmith2025", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_first_name'])
        self.assertTrue(features['contains_last_name'])
        self.assertTrue(features['contains_full_name'])
        self.assertTrue(features['contains_name_fragment'])

        # case insensitive
        features = extract_personal_info_features(
            "JOHN2025", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_first_name'])

    def test_birthday_detection(self):
        features = extract_personal_info_features(
            "Pass0515", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_combo'])
        self.assertTrue(features['contains_birth_month'])
        self.assertTrue(features['contains_birth_day'])

        features = extract_personal_info_features(
            "Pass1990", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_year'])

    def test_invalid_and_empty_inputs(self):
        # invalid birthday
        features = extract_personal_info_features("SomePass", "John", "Smith", "invalid")
        self.assertFalse(features['contains_birth_year'])

        # empty names
        features = extract_personal_info_features("Password123", "", "", "1990-05-15")
        self.assertFalse(features['contains_first_name'])
        self.assertFalse(features['contains_full_name'])


class TestScoring(unittest.TestCase):

    def test_score_range(self):
        self.assertEqual(score_rules(get_all_features("")), 0)

        self.assertEqual(score_rules(get_all_features("aB3$eF7!hJ1@kL5#nO9&")), 100)

        score = score_rules(get_all_features("password", "pass", "word", "2000-01-01"))
        self.assertGreaterEqual(score, 0)

    def test_weak_vs_strong(self):
        self.assertLess(score_rules(get_all_features("abc")), 61)
        self.assertGreater(score_rules(get_all_features("c!Xk9@Lm#Qz7wP$nR2v")), 80)

    def test_penalties_lower_score(self):
        # dictionary word penalty
        clean = score_rules(get_all_features("xYz789QwE"))
        with_dict = score_rules(get_all_features("password9Q"))
        self.assertGreater(clean, with_dict)

        # personal info penalty
        pw = "JaneDoe2025!"
        without_ctx = score_rules(get_all_features(pw))
        with_ctx = score_rules(get_all_features(pw, "Jane", "Doe", "1990-01-01"))
        self.assertGreater(without_ctx, with_ctx)

    def test_label_thresholds(self):
        self.assertEqual(label_from_score(0), "weak")
        self.assertEqual(label_from_score(60), "weak")
        self.assertEqual(label_from_score(61), "ok")
        self.assertEqual(label_from_score(80), "ok")
        self.assertEqual(label_from_score(81), "strong")
        self.assertEqual(label_from_score(100), "strong")


class TestFeedback(unittest.TestCase):

    def test_weak_password_feedback(self):
        feedback = generate_feedback(get_all_features("pass123"))
        self.assertGreater(len(feedback), 0)
        self.assertLessEqual(len(feedback), 4)
        joined = " ".join(feedback)
        self.assertIn("8 characters", joined)

    def test_personal_info_feedback(self):
        feedback = generate_feedback(get_all_features("JaneDoe!99", "Jane", "Doe", ""))
        self.assertTrue(any("name" in msg for msg in feedback))

        feedback = generate_feedback(get_all_features("myPass0322!", "Jane", "Doe", "1995-03-22"))
        self.assertTrue(any("birthday" in msg for msg in feedback))

    def test_strong_password_feedback(self):
        feedback = generate_feedback(get_all_features("aB3$eF7!hJ1@kL5#nO9&"))
        self.assertTrue(any("Great" in msg for msg in feedback))


class TestEstimateStrengthRules(unittest.TestCase):

    def test_full_pipeline(self):
        result = estimate_strength_rules("abc")
        self.assertIn("score", result)
        self.assertIn("label", result)
        self.assertIn("feedback", result)
        self.assertLess(result["score"], 61)
        self.assertEqual(result["label"], "weak")

        result = estimate_strength_rules("aB3$eF7!hJ1@kL5#nO9&")
        self.assertGreater(result["score"], 80)
        self.assertEqual(result["label"], "strong")


class TestEstimateStrength(unittest.TestCase):

    def test_output_shape(self):
        # result always has the three required keys
        result = estimate_strength("abc")
        self.assertIn("score", result)
        self.assertIn("label", result)
        self.assertIn("feedback", result)

    def test_personal_info_lowers_score(self):
        # same password, but with personal context should score lower
        pw = "c!Xk9@Lm#Qz7wP$nR2v"
        without_ctx = estimate_strength(pw)
        with_ctx = estimate_strength("Jane1995!xKq", "Jane", "Doe", "1995-03-22")
        self.assertGreater(without_ctx["score"], with_ctx["score"])

    def test_strong_password_no_context(self):
        result = estimate_strength("c!Xk9@Lm#Qz7wP$nR2v")
        self.assertEqual(result["label"], "strong")

    def test_weak_password_no_context(self):
        result = estimate_strength("abc")
        self.assertEqual(result["label"], "weak")


if __name__ == "__main__":
    unittest.main()
