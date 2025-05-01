from ultralytics import YOLO
import cv2
from PIL import Image
import os

model = YOLO("yolov8n.pt")

def detect_horses(image_path):
    results = model.predict(image_path, classes=17)
    count = len(results[0].boxes)
    plotted = results[0].plot()[:, :, ::-1]  # Конвертация BGR в RGB
    return count, Image.fromarray(plotted)

def process_video(input_path):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_path = os.path.join(os.path.dirname(input_path), f"processed_{os.path.basename(input_path)}")
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        results = model.predict(frame, classes=17)
        annotated_frame = results[0].plot()
        out.write(annotated_frame)
    
    cap.release()
    out.release()
    return output_path