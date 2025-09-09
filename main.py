from picamera2 import Picamera2 #type: ignore (에러 무시 - picamera는 리눅스 전용 모듈임.)
from ultralytics import YOLO
import serial
import time
import random

### VNC에서 프로그램 실행 전 터미널에 source myenv/bin/activate로 가상환경 활성화하기 ###

#딥러닝 모델 (가벼운 버전)
model = YOLO('yolov8n.pt')

#포트 연결
sr = serial.Serial(port='', baudrate=115200, timeout=0.02) #baudrate: 통신 속도, 아두이노와 같은 값이어야 함.
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
    if not data and not results: #데이터 들어올 때까지 반복
        continue

    if data:
        #머신 러닝이 아닌 모션은 자연스러움을 더하기 위해 랜덤 모듈을 사용하는 게 좋을 듯.
        line = eval(data.decode('utf-8', errors='replace').strip()) #디코딩 및 공백문자 제거 + eval()

        gyro = tuple(line[0])
        brightness = line[1]
        dist = tuple(line[2])
        temp_humid = tuple(line[3])

        if brightness < 400: #조도 센서: 점등
            light(0)
        elif brightness >= 400: #조도 센서: 소등
            light(1)


        #자이로 - 수정 필요
        if gyro: #두드림(진동) 감지
            wakeup()


        #초음파 센서 거리 값.
        if dist[0] <= 15: #사물과의 거리가 15cm 이하일 때 (변경 가능)
            #거리가 가까울 경우 할 수 있는 모션은 2가지
            motion = random.randint(1, 2)
            if motion == 1:
                turn(random.randint(-360, 360)) #무작위 방향, 각도로 회전
            elif motion == 2:
                mx = 0
                for i in dist: #가장 거리가 먼 방향 찾음 (곧, 좌우앞뒤 중 막히지 않았거나 그나마 가장 멀리 갈 수 있는 곳을 찾음)
                    if (dist[mx] < dist[i]):
                        mx = i
                if mx == 1:
                    turn(180)
                elif mx == 2:
                    turn(-90)
                elif mx == 3:
                    turn(90)
                else: #그럴리는 없겠지만, 전방 거리가 가장 긴 경우 (월E가 갇힌 경우)
                    turn(360)
        else:
            walk(1, 1) #전진 - 속도나 시간 등은 랜덤하게 변경 가능
    
    if results:
        #사람 인식 시 실행할 코드: 각 객체 상자의 (좌상단, 우하단) 좌표는 boxes list에 있음.
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            
            if cls == 0:  # 사람
                #객체의 상단 끝으로 카메라 각도 조절하는 코드;
                x1, y1, x2, y2 = xyxy #사람 블록의 좌상단xy, 우하단 xy
                #얼굴 쪽을 주시하기 위해, 실제 카메라가 이동해야할 좌표는 블록의 위쪽임. 
                move_pos = tuple((x1+x2)/2, y1)
                if move_pos[0] < 0:
                    turn(10)
                elif move_pos[0] > 0:
                    turn(-10)
                
                if move_pos[1] #작업 중

            else: # 사물
                time.sleep(random.randint(1,5)) #일정 시간 주시 후 리턴하는 코드;
