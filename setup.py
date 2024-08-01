from setuptools import setup, find_packages

setup(
    name='ultimate_image_processor',
    version='0.1',
    packages=find_packages(),
    description='A simple example package',
    author='Ryan Brost',
    author_email='rsbrost@sandia.gov',
    install_requires=[
        'opencv-python',
        'findpeaks',
        'scikit-image',
        'pathlib',
        'numpy',
        'imageio',
        'scipy',
        'numpy',
        'ipykernel'
    ],
)
