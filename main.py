"""
AI Password Strength Estimator

1. Extract features from the user info and the password

"""

from datetime import datetime
from feature_helpers import (
    compute_max_run_length,
    has_sequence,
    has_dictionary_word,
    ends_with_year,
    normalize_string,
    contains_name_fragment,
    contains_birth_combo,
)

# extact password strength features like length, types of chars, and other patterns
def extract_features(password: str):
    features = {}
    
    features['length'] = len(password)
    features['num_lower'] = sum(1 for c in password if c.islower())
    features['num_upper'] = sum(1 for c in password if c.isupper())
    features['num_digits'] = sum(1 for c in password if c.isdigit())
    features['num_symbols'] = sum(1 for c in password if not c.isalnum())
    
    unique_chars = set(password)
    features['num_unique_chars'] = len(unique_chars)
    features['unique_ratio'] = features['num_unique_chars'] / max(1, features['length'])
    
    features['max_run_length'] = compute_max_run_length(password)
    features['has_sequence'] = has_sequence(password)
    features['has_dictionary_word'] = has_dictionary_word(password)
    features['ends_with_year'] = ends_with_year(password)
    
    return features

# extract features related to the personal user info entered 
def extract_personal_info_features(password, first_name, last_name, birthday):
    features = {}
    
    password_normalized = normalize_string(password)
    first_name_norm = normalize_string(first_name)
    last_name_norm = normalize_string(last_name)
    
    features['contains_first_name'] = (
        first_name_norm != "" and first_name_norm in password_normalized
    )
    features['contains_last_name'] = (
        last_name_norm != "" and last_name_norm in password_normalized
    )
    features['contains_full_name'] = (
        first_name_norm != "" and last_name_norm != "" and
        (first_name_norm + last_name_norm) in password_normalized
    )
    features['contains_name_fragment'] = contains_name_fragment(
        password_normalized, first_name_norm, last_name_norm
    )
    
    if birthday:
        try:
            birth_date = datetime.strptime(birthday, "%Y-%m-%d")
            
            year = str(birth_date.year)
            year_2digit = str(birth_date.year)[2:]
            month = f"{birth_date.month:02d}"
            day = f"{birth_date.day:02d}"
            
            features['contains_birth_year'] = year in password
            features['contains_birth_year_2digit'] = year_2digit in password
            features['contains_birth_month'] = month in password
            features['contains_birth_day'] = day in password
            features['contains_birth_combo'] = contains_birth_combo(
                password, month, day, year, year_2digit
            )
        except ValueError:
            features['contains_birth_year'] = False
            features['contains_birth_year_2digit'] = False
            features['contains_birth_month'] = False
            features['contains_birth_day'] = False
            features['contains_birth_combo'] = False
    else:
        features['contains_birth_year'] = False
        features['contains_birth_year_2digit'] = False
        features['contains_birth_month'] = False
        features['contains_birth_day'] = False
        features['contains_birth_combo'] = False
    
    return features
