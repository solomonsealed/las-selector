import laspy
import numpy as np
from pathlib import Path
import csv

def chunk(num_divisions=2):
    las = laspy.read("../resources/las/491000_5458000.las")

    # Get bounds
    min_x, max_x = las.x.min(), las.x.max()
    min_y, max_y = las.y.min(), las.y.max()

    # Create grid breakpoints
    x_edges = np.linspace(min_x, max_x, num_divisions + 1)
    y_edges = np.linspace(min_y, max_y, num_divisions + 1)

    # Output directory
    output_dir = "../resources/chunks"
    Path(output_dir).mkdir(exist_ok=True)

    metadata = []

    # Loop through grid tiles
    for i in range(num_divisions):
        for j in range(num_divisions):
            x_min = x_edges[i]
            x_max = x_edges[i + 1]
            y_min = y_edges[j]
            y_max = y_edges[j + 1]

            # Create a mask for points in this tile
            mask = (
                (las.x >= x_min) & (las.x < x_max) &
                (las.y >= y_min) & (las.y < y_max)
            )

            result = write_quadrant(las, output_dir, mask, x_min, y_min, x_max, y_max)
            if result:
                metadata.append(result)

    # Save metadata as CSV
    csv_path = Path(output_dir) / "index.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["filename", "min_x", "min_y", "max_x", "max_y", "num_points"])
        writer.writeheader()
        writer.writerows(metadata)

    print(f"📝 Metadata saved to {csv_path}")

def write_quadrant(las, base_path, mask, min_x, min_y, max_x, max_y):
    if mask.sum() == 0:
        print(f"⚠️ Skipping empty tile {int(min_x)}_{int(min_y)}")
        return None

    points = las.points[mask]
    new_las = laspy.LasData(las.header)
    new_las.points = points

    filename = f"tile_{int(min_x)}_{int(min_y)}_{int(max_x)}_{int(max_y)}.las"
    filepath = f"{base_path}/{filename}"
    new_las.write(filepath)

    print(f"✅ Saved {filename} with {mask.sum()} points")

    return {
        "filename": filename,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "num_points": mask.sum()
    }