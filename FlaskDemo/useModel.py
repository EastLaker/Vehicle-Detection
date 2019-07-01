# coding=utf-8
import os
# 图像读取库
from PIL import Image
# 矩阵运算库
import numpy as np
import tensorflow as tf
import glob

class vehicledect:
    # 数据文件夹
    data_dir = "./test"
    # 模型文件路径
    model_path = "model/image_model"

    def __init__(self):
        self.data_dir = "./test"
        self.model_path = "model/image_model"

    # 修改图片尺寸
    def convertjpg(self, jpgfile, outdir, width=32, height=32):
        img = Image.open(jpgfile)
        img = img.convert('RGB')
        img.save(os.path.join(outdir, os.path.basename(jpgfile)))
        new_img = img.resize((width, height), Image.BILINEAR)
        new_img.save(os.path.join(outdir, os.path.basename(jpgfile)))

    # 从文件夹读取图片和标签到numpy数组中
    # 标签信息在文件名中，例如1_40.jpg表示该图片的标签为1
    def read_data(self, data_Dir):
        datas = []
        # labels = []
        fpaths = []
        for fname in os.listdir(data_Dir):
            fpath = os.path.join(data_Dir, fname)
            fpaths.append(fpath)
            image = Image.open(fpath)
            data = np.array(image) / 255.0
            datas.append(data)
        datas = np.array(datas)
        return fpaths, datas

    def train(self):
        # 将static里的图片压缩至32x32
        for jpgfile in glob.glob("./static/*.jpg"):
            self.convertjpg(jpgfile, "./test")

        fpaths, datas = self.read_data(self.data_dir)

        # 计算有多少类图片
        num_classes = 10

        # 定义Placeholder，存放输入和标签
        datas_placeholder = tf.placeholder(tf.float32, [None, 32, 32, 3])
        labels_placeholder = tf.placeholder(tf.int32, [None])

        # 存放DropOut参数的容器，训练时为0.25，测试时为0
        dropout_placeholdr = tf.placeholder(tf.float32)

        # 定义卷积层, 20个卷积核, 卷积核大小为5，用Relu激活
        conv0 = tf.layers.conv2d(datas_placeholder, 20, 5, activation=tf.nn.relu)
        # 定义max-pooling层，pooling窗口为2x2，步长为2x2
        pool0 = tf.layers.max_pooling2d(conv0, [2, 2], [2, 2])

        # 定义卷积层, 40个卷积核, 卷积核大小为4，用Relu激活
        conv1 = tf.layers.conv2d(pool0, 40, 4, activation=tf.nn.relu)
        # 定义max-pooling层，pooling窗口为2x2，步长为2x2
        pool1 = tf.layers.max_pooling2d(conv1, [2, 2], [2, 2])

        # 定义卷积层, 60个卷积核, 卷积核大小为3，用Relu激活
        conv2 = tf.layers.conv2d(pool0, 60, 3, activation=tf.nn.relu)
        # 定义max-pooling层，pooling窗口为2x2，步长为2x2
        pool2 = tf.layers.max_pooling2d(conv2, [2, 2], [2, 2])

        # 将3维特征转换为1维向量
        flatten = tf.layers.flatten(pool2)

        # 全连接层，转换为长度为100的特征向量
        fc = tf.layers.dense(flatten, 400, activation=tf.nn.relu)

        # 加上DropOut，防止过拟合
        dropout_fc = tf.layers.dropout(fc, dropout_placeholdr)

        # 未激活的输出层
        logits = tf.layers.dense(dropout_fc, num_classes)

        predicted_labels = tf.arg_max(logits, 1)

        # 利用交叉熵定义损失
        losses = tf.nn.softmax_cross_entropy_with_logits(
            labels=tf.one_hot(labels_placeholder, num_classes),
            logits=logits
        )
        # 平均损失
        mean_loss = tf.reduce_mean(losses)

        # 定义优化器，指定要优化的损失函数
        optimizer = tf.train.AdamOptimizer(learning_rate=1e-2).minimize(losses)

        # 用于保存和载入模型
        saver = tf.train.Saver()

        with tf.Session() as sess:
            print("检测车辆")
            # 如果是测试，载入参数
            saver.restore(sess, self.model_path)
            print("从{}载入模型".format(self.model_path))
            # label和名称的对照关系
            label_name_dict = {
                0: "巴士",
                1: "出租车",
                2: "货车",
                3: "家用轿车",
                4: "面包车",
                5: "吉普车",
                6: "运动型多功能车",
                7: "重型货车",
                8: "赛车",
                9: "消防车"
            }
            # 定义输入和Label以填充容器，测试时dropout为0
            test_feed_dict = {
                datas_placeholder: datas,
                dropout_placeholdr: 0
            }
            predicted_labels_val = sess.run(predicted_labels, feed_dict=test_feed_dict)
            # 真实label与模型预测label
            for fpath, predicted_label in zip(fpaths, predicted_labels_val):
                # 将label id转换为label名
                predicted_label_name = label_name_dict[predicted_label]
                print("{}\t{}".format(fpath, predicted_label_name))
                return predicted_label_name

