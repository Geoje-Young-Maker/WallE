from picamera2 import Picamera2
import tflite_runtime.interpreter as tflite
#sudo apt update
#sudo apt install python3-pip -y
#pip install --upgrade pip
#pip install --extra-index-url https://google-coral.github.io/py-repo/ tflite-runtime -> 라즈베리파이 터미널에서. 
import serial
import time
import random
import numpy as np

### VNC에서 프로그램 실행 전 터미널에 source myenv/bin/activate로 가상환경 활성화하기 ###

#딥러닝 모델 (가벼운 버전)
interpreter = tflite.Interpreter(model_path="yolov8n_int8.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#사물 코드에 대응되는 라벨
labels = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
    "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "TV",
    "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
    "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
    "scissors", "teddy bear", "hair drier", "toothbrush"
]

#포트 연결
sr = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.1) #baudrate: 통신 속도, 아두이노와 같은 값이어야 함.
time.sleep(2) #연결 대기

#전송 리스트: 모터상태, 속도, LCD
send = [0 for i in range(3)]

#월E 작동 함수
def wakeup(): #일어나는 모션
    pass 
def walk(speed): #speed의 속도로 전진 (speed < 0: 후진)
    global send
    if speed > 0: 
        send[0] = '1'
        send[1] = speed
    elif speed < 0:
        send[0] = '2'
        send[1] = -speed
def turn(degree): #degree의 각도로 회전 (+는 시계, -는 반시계)
    global send
    if degree > 0:
        send[0] = '3' #우회전
        send[1] = degree / 360
    elif degree < 0:
        send[0] = '4' #좌회전
        send[1] = abs(degree) / 360

#카메라: 사람 & 사물 인식 (반복 실행)
cam = Picamera2()
preview_config = cam.create_preview_configuration(main={"size": (320, 320)})
cam.configure(preview_config)
cam.start()

#시리얼 데이터 입력
while True:
    send = [0 for i in range(3)]
    data = sr.readline()

    frame = cam.capture_array()
    frame = frame[:, :, :3]
    input_dtype = input_details[0]['dtype'] 
    if input_dtype == np.float32: #타입이 float인 경우만 float으로 입력
        input_data = np.expand_dims(frame / 255.0, axis=0).astype(np.float32)
    else:
        input_data = np.expand_dims(frame, axis=0).astype(np.uint8)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])[0]
    boxes = output[:, :4] #4번째까지는 객체의 xywh좌표, 이후엔 80개의 클래스 정보 (아마도?) -> 4번째 기준으로 슬라이싱
    scores = np.max(output[:, 4:], axis=1)
    classes = np.argmax(output[:, 4:], axis=1)

    if not data and boxes.shape[0] == 0: #데이터 들어올 때까지 반복
        continue

    if data:
        #머신 러닝이 아닌 모션은 자연스러움을 더하기 위해 랜덤 모듈을 사용하는 게 좋을 듯.
        line = eval(data.decode('utf-8', errors='replace').strip()) #디코딩 및 공백문자 제거 + eval()
        dist = (line[0], line[1])

        #초음파 센서 거리 값.
        if dist[0] <= 15: #사물과의 거리가 15cm 이하일 때 (변경 가능)
            #거리가 가까울 경우 할 수 있는 모션은 2가지
            motion = random.randint(1, 2)
            if motion == 1:
                turn(random.randint(-360, 360)) #무작위 방향, 각도로 회전
            elif motion == 2:
                if dist[1] > dist[0]:
                    turn(180)
        else:
            walk(0.5) #전진 - 속도나 시간 등은 랜덤하게 변경 가능
    
    if boxes.shape[0] != 0:
        #사람 인식 시 실행할 코드: 각 객체 상자의 (좌상단, 우하단) 좌표는 boxes list에 있음.
        max_score = 0
        for i in range(len(boxes)):
            xywh = boxes[i]
            cls = classes[i]
            if scores[i] > scores[max_score]:
                max_score = i
            
            if cls == 0 and scores[i] > 0.5:  # 사람
                if xywh[0] > 0.5:
                    turn(10) #매 실행마다 작동 - 각 상태에 따라 회전을 반복함.
                elif xywh[0] < 0.5:
                    turn(-10)
                    
            elif scores[i] > 0.5: # 사물
                time.sleep(random.randint(1,5)) #일정 시간 주시 후 리턴하는 코드;
        
        if scores[max_score] > 0.5:
            send[2] = labels[int(classes[max_score])]

    send_data = ",".join(map(str, send)) + "\n"
    sr.write(send_data.encode("utf-8")) #데이터들을 쉼표로 구분해 전송
