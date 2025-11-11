import cv2
import numpy as np
from PIL import Image
import os, io

def fill_transparent_with_white(image: Image):
    img_array = np.array(image.convert('RGBA')) if image.mode != 'RGB' else np.array(image.convert('RGB'))

    if img_array.shape[-1] == 4:
        r, g, b, a = cv2.split(img_array)
        img_rgb = cv2.merge([r, g, b])
        white = np.ones_like(img_rgb, dtype=img_rgb.dtype) * 255
        alpha_mask = a / 255.0
        blended = (img_rgb * alpha_mask[:, :, np.newaxis] + white * (1 - alpha_mask)[:, :, np.newaxis])
        return blended.astype(np.uint8)
    else:
        return np.array(image.convert('RGB'))
    
def get_video_frames(video_file: bytes, split_count: int):
    with open("output.mp4", "wb") as f:
        f.write(video_file)

    cap = cv2.VideoCapture("output.mp4")

    if not cap.isOpened():
        print("Error: Unable to open video at the specified path")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames < split_count:
            frame_nums = [total_frames // 2]
        else:
            frame_nums = []
            split_interval = total_frames // (split_count + 1)
            for i in range(split_count):
                frame_nums.append((i + 1) * split_interval)

        frames = []

        for i in frame_nums:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = cap.read()
            if success:
                frames.append(Image.fromarray(frame, 'RGB'))
            else:
                raise PermissionError("Unable to save image to the specified path")
    
    cap.release()
    cv2.destroyAllWindows()
    os.remove("output.mp4")

    return frames

def bytestream_to_img(img_file: bytes):
    file = io.BytesIO(img_file)
    return Image.open(file)

# def img_to_bytestream(image):
#     success, buffer = cv2.imencode(".jpg", image)
#     if success:
#         return buffer.tobytes()
#     else:
#         raise BufferError("Failed to buffer image into bytestream.")
