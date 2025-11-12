import json
from pathlib import Path
import argparse

def main():
    ap = argparse.ArgumentParser(description="Check split.json for correct train/test keyword usage")
    ap.add_argument("scene_dir", help="Path to the scene folder containing split.json")
    ap.add_argument("--train-keyword", default="clutter")
    ap.add_argument("--test-keyword", default="extra")
    args = ap.parse_args()

    split_path = Path(args.scene_dir) / "split.json"
    if not split_path.is_file():
        raise FileNotFoundError(f"split.json not found at {split_path}")

    data = json.loads(split_path.read_text())
    train_list = data.get("train", [])
    test_list = data.get("test", [])

    wrong_train = [n for n in train_list if args.train_keyword not in n]
    wrong_test = [n for n in test_list if args.test_keyword not in n]

    print(f"[INFO] Checking split.json: {split_path}")
    print(f"  Train images: {len(train_list)}, Test images: {len(test_list)}")
    if wrong_train:
        print(f"  ⚠️  {len(wrong_train)} train entries missing '{args.train_keyword}':")
        for n in wrong_train[:10]:
            print(f"    - {n}")
        if len(wrong_train) > 10:
            print(f"    ... (+{len(wrong_train)-10} more)")

    if wrong_test:
        print(f"  ⚠️  {len(wrong_test)} test entries missing '{args.test_keyword}':")
        for n in wrong_test[:10]:
            print(f"    - {n}")
        if len(wrong_test) > 10:
            print(f"    ... (+{len(wrong_test)-10} more)")

    if not wrong_train and not wrong_test:
        print("✅ All train/test entries follow the expected keyword pattern.")

if __name__ == "__main__":
    main()
