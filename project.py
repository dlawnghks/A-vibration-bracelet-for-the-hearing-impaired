import sys
import time
import speech_recognition as sr
import RPi.GPIO as GPIO

# GPIO 핀 번호 설정
MOTOR_PIN = 17

# GPIO 설정 함수
def initialize_motor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTOR_PIN, GPIO.OUT)
    GPIO.output(MOTOR_PIN, GPIO.LOW)  # 초기 상태를 꺼짐으로 설정

# 진동 모터를 작동시키는 함수
def activate_motor(duration):
    GPIO.output(MOTOR_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(MOTOR_PIN, GPIO.LOW)

# 진동 모터를 반복적으로 작동시키는 함수
def pulse_motor(count, pulse_duration, pause_duration):
    for _ in range(count):
        GPIO.output(MOTOR_PIN, GPIO.HIGH)
        time.sleep(pulse_duration)
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        time.sleep(pause_duration)

# 마이크를 통해 음성을 인식하고 특정 단어를 찾는 함수
def listen_for_keywords(keywords):
    recognizer = sr.Recognizer()
    device_index = 0  # 사용할 마이크 장치 인덱스

    with sr.Microphone(device_index=device_index) as source:
        print("마이크를 통해 말하세요...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # 주변 소음 보정
        try:
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=2)
        except sr.WaitTimeoutError:
            print("시간 초과로 인해 음성을 들을 수 없습니다.")
            return ""

    try:
        recognized_text = recognizer.recognize_google(audio, language='ko-KR')
        print("인식된 텍스트:", recognized_text)
        return recognized_text
    except sr.UnknownValueError:
        print("음성을 이해할 수 없습니다.")
        return ""
    except sr.RequestError as error:
        print(f"Google API 요청 오류: {error}")
        return ""

# 메인 실행 코드
if __name__ == "__main__":
    # 트리거 및 경고 단어 목록 설정
    trigger_keywords = ["안녕", "저기"]
    alert_keywords = ["조심", "위험"]

    # 모터 초기화
    initialize_motor()

    while True:
        spoken_text = listen_for_keywords(trigger_keywords + alert_keywords)
        if any(keyword in spoken_text for keyword in trigger_keywords):
            print("트리거 단어가 감지되었습니다. 진동 모터를 활성화합니다.")
            activate_motor(3)  # 3초 동안 진동
        elif any(keyword in spoken_text for keyword in alert_keywords):
            print("경고 단어가 감지되었습니다. 진동을 짧게 여러 번 실행합니다.")
            pulse_motor(3, 1, 0.5)  # 1초 진동, 0.5초 간격으로 3회 반복
        else:
            print("지정된 단어가 감지되지 않았습니다.")
        time.sleep(0.1)  # 다음 청취 전 짧은 대기
