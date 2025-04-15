from chunker import chunk
from selector import select

def main():
    # chunk(6)
    # bbox = (491250, 5458250, 491750, 5458750)  # (min_x, min_y, max_x, max_y)
    bbox = (491000.0, 5458000.0, 491999.999, 5458999.999)

    select(
        index_csv="../resources/chunks/index.csv",
        chunks_dir="../resources/chunks",
        bbox=bbox,
        output_path="../resources/output/selected_area2.las"
    )


if __name__ == "__main__":
    main()