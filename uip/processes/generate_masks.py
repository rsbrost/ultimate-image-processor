import numpy as np
import os
import cv2
from scipy.stats.mstats import mode


def get_mode(gray_img):
    # get the background value
    vals, counts = np.unique(gray_img, return_counts=True)
    mode_idx = np.argwhere(counts == np.max(counts))
    mode = vals[mode_idx].flatten().tolist()[0]
    return mode


def thresh(gray_img, min_area=60):
    mode = get_mode(gray_img)

    # threshold above and below the mode (background) value then combine
    _, lower_thresh1 = cv2.threshold(gray_img, mode + 3, 255, cv2.THRESH_BINARY)
    _, upper_thresh2 = cv2.threshold(gray_img, 235, 255, cv2.THRESH_BINARY_INV)
    thresholded_image1 = cv2.bitwise_and(lower_thresh1, upper_thresh2)

    _, lower_thresh2 = cv2.threshold(gray_img, 20, 255, cv2.THRESH_BINARY)
    _, upper_thresh2 = cv2.threshold(gray_img, mode - 3, 255, cv2.THRESH_BINARY_INV)
    thresholded_image2 = cv2.bitwise_and(lower_thresh2, upper_thresh2)

    thresholded_image = cv2.bitwise_or(thresholded_image1, thresholded_image2)

    # erode lightly to clean up edges
    kernel_size = 3
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    eroded_image = cv2.erode(thresholded_image, kernel, iterations=1)

    # filter out the segments that do not meet the minimum area set here
    contours, hierarchy = cv2.findContours(eroded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area]
    filtered_mask = np.zeros_like(thresholded_image)
    # null = cv2.drawContours(filtered_mask, filtered_contours, -1, color=255, thickness=cv2.FILLED)

    # can smooth the edges. Not testing this now...
    # smoothed_image = cv2.bilateralFilter(filtered_mask, d=9, sigmaColor=150, sigmaSpace=150)

    return filtered_mask


def add_edges(gray_img, filtered_mask, min_area1=7, min_area2=100, max_area=5000):
    mode = get_mode(gray_img)

    # Apply automatic thresholding
    sigma = 0.03
    base_sensitivity = .1 + sigma
    lower = int(max(0, (base_sensitivity - sigma) * mode))
    upper = int(min(255, (base_sensitivity + sigma) * mode))
    # print(lower, upper)

    edges = cv2.Canny(gray_img, lower, upper)
    # edges = cv2.Canny(gray_demo_img, 10, 15)

    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area1]

    mask = np.zeros_like(gray_img)
    # null = cv2.drawContours(mask, filtered_contours, -1, (255,), thickness=2)

    segments_with_lines = filtered_mask.copy()
    segments_with_lines[mask == 255] = 0

    # filter out the segments that do not meet the minimum area set here
    contours, hierarchy = cv2.findContours(segments_with_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area2]
    final_mask = np.zeros_like(filtered_mask)
    # null = cv2.drawContours(final_mask, filtered_contours, -1, color=255, thickness=cv2.FILLED)

    # and now filter the ones that are too large
    contours, hierarchy = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) < max_area]
    final_mask = np.zeros_like(filtered_mask)
    # null = cv2.drawContours(final_mask, filtered_contours, -1, color=255, thickness=cv2.FILLED)

    # final erode for good measure
    kernel_size = 3
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    final_mask = cv2.erode(final_mask, kernel, iterations=1)

    return final_mask


def make_masks(dm):
    input_dir = dm.current_output_dir
    input_names = os.listdir(input_dir)
    input_names.sort()
    num_total = len(input_names)

    output_dir = dm.set_output_dir('semantic_masks')

    num_processed, skipped = 0, 0
    for name in input_names:
        input_path = os.path.join(input_dir, name)
        img = cv2.imread(input_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        filtered_mask = thresh(gray_img)

        final_mask = add_edges(gray_img, filtered_mask)

        # make sure the mask is predominantly black before saving
        # otherwise omit since it is likely confusing foreground with background
        flattened_mask = final_mask.flatten()
        mask_mode = mode(flattened_mask)[0]

        if mask_mode != 0:
            skipped += 1
            continue

        cv2.imwrite(os.path.join(output_dir, name), final_mask)
        num_processed += 1

    print("{} masks produced from {} input images while {} skipped for lacking mode of 0.".format(num_processed,
                                                                                                  num_total, skipped))
