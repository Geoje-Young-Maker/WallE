from picamera2 import Picamera2 #type: ignore (에러 무시 - picamera는 리눅스 전용 모듈임.)
from ultralytics import YOLO
import serial
import time
import random

### VNC에서 프로그램 실행 전 터미널에 source myenv/bin/activate로 가상환경 활성화하기 ###

#딥러닝 모델 (가벼운 버전)
model = YOLO('yolov8n.pt')

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


#카메라: 사람 & 사물 인식 (반복 실행)
cam = Picamera2()
preview_config = cam.create_preview_configuration(main={"size": (640, 480)})
cam.configure(preview_config)
cam.start()

#시리얼 데이터 입력
while True:
    data = sr.readline()
    frame = cam.capture_array()
    results = model(frame)
    boxes = results[0].boxes

    if data:
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
    
    if results:
        #사람 인식 시 실행할 코드: 각 객체 상자의 (좌상단, 우하단) 좌표는 boxes list에 있음.
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            
            if cls == 0:  # 사람
                #객체의 상단 끝으로 카메라 각도 조절하는 코드;
                x1, y1, x2, y2 = xyxy
            else: # 사물
                pass #일정 시간 주시 후 리턴하는 코드;
