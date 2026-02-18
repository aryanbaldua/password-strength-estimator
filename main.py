"""
AI Password Strength Estimator

1. Extract features from the user info and the password
2. Scoring (Postive points for good features, negative for bad features)
3. Feedback (suggestions to strengthen password based on true features)

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


# compute a 0-100 strength score from the combined feature dict, good features gain points and bad features lose points
def score_rules(features):
    score = 0
    # the good ones

    # length gets + 1.5 per char
    length = features.get('length', 0)
    score += min(length * 1.5, 30)

    # bonuses for longer 
    if length >= 12:
        score += 10
    if length >= 16:
        score += 5

    # character variety (10 each)
    if features.get('num_lower', 0) > 0:
        score += 10
    if features.get('num_upper', 0) > 0:
        score += 10
    if features.get('num_digits', 0) > 0:
        score += 10
    if features.get('num_symbols', 0) > 0:
        score += 10

    # high uniqueness ratio gets 15
    if features.get('unique_ratio', 0) > 0.7:
        score += 15

    # the bad ones

    # common dictionary words
    if features.get('has_dictionary_word', False):
        score -= 15

    # sequential patterns
    if features.get('has_sequence', False):
        score -= 10

    # trailing year
    if features.get('ends_with_year', False):
        score -= 5

    # repeated characters penalty
    max_run = features.get('max_run_length', 0)
    if max_run >= 3:
        score -= 5
    if max_run >= 5:
        score -= 5 

    if features.get('unique_ratio', 1) < 0.4:
        score -= 10

    # personal info penalties

    # name penalties
    has_first = features.get('contains_first_name', False)
    has_last = features.get('contains_last_name', False)
    has_full = features.get('contains_full_name', False)
    has_fragment = features.get('contains_name_fragment', False)

    if has_first:
        score -= 20
    if has_last:
        score -= 20
    if has_full:
        score -= 10 
    elif has_fragment and not has_first and not has_last:
        score -= 10

    # birthday penalties
    has_combo = features.get('contains_birth_combo', False)
    has_year = features.get('contains_birth_year', False)
    has_year_2d = features.get('contains_birth_year_2digit', False)

    if has_combo:
        score -= 25
    elif has_year:
        score -= 10
    elif has_year_2d:
        score -= 5

    score = int(max(0, min(100, score)))
    return score


# score to strength label mapping
def label_from_score(score):
    if score < 40:
        return "weak"
    elif score <= 70:
        return "ok"
    else:
        return "strong"


# generate 2-4 human-readable feedback strings based on detected weaknesses
# prioritizes the most impactful issues so the user knows what to fix first
def generate_feedback(features):
    feedback = []

    # --- Length feedback (most important) ---
    length = features.get('length', 0)
    if length < 8:
        feedback.append("Use at least 8 characters (12+ is even better).")
    elif length < 12:
        feedback.append("Try making your password 12+ characters for extra strength.")

    # --- Character variety ---
    missing_types = []
    if features.get('num_upper', 0) == 0:
        missing_types.append("uppercase letters")
    if features.get('num_lower', 0) == 0:
        missing_types.append("lowercase letters")
    if features.get('num_digits', 0) == 0:
        missing_types.append("digits")
    if features.get('num_symbols', 0) == 0:
        missing_types.append("symbols (e.g. !@#$)")

    if missing_types:
        feedback.append("Add " + ", ".join(missing_types) + " for more variety.")

    # --- Pattern warnings ---
    if features.get('has_dictionary_word', False):
        feedback.append("Avoid common words like 'password', 'admin', or 'login'.")

    if features.get('has_sequence', False):
        feedback.append("Avoid sequences like 'abc', '123', or 'qwerty'.")

    if features.get('ends_with_year', False):
        feedback.append("Avoid ending with a year (e.g. 2024).")

    if features.get('max_run_length', 0) >= 3:
        feedback.append("Avoid repeating the same character many times (e.g. 'aaa').")

    if features.get('unique_ratio', 1) < 0.4:
        feedback.append("Use more varied characters — too many repeats.")

    # --- Personal info warnings ---
    if features.get('contains_full_name', False):
        feedback.append("Your password contains your full name — avoid this.")
    elif features.get('contains_first_name', False) or features.get('contains_last_name', False):
        feedback.append("Your password contains your name — avoid using personal info.")
    elif features.get('contains_name_fragment', False):
        feedback.append("Your password contains part of your name — try something unrelated.")

    if features.get('contains_birth_combo', False):
        feedback.append("Your password includes your birthday — this is easy to guess.")
    elif features.get('contains_birth_year', False):
        feedback.append("Your password contains your birth year — avoid this.")
    elif features.get('contains_birth_year_2digit', False):
        feedback.append("Your password may contain part of your birth year.")

    # if nothing wrong was found, give a positive message
    if not feedback:
        feedback.append("Great password! No obvious weaknesses detected.")

    # cap at 4 messages so the user isn't overwhelmed
    return feedback[:4]


# single entry point that combines everything: features, score, label, feedback
# returns a dict ready for display or JSON output
def estimate_strength_rules(password, first_name="", last_name="", birthday=""):
    pw_features = extract_features(password)
    personal_features = extract_personal_info_features(
        password, first_name, last_name, birthday
    )
    all_features = {**pw_features, **personal_features}

    score = score_rules(all_features)
    label = label_from_score(score)
    feedback = generate_feedback(all_features)

    return {
        "score": score,
        "label": label,
        "feedback": feedback,
    }


# demo: score a few sample passwords with fake user context
# (no real personal info is used or stored)
if __name__ == "__main__":
    # fake context for demo purposes only
    demo_context = {
        "first_name": "Jane",
        "last_name": "Doe",
        "birthday": "1995-03-22",
    }

    sample_passwords = [
        "abc",                          # very short, weak
        "password123",                  # dictionary word + sequence
        "JaneDoe1995",                  # contains personal info
        "Tr0ub4dor&3",                  # mixed chars, moderate length
        "c!Xk9@Lm#Qz7wP$nR2v",        # long, complex, no patterns
    ]

    for pw in sample_passwords:
        result = estimate_strength_rules(
            pw,
            demo_context["first_name"],
            demo_context["last_name"],
            demo_context["birthday"],
        )

        print(f"\nPassword: {pw}")
        print(f"  Score: {result['score']}  Label: {result['label']}")
        print(f"  Feedback:")
        for msg in result["feedback"]:
            print(f"    - {msg}")
