import RPi.GPIO as GPIO
import time,sys,cv2
from tflite_support.task import core,vision

def classify(model, labels, image): # -> (label, probability)
    
    # classifier에 사용할 모델 설정
    classifier_options = vision.ImageClassifierOptions(
        base_options=core.BaseOptions(file_name=model))
    classifier = vision.ImageClassifier.create_from_options(classifier_options)
    
    # 텐서플로우 이미지로 변환
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    tensor_image = vision.TensorImage.create_from_array(rgb_image)
    
    # 분류 실행
    result = classifier.classify(tensor_image)
    
    # 결과 정리
    category = result.classifications[0].categories[0]
    #category_name = labels[category.index]
    probability = round(category.score, 2)
    
    return (category.index, probability)

Button=16

GPIO.setmode(GPIO.BCM)
GPIO.setup(Button, GPIO.IN)

button_flag='HIGH'

# 모델파일 지정
model = 'model.tflite'
# 레이블 파일을 읽어 리스트로
f = open('labels.txt', 'r')
labels = f.readlines()
f.close()


while True:
   cap = cv2.VideoCapture(0) # 첫번째 카메라 사용해 영상 캡쳐 
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 224) # 가로 224px
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 224) # 세로 224px
   state = GPIO.input(Button)
   if state == GPIO.HIGH:
      if button_flag=='HIGH':
         success, image = cap.read()
         if not success: # 오류시 프로그램 종료
             sys.exit('ERROR: Unable to read from webcam. Please verify your webcam settings.')
         prediction = classify(model, labels, image)
         print(prediction[0],prediction[1])
         if (prediction[0]==0 and prediction[1]>0.7): # 정답에 해당되는 인덱스 0이면서 확률도 70% 이상일 때만 통과
            LED = 24
            GPIO.setup(LED, GPIO.OUT)
            for i in range(0,3): # 초록 불
               GPIO.output(LED, GPIO.HIGH)
               time.sleep(1)
               GPIO.output(LED, GPIO.LOW)
               time.sleep(1)
         else:
            LED = 23
            GPIO.setup(LED, GPIO.OUT)
            for i in range(0,3): # 빨간 불
               GPIO.output(LED, GPIO.HIGH)
               time.sleep(1)
               GPIO.output(LED, GPIO.LOW)
               time.sleep(1)
   if cv2.waitKey(1) == 27:
        break
   time.sleep(0.1)
   cap.release() # 영상 캡쳐 중지
GPIO.cleanup()
cv2.destroyAllWindows() # 윈도우 닫기