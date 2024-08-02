import os
import cv2
import time


def get_gray_from_color(input_dir, output_dir, debug=False, overwrite=False):
    num_total = len(os.listdir(input_dir))
    num_processed = 0

    input_names = os.listdir(input_dir)
    output_names = os.listdir(output_dir)

    for img_name in input_names:
        if img_name in output_names and overwrite is False:
            continue
        image_path = os.path.join(input_dir, img_name)
        image = cv2.imread(image_path)

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(output_dir, img_name), gray_image)

        num_processed += 1

        print(f"\rGrayifying progress: {num_processed}/{num_total}", end="")
    print()

    if debug is True:
        print(f"{num_processed} images grayified out of {num_total} total images.")
        print(f"{num_total - num_processed} images were filtered out.")

    return num_processed


def run_get_gray(dm, overwrite=False):
    # set up the input and output directories
    dm.current_input_dir = dm.current_output_dir
    input_dir = dm.current_output_dir
    output_dir = dm.set_output_dir('gray')

    # now run
    st = time.time()
    num_processed = get_gray_from_color(input_dir, output_dir, overwrite)
    et = time.time() - st
    if num_processed != 0:
        print("{} images flattened in {}spi".format(num_processed, et / num_processed))
