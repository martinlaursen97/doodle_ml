import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from flask_cors import CORS
from PIL import Image

# Initialize the Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Load the trained model
model = load_model('doodle.h5')


# Define the predict route
@app.route('/predict', methods=["POST"])
def predict():
    # Get the data from the request and normalize it
    request_data = [float(i) / 255 for i in request.get_data().decode().split(',') if i != '']
    data = np.array([[request_data]])
    data = data.reshape((400, 400))

    # Resize the image to the required size
    image = Image.fromarray(data)
    image = image.resize((28, 28))

    # Convert the image to a numpy array and add a dimension
    image_data = np.array(image)
    image_data = np.expand_dims(image_data, axis=0)

    # Get the predictions from the model
    predictions = model.predict(image_data, verbose=0)

    # Get the list of categories
    categories = tuple(fn[:-4] for fn in os.listdir('../data') if fn.endswith('npy'))

    # Create a response dictionary
    response = {}
    for prediction, category in zip(predictions[0], categories):
        response[category] = float(prediction)

    # Return the response as a JSON object
    return jsonify({'predictions': response})


# Define the index route
@app.route('/', methods=['GET'])
def index():
    # Render the index template
    return render_template('index.html')


# Run the app
if __name__ == '__main__':
    app.run()
