import cv2
import threading
import argparse
import logging
import time
from matplotlib import pyplot as plt

def report(image, boxes):
    print (len(boxes))

def detect(stream, history):
    logging.basicConfig(level=logging.DEBUG,
        filename = stream.split('/')[-2]+'.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.info("Staring")

    frames = 0
    cap = cv2.VideoCapture(stream)
    if not cap.isOpened():
        logger.error("Can't open rtsp stream! please check the rtsp stream provision")
        return
    else:
        logger.info("Receving rstp stream")
    logger.info("Start object detection, using algorithm KNN, history length: %d"%(history))

    bs = cv2.createBackgroundSubtractorKNN(detectShadows = True)
    bs.setHistory(history)


    frame_tag = 0
    time_stamp = time.time()

    frame_log = []

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
        
        frame_tag += 1
        if(frame_tag == 20):
            now = time.time()
            fps = 20/(now-time_stamp)
            time_stamp = now    
            frame_tag = 0
            frame_log.append(fps)
            print(fps)

    x = range(len(frame_log))
    plt.plot(x,frame_log)
    plt.savefig('./objectDetection.png')
        # if(len(boxes) > 0):
        #     report(frame, boxes)

class threadDectector(threading.Thread):
    def __init__(self, stream, history):
        threading.Thread.__init__(self)
        self.stream = stream #rtsp stream
        self.history = history #the history length to perform background modeling 
    def run(self):
        detect(self.stream, self.history)

def main(args):
    streams = args.input_streams
    streams = streams.split(',')
    threads = []
    history = 20
    for stream in streams:
        thread = threadDectector(stream, history)
        thread.start()
        threads.append(thread)
    #wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input_streams", type = str, help = "input rtsp streams")
    args = parser.parse_args()
    main(args)


    

