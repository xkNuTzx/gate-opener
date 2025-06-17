import cv2, json, time
import numpy as np
import tflite_runtime.interpreter as tflite
import RPi.GPIO as GPIO

# Load config
with open("config.json") as f:
    cfg = json.load(f)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(cfg["gpio_pin"], GPIO.OUT)
GPIO.output(cfg["gpio_pin"], GPIO.LOW)

# Load model
model = cfg["model"]
interpreter = tflite.Interpreter(model_path=f"model/{model}")
interpreter.allocate_tensors()
inp, outp = interpreter.get_input_details(), interpreter.get_output_details()

# Open RTSP
cap = cv2.VideoCapture(cfg["rtsp_url"])

def trigger():
    GPIO.output(cfg["gpio_pin"], GPIO.HIGH)
    time.sleep(cfg.get("trigger_duration", 2))
    GPIO.output(cfg["gpio_pin"], GPIO.LOW)

while True:
    ret, frame = cap.read()
    if not ret:
        time.sleep(1)
        continue
    img = cv2.resize(frame, (inp[0]["shape"][2], inp[0]["shape"][1]))
    img = np.expand_dims(img.astype("float32") / 255.0, 0)

    interpreter.set_tensor(inp[0]["index"], img)
    interpreter.invoke()
    score = interpreter.get_tensor(outp[0]["index"])[0][0]

    print("SCORE:", score)
    if score > cfg.get("threshold", 0.9):
        print("MATCH → triggering")
        trigger()
        time.sleep(cfg.get("cooldown", 10))
