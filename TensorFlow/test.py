#!/usr/bin/env python
# coding: utf-8

# # Keras
# 
# Keras 是一个用于构建和训练深度学习模型的高阶 API。它可用于快速设计原型、高级研究和生产。
# 
# keras的3个优点：
# 方便用户使用、模块化和可组合、易于扩展
# 
# 
# ##  1.导入tf.keras
# tensorflow2推荐使用keras构建网络，常见的神经网络都包含在keras.layer中(最新的tf.keras的版本可能和keras不同)


import tensorflow as tf
from tensorflow.keras import layers
import numpy as np

print(tf.__version__)
print(tf.keras.__version__)

import tensorflow as tf
mnist = tf.keras.datasets.mnist

(x_train, y_train),(x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(28, 28)),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5)
model.evaluate(x_test, y_test)

