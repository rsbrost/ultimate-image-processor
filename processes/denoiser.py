import os
import cv2
import time
import math


def fast_denoise(input_dir, output_dir, only_once=False, debug=False):
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

        st = time.time()

        median_blur = cv2.medianBlur(img, 5)
        gaussian_blur = cv2.GaussianBlur(median_blur, (3, 3), 0)

        et = time.time()
        elapsed = et - st

        path = os.path.join(output_dir, img_name)
        cv2.imwrite(path, gaussian_blur)
        num_processed += 1

        times.append(elapsed)

        if only_once is True:
            break
        
        if debug is True:
            print(f"{num_processed} color input images moderate denoised and saved out of {num_total} total images. {num_total - num_processed} images were filtered out.")
            print(f"This was performed in {sum(times)}s with an average of {math.ceil(sum(times) / len(times) * 100) / 100}s per image.")
            print()

    return num_processed


def moderate_denoise(input_dir, output_dir, strength=5, only_once=False, debug=False):
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

        st = time.time()

        denoised_image = cv2.fastNlMeansDenoising(img, None, h=strength, templateWindowSize=7, searchWindowSize=10)
        median_blur = cv2.medianBlur(denoised_image, 3)

        et = time.time()
        elapsed = et - st

        path = os.path.join(output_dir, img_name)
        cv2.imwrite(path, median_blur)
        num_processed += 1

        times.append(elapsed)

        if only_once is True:
            break

    if debug is True:
        print(f"{num_processed} color input images moderate denoised and saved out of {num_total} total images. {num_total - num_processed} images were filtered out.")
        print(f"This was performed in {sum(times)}s with an average of {math.ceil(sum(times) / len(times) * 100) / 100}s per image.")
        print()

    return num_processed


def optimal_denoise(input_dir, output_dir, strength=6, only_once=False, debug=False):
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

        st = time.time()
        denoised_image = cv2.fastNlMeansDenoising(img, None, h=strength, templateWindowSize=7, searchWindowSize=21)
        # median_blur = cv2.medianBlur(img, 5)
        et = time.time()
        elapsed = et - st

        path = os.path.join(output_dir, img_name)
        cv2.imwrite(path, denoised_image)
        num_processed += 1

        times.append(elapsed)

        if only_once is True:
            break

    if debug is True:
        print(f"{num_processed} color input images optimal denoised and saved out of {num_total} total images. {num_total - num_processed} images were filtered out.")
        print(f"This was performed in {sum(times)}s with an average of {math.ceil(sum(times) / len(times) * 100) / 100}s per image.")
        print()

    return num_processed