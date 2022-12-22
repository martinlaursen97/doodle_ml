import numpy as np
from PIL import Image
import os
import urllib.request
import shutil
import time


# A decorator function to time the execution of the decorated function
def time_function(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        print(f'{func.__name__} took {elapsed:.6f} seconds')
        return result

    return wrapper


# A utility function to create directories if they do not already exist
def create_directories_if_not_exists(*directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory)


class NpyImageConverter:
    def __init__(self, data_path, training_dir, testing_dir, train_amount, test_amount, extension, img_width, img_height):
        # Initialize the class variables
        self.data_path = data_path
        self.training_dir = training_dir
        self.testing_dir = testing_dir
        self.train_amount = train_amount
        self.test_amount = test_amount
        self.extension = extension
        self.img_width = img_width
        self.img_height = img_height

        # Create necessary directories for the data
        create_directories_if_not_exists(data_path, training_dir, testing_dir)

    @time_function
    def download_npy_files(self, url, categories):
        # Download the npy files for the given categories from the given URL
        for category in categories:
            file_path = f'{self.data_path}/{category}.npy'
            if not os.path.exists(file_path):
                local_filename, headers = urllib.request.urlretrieve(
                    f'{url}/{category}.npy',
                    file_path
                )
                print(f'Download complete: {local_filename}')

    @time_function
    def convert_and_save_images(self, categories):
        # Convert and save the images from the npy files to the training and testing directories
        for category in categories:
            training_category_dir = f'{self.training_dir}/{category}'
            testing_category_dir = f'{self.testing_dir}/{category}'

            create_directories_if_not_exists(training_category_dir, testing_category_dir)

            npy_data = np.load(f'{self.data_path}/{category}.npy')

            self.save_images_to_category_dir(npy_data, training_category_dir, 0, self.train_amount)
            self.save_images_to_category_dir(npy_data, testing_category_dir, self.train_amount,
                                             self.test_amount + self.train_amount)

    @time_function
    def save_images_to_category_dir(self, loaded_npy, dir_path, start, stop):
        save_count = 0

        for idx in range(start, stop):
            save_path = f'{dir_path}/{idx + 1}.{self.extension}'

            if not os.path.exists(save_path):
                pixels = loaded_npy[idx]
                pixel_matrix = pixels.reshape((self.img_width, self.img_height))
                img = Image.fromarray(pixel_matrix)
                img.save(save_path)
                save_count += 1

        print(f'Saved {save_count} images to {dir_path}')

    @time_function
    def clear_unused_files(self, categories):
        # Clear unused npy files
        for file in os.listdir(self.data_path):
            if file.endswith('.npy') and file[:-4] not in categories:
                os.remove(f'{self.data_path}/{file}')

        # Clear unused directories
        for directory in [self.training_dir, self.testing_dir]:
            for file in os.listdir(directory):
                file_path = f'{directory}/{file}'
                if file not in categories:
                    shutil.rmtree(file_path)

    def clear_out_of_bounds_images(self, categories):
        removed_count = 0

        for category in categories:
            for directory in [self.training_dir, self.testing_dir]:
                category_dir = f'{directory}/{category}'

                if os.path.exists(category_dir):
                    for img_file in os.listdir(category_dir):
                        img_number = int(img_file.split('.')[0])
                        img_path = f'{category_dir}/{img_file}'

                        if directory == self.training_dir and img_number > self.train_amount:
                            os.remove(img_path)
                            removed_count += 1
                        elif directory == self.testing_dir and (
                                img_number < self.train_amount or img_number > self.train_amount + self.test_amount):
                            os.remove(img_path)
                            removed_count += 1

        print(f'Removed {removed_count} invalid images')


if __name__ == '__main__':
    # Set the paths for the data, training, and testing directories
    DATA_PATH = '../data'
    TRAINING_PATH = f'{DATA_PATH}/training'
    TESTING_PATH = f'{DATA_PATH}/testing'

    # Set the number of training and testing images to be generated
    NUM_TRAINING_IMAGES = 10000
    NUM_TESTING_IMAGES = 1000

    # Set file extension
    EXTENSION = 'jpg'

    # Set the dimensions of the generated images
    IMG_WIDTH = 28
    IMG_HEIGHT = 28

    # Choose the categories of images to be downloaded and generated from the QuickDraw dataset
    # https://quickdraw.withgoogle.com/data
    CATEGORIES = ['cat', 'axe', 'bicycle', 'skull', 'rainbow', 'tree', 'zigzag', 'cake']

    # Set the URL of the QuickDraw dataset
    URL = 'https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap'

    # Initialize the NpyImageConverter object
    converter = NpyImageConverter(DATA_PATH, TRAINING_PATH, TESTING_PATH, NUM_TRAINING_IMAGES, NUM_TESTING_IMAGES,
                                  EXTENSION, IMG_WIDTH, IMG_HEIGHT)

    converter.clear_unused_files(CATEGORIES)
    converter.clear_out_of_bounds_images(CATEGORIES)
    converter.download_npy_files(URL, CATEGORIES)
    converter.convert_and_save_images(CATEGORIES)
