import glob
import os
import tempfile
import cv2

frames_dir = os.path.join(tempfile.gettempdir(), "walk_frames")
frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.jpg")))
if not frame_files:
    raise RuntimeError(f"No frames found in {frames_dir}")

first = cv2.imread(frame_files[0])
if first is None:
    raise RuntimeError(f"Failed to read first frame: {frame_files[0]}")

h, w = first.shape[:2]
out_path = r"C:\Users\Habib\Desktop\شقتي\Zedan_Apartment_3D_Walkthrough.mp4"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(out_path, fourcc, 15.0, (w, h))
if not writer.isOpened():
    raise RuntimeError("Could not open VideoWriter with mp4v")

count = 0
for fp in frame_files:
    img = cv2.imread(fp)
    if img is None:
        raise RuntimeError(f"Corrupt frame: {fp}")
    if img.shape[:2] != (h, w):
        img = cv2.resize(img, (w, h))
    writer.write(img)
    count += 1

writer.release()
size_bytes = os.path.getsize(out_path)
print(f"ENCODED {count} FRAMES -> {out_path} ({size_bytes / (1024 * 1024):.2f} MB)")
if size_bytes < 100 * 1024:
    raise RuntimeError(f"Output MP4 unexpectedly small: {size_bytes} bytes")
