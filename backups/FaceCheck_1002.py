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
import os
import pickle
import random
import re
import sys
import time
from urllib.parse import quote_plus

import cv2 as cv
import numpy as np
import dlib
import requests
from PIL import Image
import multiprocessing as mlp
from baidu_aip import AipSpeech
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl



class FaceCheck(object):

    def __init__(self,app_id=None,api_key=None,secretkey=None):
        """
        人脸检测程序，调用设备摄像头，提取图像中的人脸，并与百度人脸库中的人脸数据进行比对
        :param app_id:
        :param api_key:
        :param secretkey:
        """
        # 画面获取进程存入图像，人脸检测进程读取图像
        self.Pictures = mlp.Queue(20)
        # 初始化用户信息
        self.UserInfo = {}
        if os.path.exists('./config.pkl'):
            with open('./config.pkl','rb') as f:self.UserInfo = pickle.load(f)
        self.UserInfo['APPID'] = self.UserInfo['APPID'] if 'APPID' in self.UserInfo.keys() else '17376947'
        self.UserInfo['APIKEY'] = self.UserInfo['APIKEY'] if 'APIKEY' in self.UserInfo.keys() else 'K7G0KLcoQnTLH4QjmCZMigyM'
        self.UserInfo['SECRETKEY'] = self.UserInfo['SECRETKEY'] if 'SECRETKEY' in self.UserInfo.keys() else 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL'
        self.UserInfo['AccessToken'] = self.UserInfo['AccessToken'] if 'AccessToken' in self.UserInfo.keys() else "None" #语音合成添加参数时，避免布尔判断为空，丢掉参数

        self.APPID = app_id if app_id else self.UserInfo['APPID']
        self.APIKEY = api_key if api_key else self.UserInfo['APIKEY']
        self.SECRETKEY = secretkey if secretkey else self.UserInfo['SECRETKEY']
        self.AccessToken = self.UserInfo['AccessToken']

        # self.APPID = '17376947' if not app_id else app_id
        # self.APIKEY = 'K7G0KLcoQnTLH4QjmCZMigyM' if not api_key else api_key
        # self.SECRETKEY = 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL' if not secretkey else secretkey
        # self.AccessToken = '24.1cfd5fdd87d1868dc05ddbf033663423.2592000.1572447440.282335-17376947'#7





    def get_face_location_cv(self,_Q):
        """
        人脸检测线程
        :param _Q:
        :return:
        """
        while True:
            if _Q.empty():continue
            else:
                _image = _Q.get()
                detector = dlib.get_frontal_face_detector()
                # 已经是RGB
                _img = cv.imdecode(_image,1)
                img_rgb = cv.cvtColor(_img,cv.COLOR_BGR2RGB)
                img = cv.cvtColor(_img,cv.COLOR_BGRA2GRAY)
                rects = detector(_img,1)
                print(rects)
                if rects:
                    print('正在进行人脸处理')
                    _session_id = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + str(random.randint(0, 9))
                    _path_img = './Face_img/cv/source/{}.png'.format(_session_id)
                    cv.imwrite(_path_img,_img)
                    for rect in rects:
                        # 匹配得出人脸坐标int(x)-10 if num%2==0 else int(x)+10
                        # face_pos = list(str(rect).replace('[(','').replace(') (',',').replace(')]','').replace(' ','').split(','))
                        # str转为int
                        face_pos = [rect.left()-20,rect.top()-20,rect.right()+20,rect.bottom()+20]
                        print(face_pos)
                        # 从图像中切割出人脸部分
                        self.face_spilt(img_rgb,face_pos)
                else:
                    print('没有发现人脸信息')


    def face_spilt(self,_image,face_pos):
        """
        传入原图像和人脸位置数据，切割人脸图像并保存
        :param _image:
        :param face_pos:
        :return:
        """
        _session_id = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + str(random.randint(0, 9))
        _path_face = './Face_img/cv/split/{}.png'.format(_session_id)
        _img = Image.fromarray(_image)
        _face = _img.crop(face_pos)
        _face.save(_path_face)
        # 从百度人脸库中搜索人脸
        self.face_search(_path_face)
        # _face.show()


    def face_search(self,_path):
        """
        传入人脸图像路径，从人脸库中搜索人脸
        :param _path:
        :return:
        """
        _url = 'https://aip.baidubce.com/rest/2.0/face/v3/search'
        _data = self._make_req_params(image=_path, image_type='BASE64', group_id_list= 'friends,classmates_high,manager')
        res = self._Request_post(self._get_requrl(_url),_data)
        try:
            answer = json.loads(res.text)
            if not answer['error_code']:
                answer = answer['result']['user_list'][0]
                if int(answer['score']) >= 80:
                    self.next_deal()
                    print(answer['group_id'],answer['user_id'],answer['score'])
        except Exception as err:
            print(err)


    def video_to_image(self,_Q):
        """
        画面获取线程
        :param _Q:
        :return:
        """
        cap = cv.VideoCapture(0)
        start_time = time.time()
        while True:
            # frame是RGB的颜色模式
            ret, frame = cap.read()
            if ret:
                # gray = cv.cvtColor(frame,cv.IMREAD_COLOR)
                cv.imshow('show',frame)
                new_time = time.time()
                interval = new_time-start_time
                if interval > 1.5:
                    start_time = new_time
                    img_content = cv.imencode('.png',frame,[1,100])
                    _Q.put(img_content[1])
                if cv.waitKey(10) == ord('q'):break
                # cv.waitKey(1)

        cap.release()
        cv.destroyAllWindows()

    def _Request_post(self,_url,_data):
        """
        自定义网络请求，自动处理token失效问题
        :param _url:
        :param _data:
        :return:
        """
        _res = requests.post(_url,_data)
        _rec = None
        try:
            _ret = json.loads(_res.text)
            if "error_code" in _ret.keys():_rec = int(_ret['error_code'])
            elif 'err_subcode' in _ret.keys():_rec = int(_ret['err_subcode'])
        except Exception as e:
            print(e)
        if _rec == 100 or _rec == 110 or _rec == 111 or _rec == 16:
            print('ACCECC_TOKEN失效')
            # 重新获取access_token
            self.get_token()
            # 更新数据中的access_token
            if '?access_token=' in _url:
                re_tok = re.compile('\?access_token=(.*)')
                tok = re.findall(re_tok, _url)[0]
                _url = _url.replace(tok,self.AccessToken)
            if 'tok' in _data.keys():
                print('in')
                _data['tok'] = self.AccessToken
            # 重新执行一次访问请求
            return self._Request_post(_url,_data)
        return _res


    def _get_requrl(self,_url):
        """
        传入url，整合acesstoken后返回
        :param _url:
        :return:
        """
        return '{}?access_token={}'.format(_url,self.AccessToken)


    def get_token(self):
        """
        获取ACESSTOKEN
        :return:
        """
        print('正在获取ACCESS_TOKEN')
        _url = 'https://aip.baidubce.com/oauth/2.0/token'
        _data = self._make_req_params()
        _res = self._Request_post(_url,_data)
        _answer = json.loads(_res.text)
        self.AccessToken = _answer['access_token']
        self.UserInfo['AccessToken'] = self.AccessToken
        TokenAlTime = int(_answer['expires_in']) + int(time.time())
        with open('./config.pkl', 'wb') as f: pickle.dump(self.UserInfo,f)
        print(self.AccessToken)
        print('获取ACCECC_TOKEN成功')

    def media_to_bs64(self,media):
        with open(media, 'rb') as f:return base64.b64encode(f.read()).decode()


    def _make_req_params(self,**kwargs):
        """
        百度API请求参数处理
        :param kwargs:
        :return:
        """
        _data = {'grant_type': 'client_credentials', 'client_id': self.APIKEY, 'client_secret': self.SECRETKEY}
        for arg in kwargs:
            if arg == 'tok': kwargs[arg] = kwargs[arg] if kwargs[arg] else self.AccessToken
            if arg == 'image': kwargs[arg] = self.media_to_bs64(kwargs[arg])
            if arg == 'tex': kwargs[arg] = quote_plus(kwargs[arg])
            if kwargs[arg]:
                _data[arg] = kwargs[arg]
        return _data


    def TTS(self,text,spd=None,pit=None,vol=None,per=None,aue=None,tok=None):
        """
        :param text: 待合成文本
        :param spd: 语速
        :param pit: 音调
        :param vol: 音量
        :param per: 发音人
        :param aue: 音频格式
        :param tok: access_token
        :return:
        """
        per = 111
        _url = 'http://tsn.baidu.com/text2audi'
        _url2 = ' https://tsn.baidu.com/text2audio'
        _cuid = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + str(random.randint(0, 9))
        _data = self._make_req_params(tex=text,spd=spd,pit=pit,vol=vol,per=per,aue=aue,tok=tok,cuid=_cuid,ctp=1,lan='zh')
        res = self._Request_post(_url2, _data)
        with open('tts.mp3','wb') as f:f.write(res.content)
        os.startfile('tts.mp3')



    def Run(self):
        """
        启动人脸检查进程
        :return:
        """
        P1 = mlp.Process(target=self.get_face_location_cv,args=(self.Pictures,))
        P2 = mlp.Process(target=self.video_to_image,args=(self.Pictures,))
        P1.start()
        P2.start()

    def next_deal(self):
        self.play_media('welcome.wav')

    def play_media(self,_file):
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.playlist.addMedia(QMediaContent(QUrl(_file)))
        self.player.play()
        while True:
            play_time = self.player.position()
            time.sleep(0.1)
            if play_time == self.player.position() and play_time != 0:
                break


if __name__ == '__main__':
    APP = FaceCheck()
    APP.Run()
    # APP.TTS(text='欢迎回来')
    # APP.next_deal()