import cv2
import os
import sys
import numpy as np
import tensorflow as tf

char_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
              'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '川', '鄂', '赣', '甘', '贵',
              '桂', '黑', '沪', '冀', '津', '京', '吉', '辽', '鲁', '蒙', '闽', '宁', '青', '琼', '陕', '苏', '晋',
              '皖', '湘', '新', '豫', '渝', '粤', '云', '藏', '浙']
car_plate_w, car_plate_h = 136, 36
char_w, char_h = 20, 20

class Vehicle_License_Plate(object):
    "车牌识别"
    def __init__(self, picture):
        self.vehicle_license_plate = self.vehicle_license_plate_recognition(picture)

    def hist_image(self,img):
        assert img.ndim == 2
        hist = [0 for i in range(256)]
        img_h, img_w = img.shape[0], img.shape[1]

        for row in range(img_h):
            for col in range(img_w):
                hist[img[row, col]] += 1
        p = [hist[n] / (img_w * img_h) for n in range(256)]
        p1 = np.cumsum(p)
        for row in range(img_h):
            for col in range(img_w):
                v = img[row, col]
                img[row, col] = p1[v] * 255
        return img

    def find_board_area(self,img):
        assert img.ndim == 2
        img_h, img_w = img.shape[0], img.shape[1]
        top, bottom, left, right = 0, img_h, 0, img_w
        flag = False
        h_proj = [0 for i in range(img_h)]
        v_proj = [0 for i in range(img_w)]

        for row in range(round(img_h * 0.5), round(img_h * 0.8), 3):
            for col in range(img_w):
                if img[row, col] == 255:
                    h_proj[row] += 1
            if flag == False and h_proj[row] > 12:
                flag = True
                top = row
            if flag == True and row > top + 8 and h_proj[row] < 12:
                bottom = row
                flag = False

        for col in range(round(img_w * 0.3), img_w, 1):
            for row in range(top, bottom, 1):
                if img[row, col] == 255:
                    v_proj[col] += 1
            if flag == False and (v_proj[col] > 10 or v_proj[col] - v_proj[col - 1] > 5):
                left = col
                break
        return left, top, 120, bottom - top - 10

    def verify_scale(self,rotate_rect):
        error = 0.4
        aspect = 4  # 4.7272
        min_area = 10 * (10 * aspect)
        max_area = 150 * (150 * aspect)
        min_aspect = aspect * (1 - error)
        max_aspect = aspect * (1 + error)
        theta = 30

        # 宽或高为0，不满足矩形直接返回False
        if rotate_rect[1][0] == 0 or rotate_rect[1][1] == 0:
            return False

        r = rotate_rect[1][0] / rotate_rect[1][1]
        r = max(r, 1 / r)
        area = rotate_rect[1][0] * rotate_rect[1][1]
        if area > min_area and area < max_area and r > min_aspect and r < max_aspect:
            # 矩形的倾斜角度在不超过theta
            if ((rotate_rect[1][0] < rotate_rect[1][1] and rotate_rect[2] >= -90 and rotate_rect[2] < -(90 - theta)) or
                    (rotate_rect[1][1] < rotate_rect[1][0] and rotate_rect[2] > -theta and rotate_rect[2] <= 0)):
                return True
        return False

    def img_Transform(self,car_rect, image):
        img_h, img_w = image.shape[:2]
        rect_w, rect_h = car_rect[1][0], car_rect[1][1]
        angle = car_rect[2]

        return_flag = False
        if car_rect[2] == 0:
            return_flag = True
        if car_rect[2] == -90 and rect_w < rect_h:
            rect_w, rect_h = rect_h, rect_w
            return_flag = True
        if return_flag:
            car_img = image[int(car_rect[0][1] - rect_h / 2):int(car_rect[0][1] + rect_h / 2),
                      int(car_rect[0][0] - rect_w / 2):int(car_rect[0][0] + rect_w / 2)]
            return car_img

        car_rect = (car_rect[0], (rect_w, rect_h), angle)
        box = cv2.boxPoints(car_rect)

        heigth_point = right_point = [0, 0]
        left_point = low_point = [car_rect[0][0], car_rect[0][1]]
        for point in box:
            if left_point[0] > point[0]:
                left_point = point
            if low_point[1] > point[1]:
                low_point = point
            if heigth_point[1] < point[1]:
                heigth_point = point
            if right_point[0] < point[0]:
                right_point = point

        if left_point[1] <= right_point[1]:  # 正角度
            new_right_point = [right_point[0], heigth_point[1]]
            pts1 = np.float32([left_point, heigth_point, right_point])
            pts2 = np.float32([left_point, heigth_point, new_right_point])  # 字符只是高度需要改变
            M = cv2.getAffineTransform(pts1, pts2)
            dst = cv2.warpAffine(image, M, (round(img_w * 2), round(img_h * 2)))
            car_img = dst[int(left_point[1]):int(heigth_point[1]), int(left_point[0]):int(new_right_point[0])]

        elif left_point[1] > right_point[1]:  # 负角度
            new_left_point = [left_point[0], heigth_point[1]]
            pts1 = np.float32([left_point, heigth_point, right_point])
            pts2 = np.float32([new_left_point, heigth_point, right_point])  # 字符只是高度需要改变
            M = cv2.getAffineTransform(pts1, pts2)
            dst = cv2.warpAffine(image, M, (round(img_w * 2), round(img_h * 2)))
            car_img = dst[int(right_point[1]):int(heigth_point[1]), int(new_left_point[0]):int(right_point[0])]

        return car_img

    '''1.图像预处理'''
    def pre_process(self,orig_img):
        # BGR图片转灰度图：减少数据量
        gray_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
        '''
        cv2.blur(img, (3, 3))  进行均值滤波：柔化一些小的噪声点
        参数说明：img表示输入的图片， (3, 3) 表示进行均值滤波的方框大小
        '''
        blur_img = cv2.blur(gray_img, (3, 3))
        '''
        1.利用Sobel方法可以进行sobel边缘检测
        2.blur_img表示源图像，即进行边缘检测的图像
        3.cv2.CV_16S表示16位有符号的数据类型。
        4.第3和第4个参数分别是对X和Y方向的导数（即dx,dy），对于图像来说就是差分，这里1表示对X求偏导（差分），0表示不对Y求导（差分）。其中，X还可以求2次导。
        5.注意：对X求导就是检测X方向上是否有边缘。
        6.第5个参数ksize是指核的大小。
        '''
        sobel_img = cv2.Sobel(blur_img, cv2.CV_16S, 1, 0, ksize=3)
        '''
        在Sobel函数的第2个参数这里使用了cv2.CV_16S。因为OpenCV文档中对Sobel算子的介绍中有这么一句：“in the case of 8-bit 
        input images it will result in truncated derivatives”。即Sobel函数求完导数后会有负值，还有会大于255的值。而原图像
        是uint8，即8位无符号数，所以Sobel建立的图像位数不够，会有截断。因此要使用16位有符号的数据类型，即cv2.CV_16S
        在经过处理后，别忘了用convertScaleAbs()函数将其转回原来的uint8形式。否则将无法显示图像，而只是一副灰色的窗口。
        '''
        sobel_img = cv2.convertScaleAbs(sobel_img)
        '''
        原始图片从RGB转HSV：车牌背景色一般是蓝色或黄色
        HSV颜色空间：HSV(hue,saturation,value)颜色空间的模型对应于圆柱坐标系中的一个圆锥形子集
        '''
        hsv_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)
        h, s, v = hsv_img[:, :, 0], hsv_img[:, :, 1], hsv_img[:, :, 2]
        '''
        从sobel处理后的图片找到蓝色或黄色区域：从HSV中取出蓝色、黄色区域，和sobel处理后的图片相乘
        #黄色色调区间[26，34],蓝色色调区间:[100,124]
        '''
        blue_img = (((h > 26) & (h < 34)) | ((h > 100) & (h < 124))) & (s > 70) & (v > 70)
        blue_img = blue_img.astype('float32')
        mix_img = np.multiply(sobel_img, blue_img)
        mix_img = mix_img.astype(np.uint8)
        '''二值化：最大类间方差法'''
        ret, binary_img = cv2.threshold(mix_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        '''闭运算：将车牌垂直的边缘连成一个整体，注意核的尺寸'''
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 5))
        close_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
        '''
        在 close_img 中，虽然车牌被相对完整的找出来了，但是整个图片还有太多干扰项，
        接下来就是排除干扰项，尽可能地只保留车牌区域
        '''
        return close_img

    '''2.1车牌定位'''
    def locate_carPlate(self,orig_img, pred_image):
        carPlate_list = []
        temp1_orig_img = orig_img.copy()  # 调试用
        temp2_orig_img = orig_img.copy()  # 调试用
        '''
        cv2.findContours()函数来查找检测物体的轮廓
        在 openCV4 中
            1.三个输入参数：输入图像（二值图像），轮廓检索方式，轮廓近似方法
            2.两个返回值：图像，轮廓，轮廓的层析结构
        '''
        contours, heriachy = cv2.findContours(pred_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        '''求得轮廓外接矩形'''
        for i, contour in enumerate(contours):
            cv2.drawContours(temp1_orig_img, contours, i, (0, 255, 255), 2)
            # 获取轮廓最小外接矩形，返回值rotate_rect
            rotate_rect = cv2.minAreaRect(contour)
            # 根据矩形面积大小和长宽比判断是否是车牌
            if self.verify_scale(rotate_rect):
                ret, rotate_rect2 = self.verify_color(rotate_rect, temp2_orig_img)
                if ret == False:
                    continue
                # 车牌位置矫正
                car_plate = self.img_Transform(rotate_rect2, temp2_orig_img)
                car_plate = cv2.resize(car_plate, (car_plate_w, car_plate_h))  # 调整尺寸为后面CNN车牌识别做准备
                # ========================调试看效果========================#
                box = cv2.boxPoints(rotate_rect2)
                for k in range(4):
                    n1, n2 = k % 4, (k + 1) % 4
                    cv2.line(temp1_orig_img, (box[n1][0], box[n1][1]), (box[n2][0], box[n2][1]), (255, 0, 0), 2)
                # cv2.imshow('opencv_' + str(i), car_plate)
                # ========================调试看效果========================#
                carPlate_list.append(car_plate)

        # cv2.imshow('contour', temp1_orig_img)
        return carPlate_list

    '''2.2给候选车牌区域做漫水填充算法，一方面补全车牌定位中求轮廓可能存在轮廓歪曲的问题，另一方面也可以将非车牌区排除掉'''
    def verify_color(self,rotate_rect, src_image):
        img_h, img_w = src_image.shape[:2]
        mask = np.zeros(shape=[img_h + 2, img_w + 2], dtype=np.uint8)
        connectivity = 4  # 种子点上下左右4邻域与种子颜色值在[loDiff,upDiff]的被涂成new_value，也可设置8邻域
        loDiff, upDiff = 30, 30
        new_value = 255
        flags = connectivity
        flags |= cv2.FLOODFILL_FIXED_RANGE  # 考虑当前像素与种子象素之间的差，不设置的话则和邻域像素比较
        flags |= new_value << 8
        flags |= cv2.FLOODFILL_MASK_ONLY  # 设置这个标识符则不会去填充改变原始图像，而是去填充掩模图像（mask）

        rand_seed_num = 5000  # 生成多个随机种子
        valid_seed_num = 200  # 从rand_seed_num中随机挑选valid_seed_num个有效种子
        adjust_param = 0.1
        box_points = cv2.boxPoints(rotate_rect)
        box_points_x = [n[0] for n in box_points]
        box_points_x.sort(reverse=False)
        adjust_x = int((box_points_x[2] - box_points_x[1]) * adjust_param)
        col_range = [box_points_x[1] + adjust_x, box_points_x[2] - adjust_x]
        box_points_y = [n[1] for n in box_points]
        box_points_y.sort(reverse=False)
        adjust_y = int((box_points_y[2] - box_points_y[1]) * adjust_param)
        row_range = [box_points_y[1] + adjust_y, box_points_y[2] - adjust_y]
        # 如果以上方法种子点在水平或垂直方向可移动的范围很小，则采用旋转矩阵对角线来设置随机种子点
        if (col_range[1] - col_range[0]) / (box_points_x[3] - box_points_x[0]) < 0.4 \
                or (row_range[1] - row_range[0]) / (box_points_y[3] - box_points_y[0]) < 0.4:
            points_row = []
            points_col = []
            for i in range(2):
                pt1, pt2 = box_points[i], box_points[i + 2]
                x_adjust, y_adjust = int(adjust_param * (abs(pt1[0] - pt2[0]))), int(
                    adjust_param * (abs(pt1[1] - pt2[1])))
                if (pt1[0] <= pt2[0]):
                    pt1[0], pt2[0] = pt1[0] + x_adjust, pt2[0] - x_adjust
                else:
                    pt1[0], pt2[0] = pt1[0] - x_adjust, pt2[0] + x_adjust
                if (pt1[1] <= pt2[1]):
                    pt1[1], pt2[1] = pt1[1] + adjust_y, pt2[1] - adjust_y
                else:
                    pt1[1], pt2[1] = pt1[1] - y_adjust, pt2[1] + y_adjust
                temp_list_x = [int(x) for x in np.linspace(pt1[0], pt2[0], int(rand_seed_num / 2))]
                temp_list_y = [int(y) for y in np.linspace(pt1[1], pt2[1], int(rand_seed_num / 2))]
                points_col.extend(temp_list_x)
                points_row.extend(temp_list_y)
        else:
            points_row = np.random.randint(row_range[0], row_range[1], size=rand_seed_num)
            points_col = np.linspace(col_range[0], col_range[1], num=rand_seed_num).astype(np.int)

        points_row = np.array(points_row)
        points_col = np.array(points_col)
        hsv_img = cv2.cvtColor(src_image, cv2.COLOR_BGR2HSV)
        h, s, v = hsv_img[:, :, 0], hsv_img[:, :, 1], hsv_img[:, :, 2]
        # 将随机生成的多个种子依次做漫水填充,理想情况是整个车牌被填充
        flood_img = src_image.copy()
        seed_cnt = 0
        for i in range(rand_seed_num):
            rand_index = np.random.choice(rand_seed_num, 1, replace=False)
            row, col = points_row[rand_index], points_col[rand_index]
            # 限制随机种子必须是车牌背景色
            if (((h[row, col] > 26) & (h[row, col] < 34)) | ((h[row, col] > 100) & (h[row, col] < 124))) & (
                    s[row, col] > 70) & (v[row, col] > 70):
                cv2.floodFill(src_image, mask, (col, row), (255, 255, 255), (loDiff,) * 3, (upDiff,) * 3, flags)
                cv2.circle(flood_img, center=(col, row), radius=2, color=(0, 0, 255), thickness=2)
                seed_cnt += 1
                if seed_cnt >= valid_seed_num:
                    break
        # ======================调试用======================#
        show_seed = np.random.uniform(1, 100, 1).astype(np.uint16)
        # cv2.imshow('floodfill'+str(show_seed),flood_img)
        # cv2.imshow('flood_mask'+str(show_seed),mask)
        # ======================调试用======================#
        # 获取掩模上被填充点的像素点，并求点集的最小外接矩形
        mask_points = []
        for row in range(1, img_h + 1):
            for col in range(1, img_w + 1):
                if mask[row, col] != 0:
                    mask_points.append((col - 1, row - 1))
        mask_rotateRect = cv2.minAreaRect(np.array(mask_points))
        if self.verify_scale(mask_rotateRect):
            return True, mask_rotateRect
        else:
            return False, mask_rotateRect

    '''3.车牌过滤'''
    def cnn_select_carPlate(self,plate_list, model_path):
        if len(plate_list) == 0:
            return False, plate_list
        g1 = tf.Graph()
        sess1 = tf.Session(graph=g1)
        with sess1.as_default():
            with sess1.graph.as_default():
                model_dir = os.path.dirname(model_path)
                saver = tf.train.import_meta_graph(model_path)
                '''
                tf.train.latest_checkpoint()来自动获取最后一次保存的模型
                 '''
                saver.restore(sess1, tf.train.latest_checkpoint(model_dir))
                graph = tf.get_default_graph()
                net1_x_place = graph.get_tensor_by_name('x_place:0')
                net1_keep_place = graph.get_tensor_by_name('keep_place:0')
                net1_out = graph.get_tensor_by_name('out_put:0')

                input_x = np.array(plate_list)
                net_outs = tf.nn.softmax(net1_out)
                preds = tf.argmax(net_outs, 1)  # 预测结果
                probs = tf.reduce_max(net_outs, reduction_indices=[1])  # 结果概率值
                pred_list, prob_list = sess1.run([preds, probs],
                                                 feed_dict={net1_x_place: input_x, net1_keep_place: 1.0})
                # 选出概率最大的车牌
                result_index, result_prob = -1, 0.
                for i, pred in enumerate(pred_list):
                    if pred == 1 and prob_list[i] > result_prob:
                        result_index, result_prob = i, prob_list[i]
                if result_index == -1:
                    return False, plate_list[0]
                else:
                    return True, plate_list[result_index]

    '''4.1.字符分割(调用4.2)'''
    def get_chars(self,car_plate):
        img_h, img_w = car_plate.shape[:2]
        h_proj_list = []  # 水平投影长度列表
        h_temp_len, v_temp_len = 0, 0
        h_startIndex, h_end_index = 0, 0  # 水平投影记索引
        h_proj_limit = [0.2, 0.8]  # 车牌在水平方向得轮廓长度少于20%或多余80%过滤掉
        char_imgs = []

        # 将二值化的车牌水平投影到Y轴，计算投影后的连续长度，连续投影长度可能不止一段
        h_count = [0 for i in range(img_h)]
        for row in range(img_h):
            temp_cnt = 0
            for col in range(img_w):
                if car_plate[row, col] == 255:
                    temp_cnt += 1
            h_count[row] = temp_cnt
            if temp_cnt / img_w < h_proj_limit[0] or temp_cnt / img_w > h_proj_limit[1]:
                if h_temp_len != 0:
                    h_end_index = row - 1
                    h_proj_list.append((h_startIndex, h_end_index))
                    h_temp_len = 0
                continue
            if temp_cnt > 0:
                if h_temp_len == 0:
                    h_startIndex = row
                    h_temp_len = 1
                else:
                    h_temp_len += 1
            else:
                if h_temp_len > 0:
                    h_end_index = row - 1
                    h_proj_list.append((h_startIndex, h_end_index))
                    h_temp_len = 0

        # 手动结束最后得水平投影长度累加
        if h_temp_len != 0:
            h_end_index = img_h - 1
            h_proj_list.append((h_startIndex, h_end_index))
        # 选出最长的投影，该投影长度占整个截取车牌高度的比值必须大于0.5
        h_maxIndex, h_maxHeight = 0, 0
        for i, (start, end) in enumerate(h_proj_list):
            if h_maxHeight < (end - start):
                h_maxHeight = (end - start)
                h_maxIndex = i
        if h_maxHeight / img_h < 0.5:
            return char_imgs
        chars_top, chars_bottom = h_proj_list[h_maxIndex][0], h_proj_list[h_maxIndex][1]

        plates = car_plate[chars_top:chars_bottom + 1, :]
        char_addr_list = self.horizontal_cut_chars(plates)

        for i, addr in enumerate(char_addr_list):
            char_img = car_plate[chars_top:chars_bottom + 1, addr[0]:addr[1]]
            char_img = cv2.resize(char_img, (char_w, char_h))
            char_imgs.append(char_img)
        return char_imgs

    '''4.2左右切割'''
    def horizontal_cut_chars(self,plate):
        char_addr_list = []
        area_left, area_right, char_left, char_right = 0, 0, 0, 0
        img_w = plate.shape[1]

        # 获取车牌每列边缘像素点个数
        def getColSum(img, col):
            sum = 0
            for i in range(img.shape[0]):
                sum += round(img[i, col] / 255)
            return sum;

        sum = 0
        for col in range(img_w):
            sum += getColSum(plate, col)
        # 每列边缘像素点必须超过均值的60%才能判断属于字符区域
        col_limit = 0  # round(0.5*sum/img_w)
        # 每个字符宽度也进行限制
        charWid_limit = [round(img_w / 12), round(img_w / 5)]
        is_char_flag = False

        for i in range(img_w):
            colValue = getColSum(plate, i)
            if colValue > col_limit:
                if is_char_flag == False:
                    area_right = round((i + char_right) / 2)
                    area_width = area_right - area_left
                    char_width = char_right - char_left
                    if (area_width > charWid_limit[0]) and (area_width < charWid_limit[1]):
                        char_addr_list.append((area_left, area_right, char_width))
                    char_left = i
                    area_left = round((char_left + char_right) / 2)
                    is_char_flag = True
            else:
                if is_char_flag == True:
                    char_right = i - 1
                    is_char_flag = False
        # 手动结束最后未完成的字符分割
        if area_right < char_left:
            area_right, char_right = img_w, img_w
            area_width = area_right - area_left
            char_width = char_right - char_left
            if (area_width > charWid_limit[0]) and (area_width < charWid_limit[1]):
                char_addr_list.append((area_left, area_right, char_width))
        return char_addr_list

    '''5.字符提取'''
    def extract_char(self,car_plate):
        gray_plate = cv2.cvtColor(car_plate, cv2.COLOR_BGR2GRAY)
        ret, binary_plate = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        char_img_list = self.get_chars(binary_plate)
        return char_img_list

    '''6.字符识别'''
    def cnn_recongnize_char(self,img_list, model_path):
        g2 = tf.Graph()
        sess2 = tf.Session(graph=g2)
        text_list = []

        if len(img_list) == 0:
            return text_list
        with sess2.as_default():
            with sess2.graph.as_default():
                model_dir = os.path.dirname(model_path)
                saver = tf.train.import_meta_graph(model_path)
                saver.restore(sess2, tf.train.latest_checkpoint(model_dir))
                graph = tf.get_default_graph()
                net2_x_place = graph.get_tensor_by_name('x_place:0')
                net2_keep_place = graph.get_tensor_by_name('keep_place:0')
                net2_out = graph.get_tensor_by_name('out_put:0')

                data = np.array(img_list)
                # 数字、字母、汉字，从67维向量找到概率最大的作为预测结果
                net_out = tf.nn.softmax(net2_out)
                preds = tf.argmax(net_out, 1)
                my_preds = sess2.run(preds, feed_dict={net2_x_place: data, net2_keep_place: 1.0})

                for i in my_preds:
                    text_list.append(char_table[i])
                return text_list

    def vehicle_license_plate_recognition(self, picture):
        plate_model_path = "license_plate_recognition/model/plate_recongnize/model.ckpt-520.meta"
        char_model_path = "license_plate_recognition/model/char_recongnize/model.ckpt-720.meta"
        img = cv2.imread(picture)

        # 预处理
        pred_img = self.pre_process(img)

        # 车牌定位
        car_plate_list = self.locate_carPlate(img, pred_img)

        # CNN车牌过滤
        ret, car_plate = self.cnn_select_carPlate(car_plate_list, plate_model_path)
        if ret == False:
            # print("未检测到车牌")
            return "未检测到车牌"
            sys.exit(-1)
        # cv2.imshow('cnn_plate',car_plate)

        # 字符提取
        char_img_list = self.extract_char(car_plate)

        # CNN字符识别
        text = self.cnn_recongnize_char(char_img_list, char_model_path)

        # 车牌显示模式：譬如：粤S 88888
        vehicle_plate1 = []
        vehicle_plate2 = []
        for i in range(len(text)):
            if i <= 1:
                vehicle_plate1.append(text[i])
            else:
                vehicle_plate2.append(text[i])

        vehicle_plate = "".join(vehicle_plate1) + " " + "".join(vehicle_plate2)
        # print(vehicle_plate)
        return vehicle_plate

