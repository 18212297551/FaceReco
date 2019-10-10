"""

https://y.qq.com/portal/search.html#page=1&searchid=1&remoteplace=txt.yqq.top&t=song&w=%E8%A1%A8%E6%80%81
http://mirrors.aliyun.com/pypi  # /simple/pygame/

eyJhcHAtdmVyc2lvbiI6IjIuMy41IiwieWljbGVhci1ncm91cHMiOiJbe1wiZmlsdGVySWRcIjoxMTEsXCJ0aXRsZVwiOlwiQ2hpbmFMaXN0VjIuMFsyMDE5MDgxNDAwMV1cIixcInN1YnNjcmlwdGlvblVybFwiOlwiaHR0cDovL3Rvb2xzLnlpY2xlYXIuY29tL0NoaW5hTGlzdDIuMC50eHRcIixcImhvbWVwYWdlXCI6XCJodHRwOi8vd3d3LnlpY2xlYXIuY29tXCIsXCJwcmVmaXhlc1wiOm51bGwsXCJhdXRob3JcIjpcInlpY2xlYXJAYWxpeXVuLmNvbVwiLFwibGFzdFVwZGF0ZVRpbWVcIjoxNTcwMDMxMzEwOTU5LFwiUnVsZUNvdW50XCI6MTM2NjQsXCJ2ZXJzaW9uXCI6XCIyMDE5MDgxNDAwMVwiLFwiaW5zdGFsbGVkXCI6dHJ1ZX1dIiwiYXV0by11cGRhdGUiOmZhbHNlLCJkaXNhYmxlLWRldmVsb3BlciI6ZmFsc2UsInNob3cteW91a3UtZGFubXUiOnRydWUsImRpc2FibGUtdXBkYXRlLWZpbHRlci1maXJzdHJ1biI6ZmFsc2UsImZpbHRlcnMtc3RhdGUiOiJ7XCIxMTFcIjp7XCJlbmFibGVkXCI6ZmFsc2UsXCJpbnN0YWxsZWRcIjp0cnVlfX0iLCJwYWdlLXN0YXRpc3RpYyI6IntcInRvdGFsQmxvY2tlZFwiOjc0fSIsInNob3ctdGFiLWljb24tYmxvY2siOmZhbHNlfQ==

https://files.pythonhosted.org/

"""
import sys

# import pygame
import base64
import time

import eyed3
import librosa
import requests
from pydub.utils import mediainfo
from pydub import AudioSegment
import traceback
import baidu_aip

def catch_err():
    pass

file = r'D:\XiaoU\Download\SpeechSynthesis\001.mp3'
file2 = r'D:\XiaoU\Download\SpeechSynthesis\7.wav' # audio/x-wav audio/mpeg
sa = 'D:\XiaoU\Download\SpeechSynthesis\qq\q1.wav'
import os



url = 'https://aiapi.jd.com/jdai/tts'


"""
def _make_req_params(_key=False, **kwargs):

    百度API请求参数处理
    :param kwargs:
    :return:

    # '17376947', 'K7G0KLcoQnTLH4QjmCZMigyM', 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL'
    _data = {'grant_type': 'client_credentials', 'client_id': 'K7G0KLcoQnTLH4QjmCZMigyM', 'client_secret': 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL',
             'cuid': 2019100311}
    for arg in kwargs:
        if arg == 'tok':
            _data[arg] = kwargs[arg] if kwargs[arg] else self.AccessToken
        elif arg == 'image':
            _data[arg] = self.media_to_bs64(kwargs[arg])
        elif arg == 'token':
            _data[arg] = kwargs[arg] if kwargs[arg] else self.AccessToken
        elif arg == 'tex':
            _data[arg] = quote_plus(kwargs[arg])
        elif arg == 'speech':
            with open(kwargs[arg], 'rb') as f:
                speech = f.read()
                _data[arg] = base64.b64encode(speech).decode()
                _data['len'] = len(speech)
        else:
            if kwargs[arg]:
                _data[arg] = kwargs[arg]
    return _data
f = r'D:\XiaoU\Download\SpeechSynthesis\123.wav'
f2 = r'D:\XiaoU\Deal\Voice\Reco\P125.wav'
# f2 = open(f2,'rb')



__ttsUrl = 'http://tsn.baidu.com/text2audio'
__asrUrl = 'http://vop.baidu.com/server_api'
token = "24.db9b8bb237b3dc364e22bd5526871bb6.2592000.1572765301.282335-17376947"
def t():
    data = baiduaip.AipSpeech('17376947', 'K7G0KLcoQnTLH4QjmCZMigyM', 'xqdTGx6mMB6pu3WtD9c0r8yX9Sxy0OiL').asr(speech=f2.read(),format = 'wav',rate=16000)

    print(data)
t()
# sec = mediainfo(file)
# print(sec)

# me = AudioSegment.from_file(file,format='wav')

# print(123,me[90*1000:92*1000].export('./ss.wav',format='wav')[0])
# print(time.localtime())

# voice = eyed3.load(file2)
# sec = voice.info.time_secs
print(sec)
with open(file,'rb') as f:
    contents = f.read()
    contents_len = len(contents)
    print(contents_len)
    content_list = []
    f.seek(0)
    if sec > 55:
        unit_content = int(contents_len/sec)*50
        num = 0
        print(unit_content)
        while contents_len:
            pre_content = f.read(unit_content) if unit_content < contents_len else f.read()
            content_list.append(pre_content)
            contents_len -= len(pre_content)

            with open(r'D:\XiaoU\Download\SpeechSynthesis\7{}.wav'.format(num), 'wb') as f2:
                f2.write(pre_content)
            num += 1
            # break
    # else:content_list.append(f.read())
    # with open(file2,'wb') as f2:
    #     list(map(lambda content:f2.write(content),content_list))
"""