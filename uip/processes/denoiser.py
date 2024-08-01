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
            print(f"{num_processed} images fast denoised and saved out of {num_total} total images.")
            print(f"{num_total - num_processed} images were filtered out.")
            print(f"Done in {sum(times)}s with an average of {math.ceil(sum(times) / len(times) * 100) / 100}s per image.")
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
        print(f"{num_processed} images moderate denoised and saved out of {num_total} total images.")
        print(f"{num_total - num_processed} images were filtered out.")
        print(f"Done in {sum(times)}s with an average of {math.ceil(sum(times) / len(times) * 100) / 100}s per image.")
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
        print(f"{num_processed} images optimal denoised and saved out of {num_total} total images.")
        print(f"{num_total - num_processed} images were filtered out.")
        print(f"Done in {sum(times)}s with an average of {math.ceil(sum(times) / len(times) * 100) / 100}s per image.")
        print()

    return num_processed


# dm stands for directory manager
def run_denoise(dm, fast=False, moderate=False, optimal=False, only_once=False):
    if fast is False and moderate is False and optimal is False:
        assert False, "Must select one or more denoising protocols to run."

    input_dir = dm.input_dir
    denoise_base_output_dir = dm.set_output_dir('denoise')

    num_processed = 0

    if fast is True:
        fast_dn_output_dir = dm.set_output_dir('fast', base_output_dir=denoise_base_output_dir)
        # fast denoise our input images
        fast_num_processed = 0
        st = time.time()
        fast_num_processed += fast_denoise(input_dir, fast_dn_output_dir, only_once=only_once)
        et = time.time() - st
        if fast_num_processed != 0:
            print("{} images fast denoised in {}spi \n\n".format(fast_num_processed, et / fast_num_processed))

        num_processed += fast_num_processed

    if moderate is True:
        moderate_dn_output_dir = dm.set_output_dir('moderate', base_output_dir=denoise_base_output_dir)
        # moderate denoise
        moderate_num_processed = 0
        st = time.time()
        moderate_num_processed += moderate_denoise(input_dir, moderate_dn_output_dir, only_once=only_once)
        et = time.time() - st
        if moderate_num_processed != 0:
            print("{} images moderate denoised in {}spi \n\n".format(moderate_num_processed, et / moderate_num_processed))

        num_processed += moderate_num_processed

    if optimal is True:
        optimal_dn_output_dir = dm.set_output_dir('optimal', base_output_dir=denoise_base_output_dir)
        # optimal denoise
        optimal_num_processed = 0
        st = time.time()
        optimal_num_processed += optimal_denoise(input_dir, optimal_dn_output_dir, only_once=only_once)
        et = time.time() - st
        if optimal_num_processed != 0:
            print("{} images optimal denoised in {}spi \n\n".format(optimal_num_processed, et / optimal_num_processed))

        num_processed += optimal_num_processed

    return num_processed
