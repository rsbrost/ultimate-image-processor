import os
import cv2


def get_gray_from_color(input_dir, output_dir, debug=False):
    num_total = len(os.listdir(input_dir))
    num_processed = 0

    input_names = os.listdir(input_dir)
    output_names = os.listdir(output_dir)

    for img_name in input_names:
        if img_name in output_names:
            continue
        image_path = os.path.join(input_dir, img_name)
        image = cv2.imread(image_path)

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(output_dir, img_name), gray_image)

        num_processed += 1

    if debug is True:
        print(f"{num_processed} images grayified out of {num_total} total images.")
        print(f"{num_total - num_processed} images were filtered out.")

    return num_processed
