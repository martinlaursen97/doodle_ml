import numpy as np
from PIL import Image

import os
import urllib.request
import shutil
import time


def time_function(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        print(f'{func.__name__} took {elapsed:.6f} seconds')
        return result

    return wrapper


def create_paths_if_not_exists(*paths):
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)


class NpyToJpgConverter:
    def __init__(self, data_path, training_dir, testing_dir, train_amount, test_amount, img_w=28, img_h=28):
        self.data_path = data_path
        self.training_dir = training_dir
        self.testing_dir = testing_dir
        self.train_amount = train_amount
        self.test_amount = test_amount
        self.img_w = img_w
        self.img_h = img_h
        create_paths_if_not_exists(data_path, training_dir, testing_dir)

    @time_function
    def download_npy_files(self, categories):
        for category in categories:
            path = f'{self.data_path}/{category}.npy'
            if not os.path.exists(path):
                urllib.request.urlretrieve(
                    f'https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/{category}.npy',
                    path
                )

    @time_function
    def convert_and_save_images(self):
        categories = tuple(fn[:-4] for fn in os.listdir(self.data_path) if fn.endswith('npy'))

        for category in categories:
            category_training_dir_path = f'{self.training_dir}/{category}'
            category_testing_dir_path = f'{self.testing_dir}/{category}'

            if not os.path.exists(category_training_dir_path):
                os.mkdir(f'{self.training_dir}/{category}')

            if not os.path.exists(category_testing_dir_path):
                os.mkdir(f'{self.testing_dir}/{category}')

            loaded_npy = np.load(f'{self.data_path}/{category}.npy')
            self.save_images_to_category_dir(loaded_npy, f'{self.training_dir}/{category}', 0, self.train_amount)
            self.save_images_to_category_dir(loaded_npy, f'{self.testing_dir}/{category}', self.train_amount,
                                             self.test_amount + self.train_amount)

    @time_function
    def save_images_to_category_dir(self, loaded_npy, dir_path, start, stop):
        save_count = 0
        for idx in range(start, stop):
            save_path = f'{dir_path}/{idx + 1}.jpg'

            if not os.path.exists(save_path):
                pixels = loaded_npy[idx]
                pixel_matrix = pixels.reshape((self.img_w, self.img_h))
                img = Image.fromarray(pixel_matrix)
                img.save(save_path)
                save_count += 1

        print(f'Saved {save_count} images to {dir_path}')

    @time_function
    def clear_unused_files(self, categories):
        for file in os.listdir(self.data_path):
            if file.endswith('.npy') and file[:-4] not in categories:
                os.remove(f'{self.data_path}/{file}')

        for folder in [self.training_dir, self.testing_dir]:
            for file in os.listdir(folder):

                file_path = f'{folder}/{file}'
                if file not in categories:
                    shutil.rmtree(file_path)


if __name__ == '__main__':
    DATA_PATH = '../data'
    TRAINING_PATH = f'{DATA_PATH}/training'
    TESTING_PATH = f'{DATA_PATH}/testing'
    NUM_TRAINING_IMAGES = 7000
    NUM_TESTING_IMAGES = 1000
    IMG_WIDTH = 28
    IMG_HEIGHT = 28
    CATEGORIES = ['cat', 'axe', 'bicycle', 'skull', 'rainbow', 'tree', 'zigzag', 'cake']

    converter = NpyToJpgConverter(DATA_PATH, TRAINING_PATH, TESTING_PATH, NUM_TRAINING_IMAGES, NUM_TESTING_IMAGES,
                                  IMG_WIDTH, IMG_HEIGHT)

    converter.clear_unused_files(CATEGORIES)
    converter.download_npy_files(CATEGORIES)
    converter.convert_and_save_images()
