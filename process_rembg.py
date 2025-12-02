from rembg import remove
from PIL import Image
import os
import io

source_image_path = r"C:/Users/eivin/.gemini/antigravity/brain/41681b52-c10b-4250-9f32-49139faff657/uploaded_image_1764615927978.png"
output_dir = r"c:/Users/eivin/Documents/GitHub/husks-jackpot-bar/Media/Drawings"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def process_images():
    print("Loading image...")
    with open(source_image_path, 'rb') as i:
        input_data = i.read()
    
    print("Removing background with rembg...")
    output_data = remove(input_data)
    img = Image.open(io.BytesIO(output_data))
    
    # Save the full image for debugging
    full_out_path = os.path.join(output_dir, "full_no_bg.png")
    img.save(full_out_path)
    print(f"Saved full background-removed image to {full_out_path}")

    width, height = img.size # Fixed: Define width and height

    # Simple vertical projection to find gaps
    # Array of boolean: is this column empty?
    is_column_empty = []
    for x in range(width):
        empty = True
        for y in range(height):
            if img.getpixel((x, y))[3] > 0:
                empty = False
                break
        is_column_empty.append(empty)
        
    # Find segments
    segments = []
    in_segment = False
    start_x = 0
    
    for x in range(width):
        if not is_column_empty[x] and not in_segment:
            in_segment = True
            start_x = x
        elif is_column_empty[x] and in_segment:
            in_segment = False
            segments.append((start_x, x))
            
    if in_segment:
        segments.append((start_x, width))
        
    print(f"Found {len(segments)} segments initially.")
    for i, s in enumerate(segments):
        print(f"Segment {i}: width {s[1]-s[0]}")
    
    # Filter small noise segments (e.g. < 20px width)
    valid_segments = [s for s in segments if (s[1] - s[0]) > 20]
    print(f"Segments after filtering: {len(valid_segments)}")
    
    drinks = [
        "Velvette.png",
        "Vox.png",
        "Valentino.png",
        "SirPentious.png",
        "Cherri.png",
        "Lucifer.png"
    ]
    
    use_fallback = False
    if len(valid_segments) != 6:
        print(f"Warning: Expected 6 segments, found {len(valid_segments)}. Using fallback equal split.")
        use_fallback = True
        
    if use_fallback:
        # Fallback: Split the non-transparent area into 6 equal parts
        bbox = img.getbbox()
        if bbox:
            content_width = bbox[2] - bbox[0]
            slice_width = content_width // 6
            start_x = bbox[0]
            valid_segments = []
            for i in range(6):
                l = start_x + (i * slice_width)
                r = start_x + ((i + 1) * slice_width)
                valid_segments.append((l, r))
        else:
            print("Error: Image is completely transparent!")
            return

    for i, seg in enumerate(valid_segments):
        if i < len(drinks):
            # Crop
            # We want to crop to the bounding box of the content in that vertical strip
            strip = img.crop((seg[0], 0, seg[1], height))
            bbox = strip.getbbox()
            if bbox:
                final_img = strip.crop(bbox)
                out_path = os.path.join(output_dir, drinks[i])
                final_img.save(out_path)
                print(f"Saved {drinks[i]}")

if __name__ == "__main__":
    process_images()
