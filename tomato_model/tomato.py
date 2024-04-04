# tomato_model/tomato.py
import numpy as np
from keras.preprocessing import image
from keras.models import load_model

model = load_model('tomato_model/tomatoes.hdf5')  # Replace with the actual path
class_labels = ['Tomato Bacterial spot', 'Tomato Early blight', 'Tomato Late_blight', 'Tomato Leaf Mold', 'Tomato Septoria leaf spot', 'Tomato Spider mites-Two-spotted spider mite', 'Tomato Target Spot', 'Tomato Tomato Yellow Leaf Curl Virus', 'Tomato Tomato mosaic virus', 'Tomato healthy']

def predict_tomato(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions)
    prediction_label = class_labels[predicted_class]
    return prediction_label
