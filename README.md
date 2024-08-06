# ultimate-image-processor

## Intro

Ultimate image processing package used for optimizing images of 2D nanomaterials and generating essential inputs for machine learning applications; however, many of the features and functionalities included here can generally improve image quality, segment distinct sections of images, and optimize inputs for machine learning applications.

### Install

1. Use git to clone this repository into your computer.

2. Open a terminal or anaconda prompt window. Navigate to the pyscan folder, which contains the file "setup.py".

3. Install pyscan with

```
pip install -e .
```
>Note: The ideal run order for the processes in my scenario (as implemented in uip/run.ipynb) is:
>1. Denoise
>2. (Optional) Flatten
>3. Generate Gray Images
>4. Normalize Gray Images
>5. Normalize Color Images
>6. Generate Masks

## Contribute

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Alternatively, you can create your own fork and tailor it to your use cases.

**Current development team:**
- Ryan Brost rsbrost@sandia.gov

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Citing ultimate-image-processor

If ultimate-image-processor contributes to a project that leads to publication, please acknowledge this using:

"Part of this work was enabled by the use of ultimate-image-processor (github.com/sandialabs/ultimate-image-processor), an image processing software (designed for use in machine learning applications) made available by the Center for Integrated Nanotechnologies, an Office of Science User Facility operated for the U.S. Department of Energy."