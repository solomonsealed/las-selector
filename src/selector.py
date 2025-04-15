import pandas as pd
import laspy
import numpy as np
from pathlib import Path
from laspy import ScaleAwarePointRecord

def select(index_csv, chunks_dir, bbox, output_path):
    """
    bbox: (min_x, min_y, max_x, max_y)
    """
    min_x, min_y, max_x, max_y = bbox

    # Step 1: Load metadata
    df = pd.read_csv(index_csv)

    # Step 2: Find overlapping tiles
    def overlaps(row):
        return not (
            row['max_x'] < min_x or row['min_x'] > max_x or
            row['max_y'] < min_y or row['min_y'] > max_y
        )

    overlapping = df[df.apply(overlaps, axis=1)]

    if overlapping.empty:
        print("⚠️ No overlapping tiles found.")
        return

    print(f"🔍 Found {len(overlapping)} overlapping tile(s).")

    # Step 3: Combine points from each file
    all_point_arrays = []
    first_header = None

    for _, row in overlapping.iterrows():
        las_path = Path(chunks_dir) / row['filename']
        las = laspy.read(las_path)

        # Filter points to exact bbox
        mask = (
            (las.x >= min_x) & (las.x <= max_x) &
            (las.y >= min_y) & (las.y <= max_y)
        )
        if mask.sum() == 0:
            continue

        if first_header is None:
            first_header = las.header

        all_point_arrays.append(las.points.array[mask])

    # Step 4: Merge and write
    if all_point_arrays:
        merged_array = np.concatenate(all_point_arrays)

        # Convert to ScaleAwarePointRecord using correct point format and scales
        point_record = ScaleAwarePointRecord(
            merged_array,
            point_format=first_header.point_format,
            scales=first_header.scales,
            offsets=first_header.offsets
        )

        # Create output LAS and assign points
        merged_las = laspy.LasData(first_header)
        merged_las.points = point_record
        merged_las.write(output_path)
        print(f"✅ Merged LAS saved to {output_path}")
    else:
        print("⚠️ No points found in selected area.")

