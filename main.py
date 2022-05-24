from ast import arg

import time

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import cv2
from cv2 import mean
import numpy as np
import tensorflow as tf
import time
import torch
import threading

from tool.human_app import get_hum
from tool.ppe_app import get_xyxy

from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tool import generate_detections as gdet


class CVTrackThread(threading.Thread):
    def __init__(self,video_path,id,db,dbmodel):
        
        print("Building class...")
        
        self.db = db
        self.dbmodel = dbmodel
        
        self.video_path = video_path
        if self.video_path:
            self.vid = cv2.VideoCapture(self.video_path) 
        else:
            self.vid = cv2.VideoCapture(0)
        
        
        self.frames = 1
        self.totalFrames = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.id = id
        super().__init__()
        max_cosine_distance = 0.5
        nn_budget = None
                
        model_filename = 'model_data/mars-small128.pb'
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
        self.tracker = Tracker(metric)
        self.encoder = gdet.create_box_encoder(model_filename)

        self.dictOfModels = {}
        self.listOfKeys = []
        for r, d, f in os.walk("model_data"):
            for file in f:
                if ".pt" in file:
                    torch.hub._validate_not_a_forked_repo=lambda a,b,c: True
                    self.dictOfModels[os.path.splitext(file)[0]] = torch.hub.load('ultralytics/yolov5', 'custom', path=os.path.join(r, file),)
            for key in self.dictOfModels :
                self.listOfKeys.append(key)
                
        with open('model_data/coco.names', 'r') as f:
            classes = f.read().splitlines()
            
        self.net = cv2.dnn.readNetFromDarknet('model_data/yolov4.cfg', 'model_data/yolov4.weights')
        self.model = cv2.dnn_DetectionModel(self.net)
        self.model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)
        
        self.time0 = time.time()
        _, img = self.vid.read()
        self.img = cv2.imencode('.jpg', img)[1].tobytes()
        self.img = ''
        self.datastring = ''
        
        width= int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height= int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.out = cv2.VideoWriter(f'static/out{self.id}.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20.0, (width,height))
        
        print("Success!")

    def run(self):
        
        print("Running track...")
        
        while True:
            _, img = self.vid.read()
            
            if self.frames%5 == 0:
                boxes, scores, names = [],[],[]
                for bb in get_hum(img,self.model):
                    boxes.append(bb[2])
                    scores.append(bb[1])
                    names.append(bb[0])
                
                boxes = np.array(boxes) 
                names = np.array(names)
                scores = np.array(scores)
                features = np.array(self.encoder(img, boxes))
                detections = [Detection(bbox, score, feature) for bbox, score, class_name, feature in zip(boxes, scores, names, features)]
                
                # Pass detections to the deepsort object and obtain the track information.
                self.tracker.predict()
                self.tracker.update(detections)
                for track in self.tracker.tracks:
                    if not track.is_confirmed() or track.time_since_update > 1:
                        continue 
                    
                    id = track.track_id
                    bb = track.to_tlbr()
                    
                    classs = "person_no_helmet"
                    bboxes = get_xyxy(img,self.dictOfModels)
                    
                    for bbox in bboxes:
                        
                        col1 = (int(bbox[0]) > bb[0] and int(bbox[1]) > bb[1]) or (int(bbox[2]) > bb[0] and int(bbox[3]) > bb[1]) 
                        col2 = (int(bbox[0]) < bb[2] and int(bbox[1]) < bb[3]) or (int(bbox[2]) < bb[2] and int(bbox[3]) < bb[3]) 
                        
                        if (col1 and col2) and bbox[4] > 0.65:
                            img= cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255,10,50), 1)
                            classs = "person_with_helmet"

                    datastring = str(str(self.frames)) +"_" + str(classs) + "_" + str(track.mean) + "_" + str(track.mean)
                    if not self.dbmodel.query.filter_by(thread_id = self.id,track_id = id).first():
                        self.db.session.add(self.dbmodel(self.id,id,datastring))
                        self.db.session.commit()
                        self.datastring = datastring
                    img = cv2.rectangle(img, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), (36+id*50,255-id*50,12+id*25), 1)
                    cv2.putText(img, f'{classs} -- {id}', (int(bb[0]), int(bb[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36+id*50,255-id*50,12+id*25), 2)
                self.img = cv2.imencode('.jpg', img)[1].tobytes()
                self.out.write(img)
                
            self.frames += 1
            if self.frames >= self.totalFrames:
                print("Success!")
                self.img = 0
                self.datastring = "!"
                self.out.release()
                os.system(f"ffmpeg -i static/out{self.id}.mp4 -c:v h264 static/outp{self.id}.mp4 -hide_banner -loglevel error -y")
                return 0
            