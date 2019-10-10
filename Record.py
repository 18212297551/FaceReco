import re
import time
import wave
import speech
from pyaudio import PyAudio,paInt16
# url = '%259D%25A5&per=111?access_token=24.1cfd5fdd87d1868dc05ddbf033663423.2592000.1572447440.282335'
# speech.say(url)

RATE = 16000 # 采样率
NUM_FRAMES = 16000 # 采样点，一次采样多少，分割采样率

def my_record():
    pa = PyAudio()
    stream = pa.open(format=paInt16,channels=1,rate=RATE,input=True,frames_per_buffer=NUM_FRAMES)
    times = int(time.time()) + 20
    index = 0
    with wave.open('./test.wav','wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        while times >= int(time.time()):
            string = stream.read(NUM_FRAMES)
            print(index)
            index += 1
            f.writeframes(string)
        f.close()

if __name__ == '__main__':
    my_record()







"""

'''D:\application\python37\Lib\site-packages\matlab.py'''
url = '%259D%25A5&per=111?access_token=24.1cfd5fdd87d1868dc05ddbf033663423.2592000.1572447440.282335'
# speech.say(url)

# while True:
#     text = speech.input()
#     print(text)
"""