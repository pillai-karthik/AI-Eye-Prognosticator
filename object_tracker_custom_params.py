from absl import flags
import sys
FLAGS = flags.FLAGS
FLAGS(sys.argv)

import time
import numpy as np
import cv2
import matplotlib.pyplot as plt

import tensorflow as tf
from yolov3_tf2.models import (YoloV3, YoloV3Tiny)
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import convert_boxes

from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet

import math
from itertools import combinations

import os
import datetime


####CUSTOM PARAMETERS############################################################
inputVideo='./inputs/video4.mp4'
# inputVideo='http://192.168.0.25:8080/video'#IP WebCam App
# inputVideo=0
outputVideoName='outputnormal'
outputFolderPath="./outputs/"+outputVideoName+"/"
showClassName=True
showTrackerId=True
showRenderingVideo=True


#******* TINY WEIGHTS *******
isTinyWeight=False

#******* CUSTOM WEIGHTS *******
customWeights=False
if customWeights:
    namesFile='./data/labels/custom.names'
    if isTinyWeight:
        weightsFilePath='./weights/yolov3-tiny-custom.tf'
    else:
        weightsFilePath='./weights/yolov3-custom.tf'
else:
    #Pretrained weights
    namesFile='./data/labels/coco.names'
    if isTinyWeight:
        weightsFilePath='./weights/yolov3-tiny.tf'
    else:
        weightsFilePath='./weights/yolov3.tf'


#******* COUNTING FEATURE (Total Count + Zonal(Band) Count) *******
activateCounting=False
objectsToTrack=["person"]
lineOrientationHorizontal=True
#0.5 Means line will be on middle of video vertically, small is closer to top
bandMidLineWrtHeightOrWidth=0.5
#upperBound is height*upDownBoundWrtMidLine above mid line, similarly, lowerbound. Bigger the number, bigger is the area
upDownBoundWrtMidLine=0.1


#******* TRACKER TAIL FEATURE *******
activateTrackerTail=True
tailLengthInFrames=50
variableThicknessOfTrackerLine=False


#******* INCOMING OUTGOING FEATURE *******
activateIncomingOutgoing=True
objectsTrackInOut=["person"]#["truck","car"]
incomingOutgoingLineHorizontal=True
incomingLineWrtHeightOrWidth=0.37
incomingLineThicknessWrtHeightOrWidth=0.025
outgoingLineWrtHeightOrWidth=0.43
outgoingLineThicknessWrtHeightOrWidth=0.025


#******* SOCIAL DISTANCE FEATURE *******
activateSocialDistance=False
distanceTreshold=75#in pixels


#******* GENERATE HEAT MAP *******
activateHeapMap=True


#############################################################CUSTOM PARAMETERS###


class_names = [c.strip() for c in open(namesFile).readlines()]

if isTinyWeight:
    yolo = YoloV3Tiny(classes=len(class_names))
else:
    yolo = YoloV3(classes=len(class_names))

yolo.load_weights(weightsFilePath)

max_cosine_distance = 0.5
nn_budget = None
nms_max_overlap = 0.8

model_filename = 'model_data/mars-small128.pb'
encoder = gdet.create_box_encoder(model_filename, batch_size=1)
metric = nn_matching.NearestNeighborDistanceMetric('cosine', max_cosine_distance, nn_budget)
tracker = Tracker(metric)

vid = cv2.VideoCapture(inputVideo)

codec = cv2.VideoWriter_fourcc(*'XVID')
vid_fps =int(vid.get(cv2.CAP_PROP_FPS))
vid_width,vid_height = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
os.mkdir(outputFolderPath)
out = cv2.VideoWriter(outputFolderPath+'Video_Output.avi', codec, vid_fps, (vid_width, vid_height))


if activateTrackerTail:
    from _collections import deque
    pts = [deque(maxlen=tailLengthInFrames) for _ in range(1000)]#more the maxlen, more longer is the tracker tail

counter = []
for i in objectsToTrack:
    counter.append([-1])#FOR EACH OBJECT LIKE  PERSON OR CAR, A TOTAL COUNTER IS CREATED


incomingTrackIdsList=[]
outgoingTrackIdsList=[]
incomingCount=[]#in this list, index 0 will contain counts of objectsTrackInOut[0] object
outgoingCount=[]
for i in objectsTrackInOut:
    incomingCount.append(0)
    outgoingCount.append(0)


isFirstImageSaved=False
while True:
    _, img = vid.read()
    if img is None:
        print('COMPLETED')
        break

    if activateHeapMap:
        if isFirstImageSaved!=True:
            FirstFrame=img.copy()
            isFirstImageSaved=True

    img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_in = tf.expand_dims(img_in, 0)
    img_in = transform_images(img_in, 416)

    t1 = time.time()

    boxes, scores, classes, nums = yolo.predict(img_in)

    classes = classes[0]
    names = []
    for i in range(len(classes)):
        names.append(class_names[int(classes[i])])
    names = np.array(names)
    converted_boxes = convert_boxes(img, boxes[0])
    features = encoder(img, converted_boxes)

    detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in
                  zip(converted_boxes, scores[0], names, features)]

    boxs = np.array([d.tlwh for d in detections])
    scores = np.array([d.confidence for d in detections])
    classes = np.array([d.class_name for d in detections])
    indices = preprocessing.non_max_suppression(boxs, classes, nms_max_overlap, scores)
    detections = [detections[i] for i in indices]

    tracker.predict()
    tracker.update(detections)

    cmap = plt.get_cmap('tab20b')
    colors = [cmap(i)[:3] for i in np.linspace(0,1,20)]

    current_count = [0]*len(objectsToTrack)#FOR EACH OBJECT LIKE  PERSON OR CAR, A CURRENT(Band) COUNTER IS CREATED

    centroid_dict=dict()

    for track in tracker.tracks:
        if not track.is_confirmed() or track.time_since_update >1:
            continue
        bbox = track.to_tlbr()
        class_name= track.get_class()
        color = colors[int(track.track_id) % len(colors)]
        color = [i * 255 for i in color]

        cv2.rectangle(img, (int(bbox[0]),int(bbox[1])), (int(bbox[2]),int(bbox[3])), color, 2)
        
        if showClassName and showTrackerId:
            cv2.rectangle(img, (int(bbox[0]), int(bbox[1]-30)), (int(bbox[0])+(len(class_name)+len(str(track.track_id)))*13, int(bbox[1])), color, -1)
            cv2.putText(img, class_name+"-"+str(track.track_id), (int(bbox[0]), int(bbox[1]-10)), 0, 0.5, (255, 255, 255), 1)
        elif showClassName:
            cv2.rectangle(img, (int(bbox[0]), int(bbox[1]-30)), (int(bbox[0])+(len(class_name))*13, int(bbox[1])), color, -1)
            cv2.putText(img, class_name, (int(bbox[0]), int(bbox[1]-10)), 0, 0.5, (255, 255, 255), 1)

        center_y = int(((bbox[1]) + (bbox[3]))/2) 
        center_x = int(((bbox[0]) + (bbox[2]))/2)
        height, width, _ = img.shape

        if activateSocialDistance:
            if class_name=="person":
                centroid_dict[track.track_id]=(int(center_x), int(center_y), int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))

        if activateHeapMap:
            center = (int(((bbox[0]) + (bbox[2]))/2), int(((bbox[1])+(bbox[3]))/2))
            #cv2.line(FirstFrame, int(((bbox[0]) + (bbox[2]))/2),int(((bbox[1])+(bbox[3]))/2), color, 2)
            FirstFrame = cv2.circle(FirstFrame, center, radius=0, color=(0, 0, 255), thickness=1)

#######TRACKER TAIL##################################################################################
        if activateTrackerTail:
            center = (int(((bbox[0]) + (bbox[2]))/2), int(((bbox[1])+(bbox[3]))/2))
            pts[track.track_id].append(center)#pts stores track ids list and inside that list, it has old centres of objects
            for j in range(1, len(pts[track.track_id])):
                if pts[track.track_id][j-1] is None or pts[track.track_id][j] is None:
                    continue
                if variableThicknessOfTrackerLine:
                    thickness = int(np.sqrt(64/float(j+1))*2)
                else:
                    thickness = 2
                cv2.line(img, (pts[track.track_id][j-1]), (pts[track.track_id][j]), color, thickness)
################################################################################TRACKER TAIL#########

#######COUNTING##################################################################################
        if activateCounting:
            if lineOrientationHorizontal:
                #CREATE HORIZONTAL LINES (Zone or band)
                cv2.line(img, (0, int(bandMidLineWrtHeightOrWidth*height+upDownBoundWrtMidLine*height)), (width, int(bandMidLineWrtHeightOrWidth*height+upDownBoundWrtMidLine*height)), (0, 255, 0), thickness=2)
                cv2.line(img, (0, int(bandMidLineWrtHeightOrWidth*height-upDownBoundWrtMidLine*height)), (width, int(bandMidLineWrtHeightOrWidth*height-upDownBoundWrtMidLine*height)), (0, 255, 0), thickness=2)

                if center_y <= int(bandMidLineWrtHeightOrWidth*height+upDownBoundWrtMidLine*height) and center_y >= int(bandMidLineWrtHeightOrWidth*height-upDownBoundWrtMidLine*height):
                    if class_name in objectsToTrack:
                        index=objectsToTrack.index(class_name)
                        current_count[index] += 1
                        counter[index].append(int(track.track_id))
            else:
                #CREATE VERTICAL LINES (Zone or band)
                cv2.line(img, (int(bandMidLineWrtHeightOrWidth*width+upDownBoundWrtMidLine*width), 0), (int(bandMidLineWrtHeightOrWidth*width+upDownBoundWrtMidLine*width), height), (0, 255, 0), thickness=2)
                cv2.line(img, (int(bandMidLineWrtHeightOrWidth*width-upDownBoundWrtMidLine*width), 0), (int(bandMidLineWrtHeightOrWidth*width-upDownBoundWrtMidLine*width), height), (0, 255, 0), thickness=2)

                if center_x <= int(bandMidLineWrtHeightOrWidth*width+upDownBoundWrtMidLine*width) and center_x >= int(bandMidLineWrtHeightOrWidth*width-upDownBoundWrtMidLine*width):
                    if class_name in objectsToTrack:
                        index=objectsToTrack.index(class_name)
                        current_count[index] += 1
                        counter[index].append(int(track.track_id))
#################################################################################COUNTING########

###########INCOMING OUTGOING##############################################################################
        if activateIncomingOutgoing:
            if incomingOutgoingLineHorizontal:
                #Horizontal Orientation
                cv2.line(img, (0, int(incomingLineWrtHeightOrWidth*height+incomingLineThicknessWrtHeightOrWidth*height)), (width, int(incomingLineWrtHeightOrWidth*height+incomingLineThicknessWrtHeightOrWidth*height)), (255, 0, 0), thickness=2)
                cv2.line(img, (0, int(incomingLineWrtHeightOrWidth*height-incomingLineThicknessWrtHeightOrWidth*height)), (width, int(incomingLineWrtHeightOrWidth*height-incomingLineThicknessWrtHeightOrWidth*height)), (255, 0, 0), thickness=2)

                cv2.line(img, (0, int(outgoingLineWrtHeightOrWidth*height+outgoingLineThicknessWrtHeightOrWidth*height)), (width, int(outgoingLineWrtHeightOrWidth*height+outgoingLineThicknessWrtHeightOrWidth*height)), (0, 0, 255), thickness=2)
                cv2.line(img, (0, int(outgoingLineWrtHeightOrWidth*height-outgoingLineThicknessWrtHeightOrWidth*height)), (width, int(outgoingLineWrtHeightOrWidth*height-outgoingLineThicknessWrtHeightOrWidth*height)), (0, 0, 255), thickness=2)

                if class_name in objectsTrackInOut:
                    if center_y <= int(incomingLineWrtHeightOrWidth*height+incomingLineThicknessWrtHeightOrWidth*height) and center_y >= int(incomingLineWrtHeightOrWidth*height-incomingLineThicknessWrtHeightOrWidth*height):
                        #Incoming zone touched
                        objectTrackId=int(track.track_id)
                        if objectTrackId not in incomingTrackIdsList:#Added because multiple same objectTrackId were appended to incomingTrackIdsList because of frames
                            incomingTrackIdsList.append(objectTrackId)
                            if objectTrackId not in outgoingTrackIdsList:
                                index=objectsTrackInOut.index(class_name)
                                incomingCount[index]+=1
                                outgoingTrackIdsList.append(objectTrackId)#Added so that a person is only counted once

                if class_name in objectsTrackInOut:
                    if center_y <= int(outgoingLineWrtHeightOrWidth*height+outgoingLineThicknessWrtHeightOrWidth*height) and center_y >= int(outgoingLineWrtHeightOrWidth*height-outgoingLineThicknessWrtHeightOrWidth*height):
                        #Outgoing zone touched
                        objectTrackId=int(track.track_id)
                        if objectTrackId not in outgoingTrackIdsList:
                            outgoingTrackIdsList.append(objectTrackId)
                            if objectTrackId not in incomingTrackIdsList:
                                index=objectsTrackInOut.index(class_name)
                                outgoingCount[index]+=1
                                incomingTrackIdsList.append(objectTrackId)#Added so that a person is only counted once
            else:
                #Vertical Orientation
                cv2.line(img, (int(incomingLineWrtHeightOrWidth*width+incomingLineThicknessWrtHeightOrWidth*width), 0), (int(incomingLineWrtHeightOrWidth*width+incomingLineThicknessWrtHeightOrWidth*width), height), (255, 0, 0), thickness=2)
                cv2.line(img, (int(incomingLineWrtHeightOrWidth*width-incomingLineThicknessWrtHeightOrWidth*width), 0), (int(incomingLineWrtHeightOrWidth*width-incomingLineThicknessWrtHeightOrWidth*width), height), (255, 0, 0), thickness=2)

                cv2.line(img, (int(outgoingLineWrtHeightOrWidth*width+outgoingLineThicknessWrtHeightOrWidth*width), 0), (int(outgoingLineWrtHeightOrWidth*width+outgoingLineThicknessWrtHeightOrWidth*width), height), (0, 0, 255), thickness=2)
                cv2.line(img, (int(outgoingLineWrtHeightOrWidth*width-outgoingLineThicknessWrtHeightOrWidth*width), 0), (int(outgoingLineWrtHeightOrWidth*width-outgoingLineThicknessWrtHeightOrWidth*width), height), (0, 0, 255), thickness=2)

                if class_name in objectsTrackInOut:
                    if center_x <= int(incomingLineWrtHeightOrWidth*width+incomingLineThicknessWrtHeightOrWidth*width) and center_x >= int(incomingLineWrtHeightOrWidth*width-incomingLineThicknessWrtHeightOrWidth*width):
                        #Incoming zone touched
                        objectTrackId=int(track.track_id)
                        if objectTrackId not in incomingTrackIdsList:#Added because multiple same objectTrackId were appended to incomingTrackIdsList because of frames
                            incomingTrackIdsList.append(objectTrackId)
                            if objectTrackId not in outgoingTrackIdsList:
                                index=objectsTrackInOut.index(class_name)
                                incomingCount[index]+=1
                                outgoingTrackIdsList.append(objectTrackId)#Added so that a person is only counted once

                if class_name in objectsTrackInOut:
                    if center_x <= int(outgoingLineWrtHeightOrWidth*width+outgoingLineThicknessWrtHeightOrWidth*width) and center_x >= int(outgoingLineWrtHeightOrWidth*width-outgoingLineThicknessWrtHeightOrWidth*width):
                        #Outgoing zone touched
                        objectTrackId=int(track.track_id)
                        if objectTrackId not in outgoingTrackIdsList:
                            outgoingTrackIdsList.append(objectTrackId)
                            if objectTrackId not in incomingTrackIdsList:
                                index=objectsTrackInOut.index(class_name)
                                outgoingCount[index]+=1
                                incomingTrackIdsList.append(objectTrackId)#Added so that a person is only counted once

    initialHeight=60
    if activateIncomingOutgoing:
        for objectName in objectsTrackInOut:
            index=objectsTrackInOut.index(objectName)
            cv2.putText(img, "Incoming "+objectName+"s: " + str(incomingCount[index]), (10, initialHeight), 0, 0.8, (0, 0, 255), 2)
            initialHeight+=30
            cv2.putText(img, "Outgoing "+objectName+"s: " + str(outgoingCount[index]), (10,initialHeight), 0, 0.8, (0,0,255), 2)
            initialHeight+=30
###########################################################################INCOMING OUTGOING##############

##########SOCIAL DISTANCING FEATURE###############################################################################
    if activateSocialDistance:
        red_social_dis_zone_list=[]
        red_social_dis_line_list=[]
        for (id1,p1), (id2,p2) in combinations(centroid_dict.items(),2):
            dx,dy=p1[0]-p2[0], p1[1]-p2[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < distanceTreshold:
                if id1 not in red_social_dis_zone_list:
                    red_social_dis_zone_list.append(id1)
                    red_social_dis_line_list.append(p1[0:2])
                if id2 not in red_social_dis_zone_list:
                    red_social_dis_zone_list.append(id2)
                    red_social_dis_line_list.append(p2[0:2])

        for idx, box  in centroid_dict.items():
            if idx in red_social_dis_zone_list:
                cv2.rectangle(img, (box[2],box[3]),(box[4],box[5]), (0,0,255), 2)
            else:
                cv2.rectangle(img, (box[2],box[3]),(box[4],box[5]), (0,255,0), 2)

        cv2.putText(img, "People at risk: "+str(len(red_social_dis_zone_list)), (10,initialHeight), 0, 0.8, (0,0,255), 2)
        initialHeight+=30
        for check in range(0, len(red_social_dis_line_list)-1):
            start_point=red_social_dis_line_list[check]
            end_point=red_social_dis_line_list[check+1]
            check_line_x=abs(end_point[0]-start_point[0])
            check_line_y=abs(end_point[1]-start_point[1])
            if (check_line_x<distanceTreshold) and (check_line_y<distanceTreshold):
                cv2.line(img, start_point, end_point, (0,0,255), 2)

#############################################################################SOCIAL DISTANCING FEATURE############

#######COUNTING##################################################################################
    if activateCounting:
        for objectName in objectsToTrack:
            index=objectsToTrack.index(objectName)
            cv2.putText(img, "Inside Zone "+objectName+" count: " + str(current_count[index]), (10, initialHeight), 0, 0.8, (0, 0, 255), 2)
            initialHeight+=30
            total_count = len(set(counter[index]))-1
            cv2.putText(img, "Total "+objectName+" count: " + str(total_count), (10,initialHeight), 0, 0.8, (0,0,255), 2)
            initialHeight+=30
#################################################################################COUNTING########
    
    cv2.putText(img,"Made by Karthik Pillai", (10,initialHeight), 0, 0.8, (0,0,255), 2)

    fps = 1./(time.time()-t1)
    cv2.putText(img, "FPS: {:.2f}".format(fps), (10,30), 0, 0.8, (0,0,255), 2)
    #cv2.resizeWindow(outputVideoName, 1024, 768)
    if showRenderingVideo:
        cv2.namedWindow(outputVideoName, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(outputVideoName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow(outputVideoName, img)
    else:
        print("FPS: {:.2f}".format(fps))

    out.write(img)

    if activateHeapMap:
        cv2.imwrite(outputFolderPath+"HeatMap_Output.jpg", FirstFrame)

    if cv2.waitKey(1) == ord('q'):
        print("STOPPED")
        break

vid.release()
out.release()
cv2.destroyAllWindows()