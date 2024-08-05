import imageio.v3 as iio
import skimage as ski
from findpeaks import findpeaks
import numpy as np
import os
import cv2
from scipy import stats
import time
import copy


def get_gray_peak(img_path):
    img = iio.imread(img_path, mode="L")
    img = ski.util.img_as_float(img)

    histogram, bin_edges = np.histogram(img, bins=256, range=(0, 1))

    fp = findpeaks(lookahead=1, verbose=0)

    results = fp.fit(histogram)
    df = results['df']

    max_idx = df.loc[df['y'].idxmax()]

    max_peak_df = df.loc[df['labx'] == max_idx['labx']]

    return max_peak_df


def get_std_gray(img_path):
    df = get_gray_peak(img_path)
    std = df.std()['y']

    try:
        max_y = df.loc[df['y'].idxmax()]['y']
    except Exception:
        return None

    num_stds = 10
    std_range = max_y - std * num_stds

    in_range = df.loc[df['y'] >= std_range]

    return in_range


def normalize_gray_img_background(img_path, output_dir, set_background_pix):
    img = iio.imread(img_path, mode="L")

    # vals, counts = np.unique(img, return_counts=True)
    # mode_idx = np.argwhere(counts == np.max(counts))
    # mode = vals[mode_idx].flatten().tolist()[0]

    in_range_df = get_std_gray(img_path)
    if in_range_df is None:
        print("image: {} skipped.".format(os.path.basename(img_path)))
        return 0

    background_pix_vals = in_range_df['x'].to_list()
    mode_pix = in_range_df.loc[in_range_df['y'].idxmax()]['x']

    for val in background_pix_vals:
        if set_background_pix is None:
            img[img == val] = mode_pix
        else:
            img[img == val] = set_background_pix

    img_name = os.path.basename(img_path)
    path = os.path.join(output_dir, img_name)
    cv2.imwrite(path, img)

    return 1


def normalize_gray(input_dir, output_dir, overwrite=False, set_background_pix=None, only_once=False):
    num_processed = 0
    num_total = len(os.listdir(input_dir))

    input_names = os.listdir(input_dir)
    output_names = os.listdir(output_dir)

    for img_name in input_names:
        name = img_name
        if set_background_pix == 0:
            img_name = "BLACK TEST IMG 10 " + img_name
        if img_name in output_names and overwrite is False:
            continue
        path = os.path.join(input_dir, name)
        num_processed = num_processed + normalize_gray_img_background(path, output_dir, set_background_pix)

        print(f"\rNormalize gray progress: {num_processed}/{num_total}", end="")
        if only_once is True:
            break
    print()

    print("{} gray input images normalized and saved out of {} total images. {} images were filtered out."
          .format(num_processed, num_total, num_total - num_processed))

    return num_processed

######################################################################################


def get_color_peaks(img):
    # vals, counts = np.unique(img, return_counts=True)
    # mode_idx = np.argwhere(counts == np.max(counts))
    # mode = vals[mode_idx].flatten().tolist()[0]

    colors = ("red", "green", "blue")
    max_peaks = []

    # Consider forcing a range that the max peaks must lie within,
    # a range of possible background pixel values to omit non normalized images.
    for channel_id, color in enumerate(colors):
        vals, counts = np.unique(img[:, :, channel_id], return_counts=True)
        # mode_idx = np.argwhere(counts == np.max(counts))
        # print(mode_idx, " is the mode for ", channel_id)

        histogram, bin_edges = np.histogram(img[:, :, channel_id], bins=256, range=(0, 256))

        fp = findpeaks(lookahead=1, verbose=0)

        results = fp.fit(histogram)
        df = results['df']
        max_idx = df.loc[df['y'].idxmax()]
        max_peak_df = df.loc[df['labx'] == max_idx['labx']]

        max_y = df.loc[df['y'].idxmax()]['y']
        std = max_peak_df.std()['y']
        num_stds = 10
        std_range = max_y - std * num_stds
        in_range = max_peak_df.loc[max_peak_df['y'] >= std_range]

        max_peaks.append(in_range)

    return max_peaks


def optimal_normalize_all_channels(image_path, gray_img_path, max_peaks, output_dir, set_background_pix=None):
    img = cv2.imread(image_path)

    gray_img = cv2.imread(gray_img_path)
    if gray_img is None:
        print(f"gray_img is None for path {gray_img_path}")
        return 0
    flattened_gray = gray_img.flatten()
    gray_mode = stats.mode(flattened_gray)[0]

    background_pix_values = []
    mode_pixels = []
    for i in range(3):
        background_pix_values.append(max_peaks[i]['x'].to_list())
        if max_peaks[i].empty:
            print("image: {} skipped because of color ambiguity.".format(os.path.basename(image_path)))
            return 0

        mode_pixels.append(max_peaks[i].loc[max_peaks[i]['y'].idxmax()]['x'])

    for i in range(3):
        for c in background_pix_values[i]:
            if set_background_pix is None:
                img[:, :, i:i + 1][img[:, :, i:i + 1] == c] = mode_pixels[i]
                img[:, :, i:i + 1][gray_img[:, :, i:i + 1] == gray_mode] = mode_pixels[i]
            else:
                img[:, :, i:i + 1][img[:, :, i:i + 1] == c] = set_background_pix
                img[:, :, i:i + 1][gray_img[:, :, i:i + 1] == gray_mode] = set_background_pix

    img_name = os.path.basename(image_path)
    path = os.path.join(output_dir, img_name)

    # imwrite messes up how some paths save, so must convert path str to literal
    raw_path = r'{}'.format(path)
    cv2.imwrite(raw_path, img)

    return 1


def moderate_normalize_color(image_path, gray_img_path, max_peaks, output_dir, set_background_pix=None):
    img = cv2.imread(image_path)

    gray_img = cv2.imread(gray_img_path)
    if gray_img is None:
        return 0
    flattened_gray = gray_img.flatten()
    gray_mode = stats.mode(flattened_gray)[0]

    background_pix_values = []
    mode_pixels = []
    for i in range(3):
        background_pix_values.append(max_peaks[i]['x'].to_list())
        if max_peaks[i].empty:
            print("image: {} skipped because of color ambiguity.".format(os.path.basename(image_path)))
            return 0

        mode_pixels.append(max_peaks[i].loc[max_peaks[i]['y'].idxmax()]['x'])

    for i in range(3):
        if set_background_pix is None:
            img[:, :, i:i + 1][gray_img[:, :, i:i + 1] == gray_mode] = mode_pixels[i]
        else:
            img[:, :, i:i + 1][gray_img[:, :, i:i + 1] == gray_mode] = set_background_pix

    img_name = os.path.basename(image_path)
    if set_background_pix is None:
        path = os.path.join(output_dir, img_name)
    else:
        path = os.path.join(output_dir, "BLACK TEST IMG 10 " + img_name)

    # imwrite messes up how some paths save, so must convert path str to literal
    raw_path = r'{}'.format(path)
    cv2.imwrite(raw_path, img)

    return 1


def fast_normalize_color(image_path, output_dir, normalized_output_dir):
    try:
        img = cv2.imread(image_path)

        img_name = os.path.basename(image_path)
        path1 = os.path.join(output_dir, img_name)
        path2 = os.path.join(normalized_output_dir, img_name)

        ret, thresh = cv2.threshold(img, 140, 255, cv2.THRESH_TOZERO)
        cv2.imwrite(path1, thresh)

        img_normalized = cv2.normalize(thresh, None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        cv2.imwrite(path2, img_normalized)

        return 1
    except Exception:
        return 0


def normalize_color(input_dir, gray_norm_dir, output_dir, version='optimal', overwrite=True,
                    set_background_pix=None, only_once=False):
    num_processed = 0
    num_total = len(os.listdir(input_dir))

    input_names = os.listdir(input_dir)
    output_names = os.listdir(output_dir)

    for img_name in input_names:
        name = img_name
        if img_name in output_names and overwrite is False:
            continue
        path = os.path.join(input_dir, name)

        if version == 'fast':
            num_processed = num_processed + fast_normalize_color(path, gray_norm_dir, output_dir)
            continue

        gray_norm_img = os.path.join(gray_norm_dir, img_name)
        req_img = cv2.imread(gray_norm_img)
        if req_img is None:
            continue

        img = cv2.imread(path)

        gray_path = os.path.join(gray_norm_dir, img_name)

        in_ranges = get_color_peaks(img)

        for i in range(3):
            if in_ranges[i] is None:
                print("image: {} skipped because of color ambiguity.".format(img_name))
                continue

        # colors = ("red", "green", "blue")

        # normalize_all_channels(path, in_ranges)
        if version == 'optimal':
            # takes about 2.2s
            num_processed = num_processed + optimal_normalize_all_channels(path,
                                                                           gray_path,
                                                                           in_ranges,
                                                                           output_dir,
                                                                           set_background_pix)
        elif version == 'moderate':
            # takes about 1.5s
            num_processed = num_processed + moderate_normalize_color(path,
                                                                     gray_path,
                                                                     in_ranges,
                                                                     output_dir,
                                                                     set_background_pix)
        else:
            assert False, version + " not a version for color normalization."

        if only_once is True:
            break

    print("{} images normalized and saved out of {} total images with {} version. {} images were filtered out."
          .format(num_processed, num_total, version, num_total - num_processed))

    return num_processed


def run_normalize_gray(dm, overwrite=False, debug=False, only_once=False):
    # set up the input and output directories
    dm.gray_input_dir = dm.current_output_dir
    dm.current_input_dir = dm.current_output_dir
    input_dir = dm.current_input_dir

    base_output_dir = dm.set_output_dir('normalized')
    output_dir = dm.set_output_dir('gray', base_output_dir=base_output_dir)

    if debug is True:
        print(f"input dir in run normalize gray is: {input_dir}")
        print(f"output dir in run normalize gray is: {output_dir}")

        # set up debug output dir
        debug_output_dir = dm.set_output_dir('debug_gray', base_output_dir=base_output_dir)
        # now run
        st = time.time()
        num_processed = normalize_gray(input_dir, debug_output_dir, overwrite=overwrite, set_background_pix=0, only_once=only_once)
        et = time.time() - st
        if num_processed != 0:
            print("{} debug gray images normalized in {}spi".format(num_processed, et / num_processed))

    # now run
    st = time.time()
    num_processed = normalize_gray(input_dir, output_dir, overwrite=overwrite)
    et = time.time() - st
    if num_processed != 0:
        print("{} gray images normalized in {}spi".format(num_processed, et / num_processed))


def run_normalize_color(dm, version='optimal', overwrite=False, debug=False, only_once=False):
    # set up important directories first
    color_input_dir = copy.deepcopy(dm.current_input_dir)  # these are the denoised/flattened color images

    # run normalize gray
    run_normalize_gray(dm, overwrite=overwrite, debug=debug, only_once=only_once)

    # set up the input and output directories
    gray_input_dir = dm.current_output_dir  # these are the normalized grey images
    base_output_dir = dm.set_output_dir('normalized')
    output_dir = dm.set_output_dir('color', base_output_dir=base_output_dir)

    if debug is True:
        print(f"color input dir in run normalize color is: {color_input_dir}")
        print(f"base output dir in run normalize color is: {base_output_dir}")
        print(f"gray input dir in run normalize color is: {gray_input_dir}")
        print(f"output dir in run normalize color is: {output_dir}")

        # set up debug output dir
        debug_output_dir = dm.set_output_dir('debug_color', base_output_dir=base_output_dir)
        print(f"debug_output_dir is: {debug_output_dir}")
        print()

        # now run
        st = time.time()
        num_processed = normalize_color(color_input_dir, gray_input_dir, debug_output_dir, version,
                                        overwrite=overwrite, set_background_pix=0, only_once=only_once)
        et = time.time() - st
        if num_processed != 0:
            print("{} debug color images normalized in {}spi".format(num_processed, et / num_processed))

    else:
        # now run
        st = time.time()
        num_processed = normalize_color(color_input_dir, gray_input_dir, output_dir, version=version,
                                        overwrite=overwrite, only_once=only_once)
        et = time.time() - st
        if num_processed != 0:
            print("{} color images normalized in {}spi".format(num_processed, et / num_processed))
