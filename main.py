import os
import cv2
import numpy as np
import tensorflow as tf
import time
import torch

from human_app import get_hum
from ppe_app import get_xyxy

from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tool import generate_detections as gdet

video_path   = "static/vid4.mp4"

def Object_tracking(video_path, output_path = '', input_size=416, show=False):
    # Definition of the parameters
    max_cosine_distance = 0.5
    nn_budget = None
    
    #initialize deep sort object
    model_filename = 'model_data/mars-small128.pb'
    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
    tracker = Tracker(metric)
    encoder = gdet.create_box_encoder(model_filename)

    times = []

    if video_path:
        vid = cv2.VideoCapture(video_path) # detect on video
    else:
        vid = cv2.VideoCapture(0) # detect from webcam

    # by default VideoCapture returns float instead of int
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    codec = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, codec, fps, (width, height)) # output_path must be .mp4
    
    dictOfModels = {}
    listOfKeys = []
    for r, d, f in os.walk("model_data"):
        for file in f:
            if ".pt" in file:
                torch.hub._validate_not_a_forked_repo=lambda a,b,c: True
                dictOfModels[os.path.splitext(file)[0]] = torch.hub.load('ultralytics/yolov5', 'custom', path=os.path.join(r, file),)
        for key in dictOfModels :
            listOfKeys.append(key)
    
    with open('model_data/coco.names', 'r') as f:
        classes = f.read().splitlines()
    
    net = cv2.dnn.readNetFromDarknet('model_data/yolov4.cfg', 'model_data/yolov4.weights')
    
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)
    
    frame = 0;
    
    
    while True:
        
        _, img = vid.read()
        
        if frame%15 == 0:
            boxes, scores, names = [],[],[]
            for bb in get_hum(img,model):
                boxes.append(bb[2])
                scores.append(bb[1])
                names.append(bb[0])
            
            boxes = np.array(boxes) 
            names = np.array(names)
            scores = np.array(scores)
            features = np.array(encoder(img, boxes))
            detections = [Detection(bbox, score, feature) for bbox, score, class_name, feature in zip(boxes, scores, names, features)]
            
            # Pass detections to the deepsort object and obtain the track information.
            tracker.predict()
            tracker.update(detections)

            for track in tracker.tracks:
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue 
                id = track.track_id
                bb = track.to_tlbr()
                
                classs = "person_no_helmet"
                bboxes = get_xyxy(img,dictOfModels)
                
                for bbox in bboxes:
                    
                    col1 = (int(bbox[0]) > bb[0] and int(bbox[1]) > bb[1]) or (int(bbox[2]) > bb[0] and int(bbox[3]) > bb[1]) 
                    col2 = (int(bbox[0]) < bb[2] and int(bbox[1]) < bb[3]) or (int(bbox[2]) < bb[2] and int(bbox[3]) < bb[3]) 
                    
                    if (col1 and col2) and bbox[4] > 0.65:
                        img= cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255,10,50), 1)
                        classs = "person_with_helmet"
                img = cv2.rectangle(img, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), (36+id*50,255-id*50,12+id*25), 1)
                cv2.putText(img, f'{classs} -- {id}', (int(bb[0]), int(bb[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36+id*50,255-id*50,12+id*25), 2)
            
            if show:
                cv2.imshow('output', img)
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    break
        frame += 1
    cv2.destroyAllWindows()

Object_tracking( video_path, '', show=True)


