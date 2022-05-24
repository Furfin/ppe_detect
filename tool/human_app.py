
 
def get_hum(img,model):
    result = []

    classIds, scores, boxes = model.detect(img, confThreshold=0.6, nmsThreshold=0.4)
    
    for (classId, score, box) in zip(classIds, scores, boxes):
        if classId == 0:
            result.append((classId,score,box))
    
    return result