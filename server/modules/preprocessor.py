import cv2
import numpy as np

def fill_transparent_with_white(image):
    img_array = np.array(image)
    if img_array.shape[-1] == 4:
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
        b, g, r, a = cv2.split(img_cv)
        img_bgr = cv2.merge([b, g, r])
        white = np.ones_like(img_bgr, dtype=img_bgr.dtype) * 255
        alpha_mask = a / 255.0
        blended = (img_bgr * alpha_mask[:, :, np.newaxis] + white * (1 - alpha_mask)[:, :, np.newaxis])
        return blended.astype(np.uint8)
    else:
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
def save_video_frames(video_path: str, split_count: int):
    cap = cv2.VideoCapture(video_path)

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

        for i, j in enumerate(frame_nums):
            cap.set(cv2.CAP_PROP_POS_FRAMES, j)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(f"output_frame_{i}.jpg", frame)
            else:
                print("Error: Unable to save image to the specified path")
    
    cap.release()
    cv2.destroyAllWindows()
    return