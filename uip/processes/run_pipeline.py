import uip
import os
import time


def run_pipeline(input_dir="input", output_dir="ouput", flatfield_dir="flatfield", overwrite=True):
    st = time.time()
    # set up the directory manager
    dm = uip.DirectoryManager(input_dir=input_dir, output_dir=output_dir, flatfield_dir=flatfield_dir)

    num_total = len(os.listdir(dm.base_input_dir))

    uip.run_denoise(dm, optimal=True, overwrite=overwrite)

    num_flatfield_inputs = len(os.listdir(dm.flatfield_dir))
    if num_flatfield_inputs == 1:
        uip.run_flatten(dm, overwrite=overwrite)
    else:
        print(f"Flattening/removing vignette: skipped since not 1 but {num_flatfield_inputs} flatfield inputs found.\n")

    uip.run_get_gray(dm, overwrite=overwrite)

    uip.run_normalize_color(dm, overwrite=overwrite)

    num_processed = uip.make_masks(dm)

    et = round((time.time() - st), 3)
    spi = round((et / num_processed), 3)
    if num_processed > 0:
        print(f"{num_processed}/{num_total} images fully processed and masks generated in {et}"
              + f" at a rate of {spi} seconds per image.")
