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

a = tf.test.is_built_with_cuda()
print(a)

b = tf.test.is_gpu_available(cuda_only = False, min_cuda_compute_capability = None)
print(b)