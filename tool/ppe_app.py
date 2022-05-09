
def get_xyxy(img,dictOfModels):
   
    result = dictOfModels['best'](img)
    return result.xyxy[0]
