import cv2
import numpy as np
import os


def remove_vignette(image, flatfield, max_background_value: int = 241):
    image_no_vignette = image / flatfield * cv2.mean(flatfield)[:-1]
    image_no_vignette[image_no_vignette > max_background_value] = max_background_value
    return np.asarray(image_no_vignette, dtype=np.uint8)

def flatten(input_dir, flatfield_img, output_dir):
    num_total = len(os.listdir(input_dir))
    num_processed = 0
    times = []
    
    input_names = os.listdir(input_dir)
    output_names = os.listdir(output_dir)

    for img_name in input_names:
        if img_name in output_names:
            continue
        path = os.path.join(input_dir, img_name)
        img = cv2.imread(path)

        flat_img = remove_vignette(img, flatfield_img)

        cv2.imwrite(os.path.join(output_dir, img_name), flat_img)
        num_processed += 1
    
    return num_processed