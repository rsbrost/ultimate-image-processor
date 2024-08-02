import cv2
import numpy as np
import os
import time


def remove_vignette(image, flatfield, max_background_value: int = 241):
    image_no_vignette = image / flatfield * cv2.mean(flatfield)[:-1]
    image_no_vignette[image_no_vignette > max_background_value] = max_background_value
    return np.asarray(image_no_vignette, dtype=np.uint8)


def flatten(input_dir, flatfield_img, output_dir, overwrite):
    num_total = len(os.listdir(input_dir))
    num_processed = 0
    # times = []

    input_names = os.listdir(input_dir)
    output_names = os.listdir(output_dir)

    for img_name in input_names:
        if img_name in output_names and overwrite is False:
            continue
        path = os.path.join(input_dir, img_name)
        img = cv2.imread(path)

        flat_img = remove_vignette(img, flatfield_img)

        cv2.imwrite(os.path.join(output_dir, img_name), flat_img)
        num_processed += 1

        print(f"\rFlattened progress: {num_processed}/{num_total}", end="")
    print()

    return num_processed


def run_flatten(dm, overwrite=False):
    # open the flatfield image
    num_flatfield_inputs = len(os.listdir(dm.flatfield_dir))
    assert num_flatfield_inputs == 1, f"{num_flatfield_inputs} flatfield inputs detected. Must have 1 in uip/Flatfield."
    flatfield_name = os.listdir(dm.flatfield_dir)[0]
    flatfield_img = cv2.imread(os.path.join(dm.flatfield_dir, flatfield_name))

    # set up the input and ouput directories.
    dm.current_input_dir = dm.current_output_dir
    input_dir = dm.current_input_dir
    output_dir = dm.set_output_dir('flattened')

    # now run
    st = time.time()
    num_processed = flatten(input_dir, flatfield_img, output_dir, overwrite=overwrite)
    et = time.time() - st
    if num_processed != 0:
        print("{} images flattened in {}spi".format(num_processed, et / num_processed))
