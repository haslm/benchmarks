#!/bin/bash

i=1
rtsp_address = "rtsp://222.29.97.89:554/stream/"
test_video = "test.mp4" 

while(($i<10))
do
        echo $i
        ffmpeg -re -i $test_video -vcodec copy -codec copy -rtsp_transport tcp -f rtsp $rtsp_address
        i=$(($i+1))
done