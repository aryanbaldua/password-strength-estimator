"""
AI Password Strength Estimator

takes a password + personal info and returns a score, label, and feedback
"""

import math
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

# pull basic stats out of the password itself
def extract_features(password):
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


# check if the password contains the user's name or birthday
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
            # invalid birthday format, skip all birthday checks
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


# add points for good properties, subtract for bad ones, clamp to 0-100
def score_rules(features):
    score = 0

    # length is the biggest factor — cap at 30 points
    length = features.get('length', 0)
    score += min(length * 1.5, 30)

    # bonus for hitting common length targets
    if length >= 12:
        score += 10
    if length >= 16:
        score += 5

    # character variety
    if features.get('num_lower', 0) > 0:
        score += 10
    if features.get('num_upper', 0) > 0:
        score += 10
    if features.get('num_digits', 0) > 0:
        score += 10
    if features.get('num_symbols', 0) > 0:
        score += 10

    # reward high uniqueness
    if features.get('unique_ratio', 0) > 0.7:
        score += 15

    # penalize common patterns
    if features.get('has_dictionary_word', False):
        score -= 15
    if features.get('has_sequence', False):
        score -= 10
    if features.get('ends_with_year', False):
        score -= 5

    # penalize repeated characters
    max_run = features.get('max_run_length', 0)
    if max_run >= 3:
        score -= 5
    if max_run >= 5:
        score -= 5

    # penalize low variety overall
    if features.get('unique_ratio', 1) < 0.4:
        score -= 10

    # penalize name usage
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

    # penalize birthday usage — combos are worse than individual parts
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


# map a numeric score to a human-readable label
def label_from_score(score):
    if score <= 60:
        return "weak"
    elif score <= 80:
        return "ok"
    else:
        return "strong"


# build a short list of suggestions based on what went wrong
def generate_feedback(features):
    feedback = []

    length = features.get('length', 0)
    if length < 8:
        feedback.append("Use at least 8 characters (12+ is even better).")
    elif length < 12:
        feedback.append("Try making your password 12+ characters for extra strength.")

    # collect which character types are missing
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

    # name and birthday feedback
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

    if not feedback:
        feedback.append("Great password! No obvious weaknesses detected.")

    # cap at 4 suggestions so the output stays readable
    return feedback[:4]


# how many points to subtract for personal info — kept separate from score_rules
# so estimate_strength() can apply it on top of the ML base score
def personal_info_penalty(features):
    penalty = 0

    has_first = features.get('contains_first_name', False)
    has_last = features.get('contains_last_name', False)
    has_full = features.get('contains_full_name', False)
    has_fragment = features.get('contains_name_fragment', False)

    if has_first:
        penalty += 20
    if has_last:
        penalty += 20
    if has_full:
        penalty += 10
    elif has_fragment and not has_first and not has_last:
        penalty += 10

    has_combo = features.get('contains_birth_combo', False)
    has_year = features.get('contains_birth_year', False)
    has_year_2d = features.get('contains_birth_year_2digit', False)

    if has_combo:
        penalty += 25
    elif has_year:
        penalty += 10
    elif has_year_2d:
        penalty += 5

    return penalty


ML_FEATURE_KEYS = [
    "length", "num_lower", "num_upper", "num_digits", "num_symbols",
    "num_unique_chars", "unique_ratio", "max_run_length",
    "has_sequence", "has_dictionary_word", "ends_with_year",
]

SCALER_MEAN = [9.4353, 2.6196, 2.6043, 0.9965, 3.2149, 8.944, 0.9563, 1.0858, 0.005, 0.0, 0.0]
SCALER_STD = [4.0164, 1.7687, 1.7462, 1.0333, 2.0146, 3.7102, 0.0667, 0.2822, 0.0705, 1.0, 1.0]

# logistic regression weights extracted from training — rows are weak, ok, strong
_COEFS = [
    [-4.6000, -3.0783, -2.8685, -1.6197, -3.1512, -5.8392, 0.6689, 0.2465, 0.0746, 0.0, 0.0],
    [2.9390, 1.7470, 1.7059, 1.2377, 2.2122, -0.3610, 0.1021, -0.1164, 0.0370, 0.0, 0.0],
    [1.6610, 1.3313, 1.1627, 0.3820, 0.9390, 6.2003, -0.7710, -0.1301, -0.1116, 0.0, 0.0],
]
_INTERCEPTS = [-15.6016, 7.7061, 7.8955]
ML_LABEL_MAP = {0: "weak", 1: "ok", 2: "strong"}


# run the embedded logistic regression and return a label + per-class probabilities
def predict_ml(features):
    raw = []
    for key in ML_FEATURE_KEYS:
        val = features.get(key, 0)
        if isinstance(val, bool):
            val = int(val)
        raw.append(float(val))

    # scale each feature to mean=0, std=1 using training set stats
    scaled = [(raw[i] - SCALER_MEAN[i]) / SCALER_STD[i] for i in range(len(raw))]

    # compute one logit per class
    logits = []
    for c in range(3):
        logit = _INTERCEPTS[c]
        for i in range(len(scaled)):
            logit += _COEFS[c][i] * scaled[i]
        logits.append(logit)

    # softmax — subtract max first to avoid overflow
    max_logit = max(logits)
    exps = [math.exp(l - max_logit) for l in logits]
    total = sum(exps)
    probs = [e / total for e in exps]

    predicted_class = probs.index(max(probs))

    return ML_LABEL_MAP[predicted_class], {
        "weak": round(probs[0], 4),
        "ok": round(probs[1], 4),
        "strong": round(probs[2], 4),
    }


# rule-based pipeline only — used for testing and comparison
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


# midpoint of each label band, used to convert ML label to a number
# weak: 0-60 → 30, ok: 61-80 → 70, strong: 81-100 → 90
_ML_BASE_SCORE = {"weak": 30, "ok": 70, "strong": 90}


# main entry point — ML sets the base score, rules apply personal info penalty on top
def estimate_strength(password, first_name="", last_name="", birthday=""):
    pw_features = extract_features(password)
    personal_features = extract_personal_info_features(
        password, first_name, last_name, birthday
    )
    all_features = {**pw_features, **personal_features}

    # ML judges password structure — generalizes better than pure rules
    ml_label, _ = predict_ml(pw_features)
    base_score = _ML_BASE_SCORE[ml_label]

    # personal info can only lower the score, never raise it
    penalty = personal_info_penalty(all_features)
    final_score = int(max(0, min(100, base_score - penalty)))

    label = label_from_score(final_score)
    feedback = generate_feedback(all_features)

    return {
        "score": final_score,
        "label": label,
        "feedback": feedback,
    }


if __name__ == "__main__":
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
        result = estimate_strength(
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
