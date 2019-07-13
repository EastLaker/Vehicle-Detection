# author: 陈宏飞
import os
CUDA_VISIBLE_DEVICES=""
from keras.preprocessing import image
import numpy as np
import cv2
import keras
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import tensorflow as tf

img_height = 256      # 训练图片高度
img_width = 342       # 训练图片宽度
batch_size = 8       # 每批数量

model = keras.models.load_model("./car_model/carModel.h5")
graph = tf.get_default_graph()

# 读取
f = open('car_model.txt', 'r', encoding='utf-8')
a = f.read()
classes_dict = eval(a)
f.close()
'''
img = image.load_img('./static/vehicle/test.jpg', target_size=(img_height, img_width))
x = image.img_to_array(img)
x = x / 255
x = np.expand_dims(x, axis=0)
preds = model.predict(x)
'''


class CarModelDetector:
    @staticmethod
    def detect_model(pic_path):
        global graph
        with graph.as_default():
            img = image.load_img(pic_path, target_size=(img_height, img_width))
            x = image.img_to_array(img)
            x = x / 255
            x = np.expand_dims(x, axis=0)
            preds = model.predict(x)
            paixu = dict(zip(classes_dict, preds[0]))
            paixu = sorted(paixu.items(), key=lambda x: x[1], reverse=True)
            print(paixu[:5])
            return paixu[:5]
