#!/usr/bin/env python3
import json, sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ====== EDIT THIS ======
BASE_DIR = Path("./")
# =======================

def load_frames_count(json_path: Path) -> int:
    try:
        with json_path.open("r") as f:
            data = json.load(f)
        frames = data.get("frames", [])
        return len(frames)
    except Exception:
        return 0

# collect all scenes under BASE_DIR that have *-All with the jsons
records = []
for scene_all in BASE_DIR.rglob("*-All"):
    scene = scene_all.parent.name  # e.g., 090625-TUCCookie
    for kind in ["transforms.json", "transforms_clutter.json", "transforms_extra.json"]:
        p = scene_all / kind
        if p.exists():
            n = load_frames_count(p)
            records.append({"scene": scene, "kind": kind.replace(".json",""), "frames": n})

if not records:
    sys.exit("No transforms*.json found. Check BASE_DIR.")

df = pd.DataFrame(records)

def plot_kind(kind: str):
    d = df[df["kind"] == kind].copy()
    if d.empty:
        print(f"[warn] no {kind} found")
        return
    d = d.sort_values("frames", ascending=False)

    plt.figure(figsize=(28,6))
    bars = plt.bar(d["scene"], d["frames"])
    plt.title(f"Number of frames per scene — {kind}")
    plt.xlabel("Scene")
    plt.ylabel("Frames")
    plt.xticks(rotation=90, ha="right", fontsize=6)

    # annotate each bar with frame count
    for bar, frame in zip(bars, d["frames"]):
        plt.text(
            bar.get_x() + bar.get_width()/2,  # x position (center of bar)
            bar.get_height() + 2,             # y position (slightly above bar)
            str(frame),                       # text
            ha="center", va="bottom", fontsize=6, rotation=90
        )
    plt.margins(x=0.001) 
    plt.tight_layout()

for k in ["transforms", "transforms_clutter", "transforms_extra"]:
    plot_kind(k)

# also save a tidy CSV for reference
out_csv = BASE_DIR / "frame_counts_by_scene.csv"
df.sort_values(["kind","frames"], ascending=[True, False]).to_csv(out_csv, index=False)
print(f"Saved CSV: {out_csv}")

plt.show()

