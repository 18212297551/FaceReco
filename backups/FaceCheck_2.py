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
import playsound
import cv2 as cv
import numpy as np
import dlib
import requests
from PIL import Image
import multiprocessing as mlp
from FaceManage import FaceManage
from baidu_aip import AipSpeech

APIKEY = 'K7G0KLcoQnTLH4QjmCZMigyM'
SECRETKEY = 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL'
APPID = '17376947'

def get_face_location_cv(_image):
    detector = dlib.get_frontal_face_detector()
    # predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    _img = cv.imread(_image)
    rects = detector(_img,0)
    # print(rects)
    if rects:
        for rect in rects:
            # 匹配得出人脸坐标int(x)-10 if num%2==0 else int(x)+10
            face_pos = list(str(rect).replace('[(','').replace(') (',',').replace(')]','').replace(' ','').split(','))
            # str转为int
            # print(face_pos)
            face_pos = list(map(lambda x:int(x) ,face_pos))
            # 从图像中切割出人脸部分
            face_spilt(_image,face_pos)


def face_spilt(_image,face_pos,_path=None):
    _img = Image.open(_image)
    _face = _img.crop(face_pos )
    # _face.show()
    if not _path:
        _session_id = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + str(random.randint(0,9))
        _path = './Face_img/cv/split/{}.png'.format(_session_id)
    _face.save(_path)
    print('捕获人脸成功，保存在：\n    {}'.format(_path))
    # 从百度人脸库中搜索人脸
    face_search(_path)
    # _face.show()

def get_requrl(_url):
    __token = '?access_token=24.1cfd5fdd87d1868dc05ddbf033663423.2592000.1572447440.282335-17376947'
    return _url + __token

def face_search(_path):

    __url = 'https://aip.baidubce.com/rest/2.0/face/v3/search'
    __url = get_requrl(__url)
    data = {}
    data['image'] = media_to_bs64(_path)
    data['image_type'] = 'BASE64'
    data['group_id_list'] = 'friends,classmates_high,manager'
    res = requests.post(__url,data)
    answer = json.loads(res.text)
    print(answer)
    if not answer['error_code']:
        answer = answer['result']['user_list'][0]
        next_deal(answer['group_id'],answer['user_id'],answer['score'])

def get_token():
    __url = 'https://aip.baidubce.com/oauth/2.0/token'

    _data = {}
    _data['grant_type'] = 'client_credentials'
    _data['client_id'] = APIKEY
    _data['client_secret'] = SECRETKEY
    print(requests.post(__url,_data).text)



def video_to_image():
    cap = cv.VideoCapture(0)
    flag = True
    start_time = time.time()
    files = list(map(lambda i:'check'+str(i),range(1,21)))
    index = 0
    while flag:
        ret, frame = cap.read()
        if ret:
            # gray = cv.cvtColor(frame,cv.IMREAD_COLOR)
            cv.imshow('show',frame)
            new_time = time.time()
            interval = new_time-start_time
            if interval > 1.5:
                start_time = new_time
                _path = r'./Face_img/cv/source/{}.png'.format(files[index])
                cv.imwrite(_path,frame)
                index += 1
                if index >= len(files):
                    index = 0
                p = mlp.Process(target=get_face_location_cv,args=(_path,))
                p.start()
            if cv.waitKey(1) == ord('q'):
                break

    cap.release()
    cv.destroyAllWindows()

def tts(_text):
    speech = AipSpeech(APPID,APIKEY,SECRETKEY)
    result = speech.synthesis(_text,'zh',1,{'vol':5})

    with open('./tts.wav','wb') as f:f.write(result)
    # playsound.playsound(result)
    print(result)

def media_to_bs64(media):
    with open(media, 'rb') as f:return base64.b64encode(f.read()).decode()

def next_deal(*args):
    if args[2] > 85:
        print(args[1])


if __name__ == '__main__':
    image = r'C:\Users\BING\Desktop\20190930-000234.png'
    # FaceCheck().video_to_image()
    # Face = FaceCheck()
    # answer = Face.API.search(media_to_bs64(image),'BASE64','classmates_high,friends')
    # print(answer)
    video_to_image()
    # tts('你好')
