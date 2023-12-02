from os.path import basename, splitext
from traceback import print_exc
from PIL import Image
from constants import COMPUTED_DIRECTORY_NAME
from utils import convertToListImage, convertToPillowImage, saveImage
from services import getMean, getVariance, getStandardDeviation, getRMSE, getPSNR, addGaussianAdditiveNoise, rankOrderEVMeanFiltering

def labTask(image_path: str) -> None:
    computed_directory = f'./{COMPUTED_DIRECTORY_NAME}/'

    file_name_with_extension = basename(image_path)
    file_name, file_extension = splitext(file_name_with_extension)

    with Image.open(image_path) as im:
            image = convertToListImage(im)

            mean = getMean(image)
            variance = getVariance(image, mean)
            standard_deviation = getStandardDeviation(image, mean, variance)

            print(f'Image = {image_path}, mean = {mean}, variance = {variance}, standard deviation = {standard_deviation}.')

            std_dev_coefs = [0.2]

            noisy_images = [addGaussianAdditiveNoise(image, std_dev_coef) for std_dev_coef in std_dev_coefs]

            noisy_RMSEs = [getRMSE(image, noisy_image) for noisy_image in noisy_images]
            noisy_PSNRs = [getPSNR(image, noisy_images[i], noisy_RMSEs[i]) for i in range(len(noisy_images))]

            filter_window_sizes = [(3, 3)]

            ev = standard_deviation

            filtered_images = [[rankOrderEVMeanFiltering(noisy_image, filter_window_size, ev) for noisy_image in noisy_images] for filter_window_size in filter_window_sizes]

            filtered_RMSEs = [[getRMSE(image, filtered_image) for filtered_image in _] for _ in filtered_images]
            filtered_PSNRs = [[getPSNR(image, filtered_images[i][j], filtered_RMSEs[i][j]) for j in range(len(filtered_images[i]))] for i in range(len(filtered_images))]

            for i in range(len(noisy_images)):
                saveImage(convertToPillowImage(noisy_images[i]), f'{computed_directory}{file_name}_noisy_{i + 1}{file_extension}')

            for i in range(len(filtered_images)):
                 for j in range(len(filtered_images[i])):
                    saveImage(convertToPillowImage(filtered_images[i][j]), f'{computed_directory}{file_name}_filtered_{i + 1}_{j + 1}{file_extension}')

            print('Noisy images data:')
            for i in range(len(noisy_RMSEs)):
                print(f' RMSE_{i + 1} = {noisy_RMSEs[i]}. PSNR_{i + 1} = {noisy_PSNRs[i]}.')

            print('Filtered images data:')
            for i in range(len(filtered_RMSEs)):
                print_str = f'Filter Window sizes: {filter_window_sizes[i]}. Ev: {ev}.'

                for j in range((len(filtered_RMSEs[i]))):
                    print_str += f' RMSE_{i + 1}_{j + 1} = {filtered_RMSEs[i][j]}. PSNR_{i + 1}_{j + 1} = {filtered_PSNRs[i][j]}.'

                print(print_str)

            print('\n')

if __name__ == "__main__":
    try:
         labTask('./assets/cameraman.tif') 

         labTask('./assets/lena_gray_256.tif')         
    except Exception as e:
        print('Error occured:')
        print_exc()