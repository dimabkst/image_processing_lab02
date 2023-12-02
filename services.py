from typing import Tuple
from custom_types import EVSet, ListImage, FloatOrNone, FilterKernel, ImageFunction, ListImageWindow
from math import log10
from constants import MAX_NUMBER_OF_INTENSITY_LEVELS
from utils import generateGaussianNoise, convertToProperImage

def getMean(image: ListImage) -> float:
    N = len(image)
    M = len(image[0])

    mean = sum([sum([image[i][j] for j in range(M)]) for i in range(N)]) / (N * M)

    return mean

def getVariance(image: ListImage, mean: FloatOrNone=None) -> float:
    N = len(image)
    M = len(image[0])

    mean = mean if mean is not None else getMean(image)

    variance = sum([sum([(image[i][j] - mean) ** 2 for j in range(M)]) for i in range(N)]) / (N * M)

    return variance

def getStandardDeviation(image: ListImage, mean: FloatOrNone=None, variance: FloatOrNone=None) -> float:
    variance = variance if variance is not None else getVariance(image, mean)

    standard_deviation = variance ** 0.5

    return standard_deviation

def getMSE(image1: ListImage, image2: ListImage) -> float:
    N = len(image1)
    M = len(image1[0])

    MSE = sum([sum([(image1[i][j] - image2[i][j]) ** 2 for j in range(M)]) for i in range(N)]) / (N * M)

    return MSE

def getRMSE(image1: ListImage, image2: ListImage, MSE: FloatOrNone=None) -> float:
    MSE = MSE if MSE is not None else getMSE(image1, image2)
        
    RMSE = MSE ** 0.5

    return RMSE

def getPSNR(image1: ListImage, image2: ListImage, MSE: FloatOrNone=None, RMSE: FloatOrNone=None) -> float:
    L = MAX_NUMBER_OF_INTENSITY_LEVELS

    RMSE = RMSE if RMSE is not None else getRMSE(image1, image2, MSE)

    PSNR = (20 * log10((L - 1) / RMSE))

    return PSNR

def addGaussianAdditiveNoise(image: ListImage, std_dev_coef: float) -> ListImage:
    N = len(image)
    M = len(image[0])

    mean = getMean(image)

    standart_deviation = getStandardDeviation(image, mean)

    noise = generateGaussianNoise(mean, std_dev_coef * standart_deviation, (N, M))

    noisy_image = [[image[i][j] + noise[i][j] - mean for j in range(M)] for i in range(N)]

    return convertToProperImage(noisy_image)

def createFilterKernel(weights: FilterKernel) -> FilterKernel:
    filter_kernel = weights

    filter_kernel_sum = sum([sum(filter_kernel[row]) for row in range(len(filter_kernel))])

    if filter_kernel_sum != 1:
        filter_kernel = [[el / filter_kernel_sum for el in row] for row in filter_kernel]

    return filter_kernel

def getMirroredImageFunction(image: ListImage, filter_kernel_sizes: Tuple[int, int]) -> ImageFunction:
    N = len(image)
    M = len(image[0])
    
    extension_sizes = tuple(size // 2 for size in filter_kernel_sizes)

    def mirroredImageFunction(i: int, j: int) -> int:
        if i >= N + extension_sizes[0]:
            raise KeyError
        elif i < 0:
            ii = -i
        elif i >= N:
            ii = N - 1 - (i - N + 1)
        else:
            ii = i

        if j >= M + extension_sizes[1]:
            raise KeyError
        elif j < 0:
            jj = -j
        elif j >= M:
            jj = M - 1 - (j - M + 1)
        else:
            jj = j

        return image[ii][jj]

    return mirroredImageFunction

def getMirroredImage(image: ListImage, filter_kernel_sizes: Tuple[int, int]) -> ListImage:
    N = len(image)
    M = len(image[0])
    
    extension_sizes = tuple(size // 2 for size in filter_kernel_sizes)

    mirrored_image = []

    mirroredImageFunction = getMirroredImageFunction(image, filter_kernel_sizes)

    for i in range(-extension_sizes[0], N + extension_sizes[0]):
        mirrored_image.append([])

        for j in range(-extension_sizes[1], M + extension_sizes[1]):
            mirrored_image[-1].append(mirroredImageFunction(i, j))

    return mirrored_image

def linearSpatialFiltering(image: ListImage, filter_kernel: FilterKernel) -> ListImage:
    N = len(image)
    M = len(image[0])

    filter_kernel_sizes = (len(filter_kernel), len(filter_kernel[0]))

    extended_image_function = getMirroredImageFunction(image, filter_kernel_sizes)

    a = filter_kernel_sizes[0] // 2 # equal to (filterKernelSizes[0] - 1) / 2 in formula
    b = filter_kernel_sizes[1] // 2

    filtered_image = [[sum([sum([filter_kernel[a + s][b + t] * extended_image_function(i + s, j + t) for t in range(-b, b + 1)]) for s in range(-a, a + 1)]) for j in range(M)] for i in range(N)]

    return convertToProperImage(filtered_image)

def getEVSet(window: ListImageWindow, pixel_of_interest: int, ev: float) -> EVSet:
    window_elements = []

    for row in window:
        for el in row:
            window_elements.append(el)

    EV = [el for el in window_elements if abs(pixel_of_interest - el) <= ev]

    return EV

def getEVSetMean(EV: EVSet) -> float:
    return sum(EV) / len(EV)

def rankOrderEVMeanFiltering(image: ListImage, filter_window_sizes: Tuple[int, int], ev: float) -> ListImage:
    N = len(image)
    M = len(image[0])

    extended_image_function = getMirroredImageFunction(image, filter_window_sizes)

    a = filter_window_sizes[0] // 2
    b = filter_window_sizes[1] // 2

    filtered_image = [[getEVSetMean(getEVSet([[extended_image_function(i + s, j + t) for t in range(-b, b + 1)] for s in range(-a, a + 1)], image[i][j], ev)) for j in range(M)] for i in range(N)]

    return convertToProperImage(filtered_image)