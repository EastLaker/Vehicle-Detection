import cv2
class Face_Detection():
    @staticmethod
    def faceDetection():
        filepath = "imgfaced/faceimg.jpg"
        color = (127, 255, 0)  # 定义绘制颜色
        img = cv2.imread(filepath)  # 读取图片
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换灰色
        classifier = cv2.CascadeClassifier("haarcascade/haarcascade_frontalface_default.xml")
        faceRects = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32))
        if len(faceRects)>2:
            for faceRect in faceRects:  # 单独框出每一张人脸
                x, y, w, h = faceRect
                cv2.rectangle(img, (x, y - 10), (x + w, y + h + 10), color, 1)
        elif len(faceRects)==2:
            for faceRect in faceRects:
                x, y, w, h = faceRect
                cv2.rectangle(img, (x, y - 10), (x + w, y + h + 10), color, 1)
            a, b = faceRects
            x1, y1, w1, h1 = a
            x2, y2, w2, h2 = b
            if x1 < x2:
                cv2.rectangle(img, (x1, y1 - 30), (x1 + 104, y1 - 10), color, thickness=-1)
                cv2.putText(img, 'Codriver', ((x1, y1 - 12)), cv2.FONT_HERSHEY_PLAIN, 1.5, [12, 25, 0], 2)
                cv2.rectangle(img, (x2, y2 - 30), (x2 + 72, y2 - 10), color, thickness=-1)
                cv2.putText(img, 'Driver', ((x2, y2 - 12)), cv2.FONT_HERSHEY_PLAIN, 1.5, [12, 25, 0], 2)
            else:
                cv2.rectangle(img, (x2, y2 - 30), (x2 + 104, y2 - 10), color, thickness=-1)
                cv2.putText(img, 'Codriver', ((x2, y2 - 12)), cv2.FONT_HERSHEY_PLAIN, 1.5, [12, 25, 0], 2)
                cv2.rectangle(img, (x1, y1 - 30), (x1 + 72, y1 - 10), color, thickness=-1)
                cv2.putText(img, 'Driver', ((x1, y1 - 12)), cv2.FONT_HERSHEY_PLAIN, 1.5, [12, 25, 0], 2)
        elif len(faceRects)==1:
            for faceRect in faceRects:
                x, y, w, h = faceRect
                cv2.rectangle(img, (x, y - 10), (x + w, y + h + 10), color, 1)
                cv2.rectangle(img, (x, y - 30), (x + 72, y - 10), color, thickness=-1)
                cv2.putText(img, 'Driver', ((x, y - 12)), cv2.FONT_HERSHEY_PLAIN, 1.5, [12, 25, 0], 2)
        #else:
        #    cv2.rectangle(img, (20, 20), (247, 60), color, thickness=-1)#
        #    cv2.putText(img, 'No Driver', ((20, 57)), cv2.FONT_HERSHEY_PLAIN, 3, [12, 25, 0], 2)
        cv2.imwrite('imgfaced/test.jpg', img)
