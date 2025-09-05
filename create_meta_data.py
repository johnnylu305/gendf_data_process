from pathlib import Path
import json
import os
from datetime import datetime
from PIL import Image  # pip install pillow

# ===== User config =====
ROOT_DATASET_DIR = f"./310525-OliveOil"   # Parent folder containing scene folders like "040625-LundoBin"
OUTPUT_JSON_PATH = f"./{ROOT_DATASET_DIR}/meta.json"
DEFAULT_ENVIRONMENT = "unknown"
# ========================

IMG_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}

def parse_scene_id(scene_folder_name: str):
    """
    '040625-LundoBin' -> ('040625', 'LundoBin', '2025-06-04')
    Raises ValueError if the folder name does not match expected pattern.
    """
    parts = scene_folder_name.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) == 6:
        date_raw = parts[0]
        name = parts[1]
        try:
            dt = datetime.strptime(date_raw, "%d%m%y").date().isoformat()
        except Exception as e:
            raise ValueError(f"Invalid date format in scene folder '{scene_folder_name}': {e}")
        return date_raw, name, dt
    raise ValueError(
        f"Scene folder '{scene_folder_name}' is not in expected format 'ddMMyy-SceneName'."
    )

def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMG_EXTS

def build_scene(scene_dir: Path, root: Path):
    date_raw, scene_name, date_iso = parse_scene_id(scene_dir.name)

    clean_data = None
    clutter_data = None
    total_images = 0
    scene_wh = None  # (w, h) for the whole scene

    for sf in sorted([p for p in scene_dir.iterdir() if p.is_dir()]):
        low = sf.name.lower()
        if "-All" in str(sf):
            continue
        sf = sf / "images"            # keep as Path
        
        if not sf.exists():
            continue                        # or: raise FileNotFoundError(img_dir)

        # collect images
        abs_imgs = [p for p in sorted(sf.iterdir()) if p.is_file() and is_image(p)]
        imgs = [str(p.relative_to(root)) for p in abs_imgs]
        total_images += len(imgs)

        # infer resolution from the first image in this subfolder (assume all are same size)
        if abs_imgs:
            with Image.open(abs_imgs[0]) as im:
                w, h = im.size
            if scene_wh is None:
                scene_wh = (w, h)
            else:
                if (w, h) != scene_wh:
                    raise ValueError(
                        f"Resolution mismatch in scene '{scene_dir.name}': "
                        f"expected {scene_wh[0]}x{scene_wh[1]}, got {w}x{h} in '{sf.name}'."
                    )

        # build entry with metadata first
        entry = {
            "folder": str(sf.relative_to(root)),
            "count": len(imgs),
        }
        
        print(low)

        if low.endswith("-clean"):
            entry["theme"] = ["oil"]  
            # apple, bag, bike bell, beer, bench, bread, brush, bin, box, bike, bikes, building, bridge, cathedral, candle, can, cake, cutlery cup, coffee, cone, container, cylinder, cup, decoration, detergent, display, drawer, drink, drawing, dish, eardrop, flower, fruit, glass bottle, grass pot
            # grinder, hallway, heater, intersection, jar, juice, kettle, lamp, light pole, oil, power transformer, pot, pack, package, plush toy, pole, plant, platform, plate, rice pack, rice cooker, rock, sauce, snail, spice, stool, shop, sign, soy sauce
            # table, tea cup, toy, toaster, umbrella, vitamin water, vegetables, water bottle, water fountain, window
            entry["images"] = imgs    # put images at the end
            clean_data = entry
        elif low.endswith("-clutter"):
            entry["distractors"] = ["key", "hand"] 
            # arm, bag, bike, bird, bus, candy, can, candle chopsticks, cup, dog, eyedrop, fan, feet, hand, human, key, knife, leaf, leg, lollipop, lighter, light rail,
            # necklace, mat, motorbike, mouse, orange, package, pencil, phone, plastic bag, plane, plate, scissor, spoon, spice, scarf trimmer, soy sauce, tube, tissue, umbrella
            # vegetable, rope, tape, tag, toy, watch, wet wipe
            entry["images"] = imgs
            clutter_data = entry        

    if scene_wh is None:
        raise ValueError(f"No images found under scene '{scene_dir.name}'.")

    res_str = f"{scene_wh[0]}x{scene_wh[1]}"

    return {
        "scene_id": scene_dir.name,
        "scene_name": scene_name,
        "scene_date_raw": date_raw,
        "scene_date_iso": date_iso,
        "mode": "face_forward",       # face_forward, 360_degree, unknown
        "orientation": "portrait",   # landscape, portrait
        "device": "iPhone 15",        # iPhone 15, Galaxy A15, iPad Air (5th generation), OPPO A17
        "resolution": res_str,
        "region": " Denmark",          # Australia, Denmark, Japan, Taiwan
        "time_of_day": "unknown",     # daytime, nighttime, unknown
        "environment": "indoor",     # indoor, outdoor
        "environment_fine": "studio", # bedroom, cathedral, courtyard, cafe, garden, hallway, hotel, restaurant, park, parking lot, living room, studio, shop, street, super market, station, kitchen
        "root_folder": str(root),
        "total_images": total_images,
        "clean": clean_data,
        "clutter": clutter_data,
    }

def main():
    root = Path(ROOT_DATASET_DIR)
    if not root.exists():
        print(f"[ERROR] ROOT_DATASET_DIR not found: {root}")
        return

    #scene_dirs = sorted([p for p in root.iterdir() if p.is_dir()])

    #scenes = [build_scene(sd, root) for sd in scene_dirs]

    scenes = [build_scene(root, root)]

    manifest = {
        "version": "simple-1.0",
        "meta_generated_at": datetime.now().isoformat(timespec="seconds"),
        **scenes[0],
    }


    out = Path(OUTPUT_JSON_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Wrote manifest to {out.resolve()}")

if __name__ == "__main__":
    main()

