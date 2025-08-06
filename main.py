from picamera import Picamera #type: ignore (에러 무시 - picamera는 리눅스 전용 모듈임.)
import serial
import time
import random

### VNC에서 프로그램 실행 전 터미널에 source myenv/bin/activate로 가상환경 활성화하기 ###

#포트 연결
sr = serial.Serial(port='', baudrate=0, timeout=1) #baudrate: 통신 속도, 아두이노와 같은 값이어야 함.
time.sleep(2) #연결 대기

#월E 작동 함수
def light(n): #불 키고 끄는 함수 (0: off, 1: on)
    if n == 0:
        pass
    elif n == 1:
        pass
def wakeup(): #일어나는 모션
    pass
def walk(speed, time): #speed의 속도로 time동안 전진 (speed < 0: 후진)
    pass
def turn(degree): #degree의 각도로 회전 (+는 시계, -는 반시계)
    pass

#시리얼 데이터 입력
while True:
    data = sr.readline()
    if not data: #데이터 들어올 때까지 반복
        continue

    #머신 러닝이 아닌 모션은 자연스러움을 더하기 위해 랜덤 모듈을 사용하는 게 좋을 듯.
    line = data.decode('utf-8', errors='replace').strip() #디코딩 및 공백문자 제거
    if line == "light_on": #조도 센서: 점등
        light(0)
    elif line == "light_off": #조도 센서: 소등
        light(1)

    if line == "knock": #두드림(진동) 감지
        wakeup()
    
    if line[:8] == "distance": #초음파 센서 거리 값. 입력 형태는 달라질 수도 있음.
        dist = float(line[8:])
        if dist <= 10: #사물과의 거리가 10cm 이하일 때 (변경 가능)
            #거리가 가까울 경우 할 수 있는 모션은 2가지
            motion = random.randint(1, 2)
            if motion == 1:
                turn(random.randint(-360, 360)) #무작위 방향, 각도로 회전
            elif motion == 2:
                walk(-1, 1) #후진
        else:
            walk(1, 1) #전진 - 속도나 시간 등은 랜덤하게 변경 가능


    #카메라 데이터는 라즈베리파이에 연결함. picamera로 제어 + 입력받은 동영상 데이터를 머신러닝을 통해 분석 & 판단