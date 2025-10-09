from pathlib import Path
import json
import os
from datetime import datetime
from PIL import Image  # pip install pillow

# ===== User config =====
ROOT_DATASET_DIR = f"./310825-TownhallTree"   # Parent folder containing scene folders like "040625-LundoBin"
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
            entry["theme"] = ["tree"]
            # apple, bag, bike bell, beer, bench, bread, brush, bin, box, bike, bikes, building, bridge, cathedral, candle, can, car, cake, cutlery cup, clothes, coffee, cane, cone, comb, container, cylinder, cup, cross light, counter, daily objects, decoration, detergent, display, drawer, drink, drawing, dish, eardrop, entrance, fan, flower, fruit, gate, glass bottle, grass pot
            # grinder, hallway, heater, headphone, intersection, jar, juice, kettle, kitchen lamp, light pole, massage gun, mug, nouse, oil, orange, power transformer, pot, power bank, pack, package, plush toy, pillow, pole, plant, platform, plate, razor, rice pack, rice cooker, rock, sauce, snail, spice, stool, shop, sign, soy sauce, soup
            # sqare, safe, seat, scissor, scale, speaker, spray, table, tree, tea cup, toy, toaster, tube, umbrella, vitamin water, vegetables, wallet, watch, water bottle, water fountain, window
            entry["images"] = imgs    # put images at the end
            clean_data = entry
        elif low.endswith("-clutter"):
            entry["distractors"] = ["bird", "car", "human"] 
            # arm, bag, bike, bird, bus, box, candy, can, cane, car, candle, cloth, chopsticks, cup, charger, comb, chair, dog, disk, eyedrop, fan, feet, hand, human, key, jar, knife, leaf, leg, lollipop, lighter, light rail,
            # mat, motorbike, mouse, necklace, orange, package, pencil, phone, plastic bag, plane, plate, pillow, razor, scissor, spoon, spice, scarf trimmer, soy sauce, tube, tissue, truck, umbrella
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
        "orientation": "landscape",   # landscape, portrait
        "device": "iPhone 15",        # iPhone 15, Galaxy A15, iPad Air (5th generation), OPPO A17
        "resolution": res_str,
        "region": " Australia",          # Australia, Denmark, Japan, Taiwan
        "time_of_day": "nighttime",     # daytime, nighttime, unknown
        "environment": "outdoor",     # indoor, outdoor
        "environment_fine": "street" , # bedroom, cathedral, courtyard, cafe, garden, gym, hallway, hotel, restaurant, park, parking lot, living room, studio, shop, street, super market, station, kitchen
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

