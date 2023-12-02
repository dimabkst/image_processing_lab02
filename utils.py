from typing import List, Tuple, Union
from custom_types import ListImage, FilterKernel
from numpy import array, clip, uint8
from numpy.random import normal
from PIL import Image
from constants import MIN_INTENSITY, MAX_INTENSITY
    
def validateFilterKernelSize(filter_kernel: FilterKernel):
    rows_count = len(filter_kernel)

    if (rows_count % 2 == 0):
        raise Exception('Filter kernel has inappropriate size')
    
    cols_count = len(filter_kernel[0])

    for row in filter_kernel:
        if (len(row) != cols_count):
            raise Exception('Filter kernel has inappropriate size')
        
        if (len(row) % 2 == 0):
            raise Exception('Filter kernel has inappropriate size')
        
def validateFilterKernel(filter_kernel: FilterKernel):
    validateFilterKernelSize(filter_kernel)

    kernel_sum = sum([sum(filter_kernel[row]) for row in range(len(filter_kernel))])

    if kernel_sum != 1:
        raise Exception('Filter kernel has inappropriate elements')

def generateGaussianNoise(mean: float=0.0, std_dev: float=1.0, size:Union[Tuple[int, int], None]=None) -> List:
    return normal(mean, std_dev, size).tolist()

def convertToProperImage(image: List[List[float]]) -> ListImage:
    # Convert values to int and limit them to min_intensity, max_intensity

    return clip(image, MIN_INTENSITY, MAX_INTENSITY).astype(uint8).tolist()

def convertToListImage(image: Image.Image) -> ListImage:
    # In getpixel((x, y)) x - column, y - row 
    return [[image.getpixel((j, i)) for j in range(image.width)] for i in range(image.height)]

def convertToPillowImage(image: ListImage) -> Image.Image:
    return Image.fromarray(array(image, dtype=uint8), mode='L')

def saveImage(image: Image.Image, path: str) -> None:
    return image.save(path, mode='L')