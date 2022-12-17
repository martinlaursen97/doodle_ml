import os

import matplotlib.pyplot as plt
from tensorflow.keras.layers import Conv2D, Dense, Flatten, MaxPooling2D
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Constants
TARGET_SIZE = 28
COLOR_MODE = 'grayscale'
CLASS_MODE = 'categorical'
DATA_PATH = '../data'
TRAINING_FILES_PATH = f'{DATA_PATH}/training'
TESTING_FILES_PATH = f'{DATA_PATH}/testing'

# Create image data generator
datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

# Create training and testing datasets
training_set = datagen.flow_from_directory(
    TRAINING_FILES_PATH,
    target_size=(TARGET_SIZE, TARGET_SIZE),
    batch_size=32,
    class_mode=CLASS_MODE,
    color_mode=COLOR_MODE)

testing_set = datagen.flow_from_directory(
    TESTING_FILES_PATH,
    target_size=(TARGET_SIZE, TARGET_SIZE),
    batch_size=32,
    class_mode=CLASS_MODE,
    color_mode=COLOR_MODE)

# Create model
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(TARGET_SIZE, TARGET_SIZE, 1)))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
num_classes = len([fn for fn in os.listdir(DATA_PATH) if fn.endswith('.npy')])
model.add(Dense(num_classes, activation='softmax'))

# Compile model
adam = Adam(learning_rate=0.001)
model.compile(optimizer=adam, loss='categorical_crossentropy', metrics=['accuracy'])

# Train model and collect history
history = model.fit(x=training_set, epochs=1, validation_data=testing_set)

# Extract training and validation loss and accuracy
train_loss = history.history['loss']
train_acc = history.history['accuracy']
val_loss = history.history['val_loss']
val_acc = history.history['val_accuracy']

# Plot loss
plt.plot(train_loss, label='Training loss')
plt.plot(val_loss, label='Validation loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Evaluate model on test data
model.evaluate(testing_set)

# Save model
model.save('doodle.h5')
