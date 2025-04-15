import laspy
import numpy as np
from pathlib import Path
import csv

def chunker():
    las = laspy.read("../resources/las/491000_5458000.las")

    # Get bounds
    min_x, max_x = las.x.min(), las.x.max()
    min_y, max_y = las.y.min(), las.y.max()

    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    # Create masks for each quadrant
    mask_NE = (las.x >= mid_x) & (las.y >= mid_y)
    mask_NW = (las.x < mid_x) & (las.y >= mid_y)
    mask_SE = (las.x >= mid_x) & (las.y < mid_y)
    mask_SW = (las.x < mid_x) & (las.y < mid_y)

    # Output directory
    output_dir = "../resources/chunks"
    Path(output_dir).mkdir(exist_ok=True)

    metadata = []

    # Collect metadata from each quadrant
    for mask in [mask_NE, mask_NW, mask_SE, mask_SW]:
        result = write_quadrant(las, output_dir, mask)
        if result:
            metadata.append(result)

    # Save metadata as CSV
    csv_path = Path(output_dir) / "index.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["filename", "min_x", "min_y", "max_x", "max_y", "num_points"])
        writer.writeheader()
        writer.writerows(metadata)

    print(f"📝 Metadata saved to {csv_path}")



def write_quadrant(las, base_path, mask):
    if mask.sum() == 0:
        print("⚠️ Skipping empty tile")
        return None

    points = las.points[mask]
    new_las = laspy.LasData(las.header)
    new_las.points = points

    min_x, max_x = las.x[mask].min(), las.x[mask].max()
    min_y, max_y = las.y[mask].min(), las.y[mask].max()
    num_points = mask.sum()

    filename = f"tile_{int(min_x)}_{int(min_y)}_{int(max_x)}_{int(max_y)}.las"
    filepath = f"{base_path}/{filename}"
    new_las.write(filepath)

    print(f"✅ Saved {filename} with {num_points} points")

    return {
        "filename": filename,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "num_points": num_points
    }