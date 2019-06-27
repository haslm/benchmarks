import cv2

def get_rtsp_video_path():
    return "rtsp://222.29.97.89/stream/"

def report(image, boxes):
    print (boxes)

def detect():
    history = 20
    frames = 0

    rstp_video = get_rtsp_video_path()
    cap = cv2.VideoCapture(rstp_video)
    if not cap.isOpened():
        print("Can't open rtsp stream! please check the rtsp stream provision")
    else:
        print("Receving rtsp stream ")

    print("Start object detection, using algorithm KNN, history length: ",str(history))
    bs = cv2.createBackgroundSubtractorKNN(detectShadows = True)
    bs.setHistory(history)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        fg_mask = bs.apply(frame) # get foreground mask
        if frames < history:
            frames += 1
            continue
        #perform dilate operation for denosing
        th = cv2.threshold(fg_mask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
        th = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
        dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 3)), iterations=2)
        #get all the detected boxes 
        contours, hier = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for c in contours:
            # get axises of detected boxes
            x, y, w, h = cv2.boundingRect(c)
            boxes.append([x, y, w, h])
        if(len(boxes) > 0):
            report(frame, boxes)

if __name__ == "__main__":
    detect()



    

