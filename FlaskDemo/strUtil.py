import datetime
import random

class Pic_str:
    def create_uuid(self):  # 生成唯一的图片的名称字符串，防止图片显示时的重名问题
        now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
        random_num = random.randint(0, 100)  # 生成的随机整数n，其中0<=n<=100
        if random_num <= 10:
            random_num = str(0) + str(random_num)
        unique_num = str(now_time) + str(random_num)
        return unique_num
