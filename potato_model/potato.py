# potato_model/potato.py
import numpy as np
from keras.preprocessing import image
from keras.models import load_model

model = load_model('potato_model/potatoes.h5')  # Replace with the actual path
class_labels = ['Potato Early blight', 'Potato Late blight', 'Potato healthy']

def predict_potato(image_path):
    img = image.load_img(image_path, target_size=(256, 256))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions)
    prediction_label = class_labels[predicted_class]
    return prediction_label
