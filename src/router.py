import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

model = load_model('doodle.h5')


@app.route('/predict', methods=["POST"])
def predict():
    data = [float(i)/255 for i in request.get_data().decode().split(',') if i != '']
    data = np.array([[data]])
    data = data.reshape((400, 400))

    img = Image.fromarray(data)
    img = img.resize((28, 28))

    img = np.array(img)
    img = np.expand_dims(img, axis=0)

    predictions = model.predict(img, verbose=0)
    categories = tuple(fn[:-4] for fn in os.listdir('../data') if fn.endswith('npy'))

    response = {}
    for prediction, category in zip(predictions[0], categories):
        response[category] = float(prediction)

    return jsonify({'predictions': response})


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
