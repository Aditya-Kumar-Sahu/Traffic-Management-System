import cv2
import argparse
import numpy as np
import supervision as sv
from ultralytics import YOLO

# Video output codec
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
print(fourcc)
ZONE_POLYGON = np.array([
    [0,0],
    [900,0],
    [900, 880],
    [0, 880]
])

def parse_arg() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 Live")
    parser.add_argument(
        "--webcam-resolution",
        default=[1080, 720],
        nargs=2, 
        type=int
    )
    args = parser.parse_args()
    return args

args = parse_arg()
frame_width, frame_height = args.webcam_resolution
    
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("test.mp4")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
out = cv2.VideoWriter('result.mp4', fourcc, 25.0, (frame_width, frame_height))

model = YOLO("model_files/yolov8n.pt")
box_annotator = sv.BoxAnnotator(
    thickness = 2,
    text_thickness = 2,
    text_scale = 1
)

zone = sv.PolygonZone(polygon = ZONE_POLYGON, frame_resolution_wh = tuple(args.webcam_resolution))
zone_annotator = sv.PolygonZoneAnnotator(zone = zone, color = sv.Color.RED)

while True:
    ret, frame = cap.read()
    if not ret: break
    result = model(frame)[0]
    detections = sv.Detections.from_ultralytics(result)  

    frame = box_annotator.annotate(scene = frame, detections = detections) 
    zone.trigger(detections = detections)
    frame = zone_annotator.annotate(scene = frame)
    out.write(frame)
    cv2.imshow("yolov8",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
