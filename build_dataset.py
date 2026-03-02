import csv
import random
from main import extract_features

INPUT_FILE = "dataset_raw.csv"
TRAIN_FILE = "dataset_train.csv"
VAL_FILE = "dataset_val.csv"
TEST_FILE = "dataset_test.csv"

SEED = 42

FEATURE_COLS = [
    "length", "num_lower", "num_upper", "num_digits", "num_symbols",
    "num_unique_chars", "unique_ratio", "max_run_length",
    "has_sequence", "has_dictionary_word", "ends_with_year",
]


def load_and_extract(input_path):
    rows = []
    seen = set()  

    with open(input_path, "r", errors="replace") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            password = row.get("Password", row.get("password", ""))
            raw_label = row.get("Strength", row.get("strength", ""))

            label_map = {"Weak": "0", "Medium": "1", "Strong": "2"}
            label = label_map.get(raw_label, raw_label)

            if password in seen:
                continue
            seen.add(password)

            if not password.strip():
                continue
            if label not in ("0", "1", "2"):
                continue

            features = extract_features(password)
            rows.append((features, label))

    print(f"  total unique passwords: {len(rows)}")
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FEATURE_COLS + ["label"])

        for features, label in rows:
            row = []
            for col in FEATURE_COLS:
                val = features[col]
                if isinstance(val, bool):
                    val = int(val)
                row.append(val)
            row.append(label)
            writer.writerow(row)


def main():
    rows = load_and_extract(INPUT_FILE)

    random.seed(SEED)
    random.shuffle(rows)

    # 80/10/10 split
    n = len(rows)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    train = rows[:train_end]
    val = rows[train_end:val_end]
    test = rows[val_end:]


    for name, split in [("train", train), ("val", val), ("test", test)]:
        counts = {}
        for _, label in split:
            counts[label] = counts.get(label, 0) + 1
        print(f"   {name} labels: {counts}")

    print("Writing CSVs...")
    write_csv(TRAIN_FILE, train)
    write_csv(VAL_FILE, val)
    write_csv(TEST_FILE, test)

    print(f"Done! Files: {TRAIN_FILE}, {VAL_FILE}, {TEST_FILE}")


if __name__ == "__main__":
    main()
