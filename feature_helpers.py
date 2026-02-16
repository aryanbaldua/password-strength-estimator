import re


# find longest run of identical consecutive chars
def compute_max_run_length(password: str) -> int:
    if not password:
        return 0
    
    max_len = 1
    current_len = 1
    
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            current_len += 1
            max_len = max(max_len, current_len)
        else:
            current_len = 1
    
    return max_len


#  check for common sequential patterns
def has_sequence(password: str) -> bool:
    sequences = [
        "abcdefghijklmnopqrstuvwxyz",
        "zyxwvutsrqponmlkjihgfedcba",
        "0123456789",
        "9876543210",
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm",
    ]
    
    password_lower = password.lower()
    
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i:i+3] in password_lower:
                return True
    
    return False


# check if it contains common dictionary words
def has_dictionary_word(password: str) -> bool:
    common_words = {
        "password", "pass", "admin", "user", "test", "demo", "login",
        "hello", "world", "welcome", "secret", "dragon", "monkey",
        "baseball", "football", "soccer", "love", "money", "freedom",
        "master", "shadow", "sunshine", "rainbow",
    }
    
    password_lower = password.lower()
    
    for word in common_words:
        if word in password_lower:
            return True
    
    return False


# check if password ends with a recent year
def ends_with_year(password: str) -> bool:
    match = re.search(r'\d{4}$', password)
    
    if match:
        year = int(match.group(0))
        if 1900 <= year <= 2099:
            return True
    
    return False


# lowercase and remove separators in a string
def normalize_string(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[\s\-_.]+', '', s)
    return s


# check for fragment of name
def contains_name_fragment(password_norm: str, first_name_norm: str, last_name_norm: str) -> bool:
    names = [first_name_norm, last_name_norm]
    
    for name in names:
        if len(name) < 3:
            continue
        
        for fragment_len in [3, 4]:
            for i in range(len(name) - fragment_len + 1):
                fragment = name[i:i+fragment_len]
                if fragment in password_norm:
                    return True
    
    return False


# check for any birthday related info
def contains_birth_combo(password: str, month: str, day: str, year: str, year_2digit: str) -> bool:
    combos = [
        month + day,
        day + month,
        year + month + day,
        month + day + year_2digit,
        day + month + year_2digit,
    ]
    
    for combo in combos:
        if combo in password:
            return True
    
    return False
