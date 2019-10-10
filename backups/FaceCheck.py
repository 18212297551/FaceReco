"""
opencv获取摄像头录像，检测视频中是否有人存在，如果有人，这个人是否在我的百度人脸库中，如果在我的百度人脸库则。。。如果不在则。。。
实现思路：
1。opencv获取实时视频
2.处理视频，检测人像
3.处理人像，与人脸库对比
难点：
1.腾讯人脸搜索有QPS限制，不能每帧图像都拿去比对
2.并且比对需要时间较长，就算没有qps限制，也不可能实现每帧都进行比对
3.如何判断视频中存在人脸
4.多久进行一次检测
5.视频中人脸图像清晰度是否足够，如何防止截取的图像出现重影

"""
import base64
import json
import random
import time

import cv2 as cv
import numpy as np
import dlib
import requests
from PIL import Image
import multiprocessing as mlp
from FaceManage import FaceManage


# 画面获取进程存入图像，人脸检测进程读取图像
Pictures = mlp.Queue(20)

APIKEY = 'K7G0KLcoQnTLH4QjmCZMigyM'
SECRETKEY = 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL'
APPID = '17376947'
AccessToken = '?access_token=24.1cfd5fdd87d1868dc05ddbf033663423.2592000.1572447440.282335-17376947'
TokenAlTime = int


def get_face_location_cv(_Q):
    __doc__ = '''人脸检测线程'''
    while True:
        if _Q.empty():continue
        else:
            _image = _Q.get()
            detector = dlib.get_frontal_face_detector()
            img = cv.imdecode(_image,1)
            img_rgb = cv.cvtColor(img,cv.COLOR_BGR2RGB)
            rects = detector(img_rgb,0)
            if rects:
                print('正在进行人脸处理')
                _session_id = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + str(random.randint(0, 9))
                _path_img = './Face_img/cv/source/{}.png'.format(_session_id)
                cv.imwrite(_path_img,img_rgb)
                for rect in rects:
                    # 匹配得出人脸坐标int(x)-10 if num%2==0 else int(x)+10
                    face_pos = list(str(rect).replace('[(','').replace(') (',',').replace(')]','').replace(' ','').split(','))
                    # str转为int
                    face_pos = list(map(lambda x:int(x) ,face_pos))
                    # 从图像中切割出人脸部分
                    face_spilt(img_rgb,face_pos)
            else:
                print('没有发现人脸信息')


def face_spilt(_image,face_pos):
    # 传入原图像和人脸位置数据，切割人脸图像并保存
    _session_id = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + str(random.randint(0,9))
    _path_face = './Face_img/cv/split/{}.png'.format(_session_id)
    _path_img = './Face_img/cv/source/{}.png'.format(_session_id)
    _img = Image.fromarray(_image)
    _img.save(_path_img)
    _face = _img.crop(face_pos)
    _face.save(_path_face)
    # 从百度人脸库中搜索人脸
    face_search(_path_face)
    # _face.show()


def face_search(_path):
    # 传入人脸图像路径，从人脸库中搜索人脸
    _url = 'https://aip.baidubce.com/rest/2.0/face/v3/search'
    _data = {'image': media_to_bs64(_path), 'image_type': 'BASE64', 'group_id_list': 'friends,classmates_high,manager'}
    res = requests.post(_get_requrl(_url),_data)
    answer = json.loads(res.text)
    if not answer['error_code']:
        answer = answer['result']['user_list'][0]
        print(answer['group_id'],answer['user_id'],answer['score'])


def _get_requrl(_url):
    # 传入url，整合acesstoken后返回
    return _url + AccessToken

def get_token():
    # 获取ACESSTOKEN
    global AccessToken, TokenAlTime
    _url = 'https://aip.baidubce.com/oauth/2.0/token'
    _data = {'grant_type': 'client_credentials', 'client_id': APIKEY, 'client_secret': SECRETKEY}
    _res = requests.post(_url,_data)
    _answer = json.loads(_res.text)
    AccessToken = '?access_token=' + _answer['access_token']
    TokenAlTime = int(_answer['expires_in']) + int(time.time())

def video_to_image(_Q):
    __doc__ = '''画面获取线程'''
    cap = cv.VideoCapture(0)
    flag = True
    start_time = time.time()
    files = list(map(lambda i:'check'+str(i),range(1,21)))
    index = 0
    while flag:
        ret, frame = cap.read()
        if ret:
            gray = cv.cvtColor(frame,cv.IMREAD_COLOR)
            cv.imshow('show',gray)
            new_time = time.time()
            interval = new_time-start_time
            if interval > 1.5:
                start_time = new_time
                img_content = cv.imencode('.png',gray.copy(),[1,95])
                index += 1
                _Q.put(img_content[1])
                if index >= len(files):index = 0
            if cv.waitKey(1) == ord('q'):break

    cap.release()
    cv.destroyAllWindows()

def media_to_bs64(media):
    with open(media, 'rb') as f:return base64.b64encode(f.read()).decode()


def main():
    P1 = mlp.Process(target=get_face_location_cv,args=(Pictures,))
    P2 = mlp.Process(target=video_to_image,args=(Pictures,))
    P1.start()
    P2.start()


if __name__ == '__main__':
    main()
