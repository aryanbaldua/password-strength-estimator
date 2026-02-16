# unit tests for password feature extraction

import unittest
from main import extract_features, extract_personal_info_features


# test password feature extraction
class TestExtractFeatures(unittest.TestCase):

    def test_basic_length(self):
        features = extract_features("abc123")
        self.assertEqual(features['length'], 6)
    
    def test_character_counts(self):
        features = extract_features("Ab1!")
        self.assertEqual(features['num_lower'], 1)
        self.assertEqual(features['num_upper'], 1)
        self.assertEqual(features['num_digits'], 1)
        self.assertEqual(features['num_symbols'], 1)
    
    def test_unique_chars(self):
        features = extract_features("aabbcc")
        self.assertEqual(features['num_unique_chars'], 3)
        self.assertAlmostEqual(features['unique_ratio'], 0.5)
    
    def test_max_run_length(self):
        features = extract_features("aaabbaaa")
        self.assertEqual(features['max_run_length'], 3)
    
    def test_sequence_detection(self):
        features = extract_features("password123")
        self.assertTrue(features['has_sequence'])
        
        features = extract_features("xyz789")
        self.assertTrue(features['has_sequence'])
    
    def test_dictionary_word(self):
        features = extract_features("mypassword123")
        self.assertTrue(features['has_dictionary_word'])
        
        features = extract_features("xY9zQw2kL")
        self.assertFalse(features['has_dictionary_word'])
    
    def test_ends_with_year(self):
        features = extract_features("MyPass1990")
        self.assertTrue(features['ends_with_year'])
        
        features = extract_features("Pass2025")
        self.assertTrue(features['ends_with_year'])
        
        features = extract_features("Pass1850")
        self.assertFalse(features['ends_with_year'])
    

# test personal information feature extraction
class TestExtractPersonalInfoFeatures(unittest.TestCase):

    def test_contains_first_name(self):
        features = extract_personal_info_features(
            "John2025", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_first_name'])
    
    def test_contains_last_name(self):
        features = extract_personal_info_features(
            "Smith1990", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_last_name'])
    
    def test_contains_full_name(self):
        features = extract_personal_info_features(
            "JohnSmith2025", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_full_name'])
    
    def test_contains_name_fragment(self):
        features = extract_personal_info_features(
            "JohnX", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_name_fragment'])
    
    def test_contains_birth_year(self):
        features = extract_personal_info_features(
            "Pass1990", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_year'])
    
    def test_contains_birth_year_2digit(self):
        features = extract_personal_info_features(
            "Pass90X", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_year_2digit'])
    
    def test_contains_birth_month(self):
        features = extract_personal_info_features(
            "Pass05", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_month'])
    
    def test_contains_birth_day(self):
        features = extract_personal_info_features(
            "Pass15", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_day'])
    
    def test_contains_birth_combo(self):
        features = extract_personal_info_features(
            "Pass0515", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_birth_combo'])
    
    def test_case_insensitive_name_match(self):
        features = extract_personal_info_features(
            "JOHN2025", "John", "Smith", "1990-05-15"
        )
        self.assertTrue(features['contains_first_name'])
    
    def test_invalid_birthday_format(self):
        features = extract_personal_info_features(
            "SomePass", "John", "Smith", "invalid"
        )
        self.assertFalse(features['contains_birth_year'])
        self.assertFalse(features['contains_birth_combo'])
    
    def test_empty_birthday(self):
        features = extract_personal_info_features(
            "SomePass", "John", "Smith", ""
        )
        self.assertFalse(features['contains_birth_year'])


# test edge cases
class TestEdgeCases(unittest.TestCase):

    # check empty password
    def test_empty_password(self):
        features = extract_features("")
        self.assertEqual(features['length'], 0)
        self.assertEqual(features['max_run_length'], 0)
    
    # check single character password
    def test_single_character_password(self):
        features = extract_features("a")
        self.assertEqual(features['length'], 1)
        self.assertEqual(features['num_unique_chars'], 1)
    
    # check with empty first and last names
    def test_empty_names(self):
        features = extract_personal_info_features(
            "Password123", "", "", "1990-05-15"
        )
        self.assertFalse(features['contains_first_name'])
        self.assertFalse(features['contains_last_name'])
        self.assertFalse(features['contains_full_name'])


if __name__ == "__main__":
    unittest.main()
