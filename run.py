import argparse
import _thread
from manage import Global_Manager

global_manager = Global_Manager()

def initialize(args):
    config_file = args.configfile
    print("Reading global config from " + config_file)
    global_manager.read(config_file)
    print("Connect to all the devices")
    global_manager.ssh_connect()
    print("Make workspace")
    global_manager.make_workspace()
    
def run_objDetection(args):
    #Install EasyDarwin
    #TODO
   
    """
    setup docker environment on edge nodes
    """
    cmd = "docker pull pkuzhou/edge_bench:object_detection"
    global_manager.broadcast(cmd, global_manager.edge_managers, sync = True)

    cmd = "docker stop object_detection"
    global_manager.broadcast(cmd, global_manager.edge_managers, sync = True)

    cmd = "docker rm object_detection"
    global_manager.broadcast(cmd, global_manager.edge_managers, sync = True)

    cmd = "docker run --name object_detection -dit pkuzhou/edge_bench:object_detection "
    threads = global_manager.broadcast(cmd, global_manager.edge_managers, sync = True)

    #push rtsp in iot devices
    test_video = "test.mp4"
    rtsp_address = "rtsp://127.0.0.1/stream"
    cmd = "ffmpeg -re -i %s -vcodec copy -codec copy -rtsp_transport tcp -f rtsp %s"%(test_video, rtsp_address)
    threads = global_manager.broadcast(cmd, global_manager.iot_managers,sync =False)
    all_streams = ""
    for edge_manager in global_manager.edge_managers:
        for iot in edge_manager.connected_iots:
            rtsp_stream = "rtsp://%s/stream"%(iot.ip)
            all_streams+=rtsp_stream
            all_streams+=','

    cmd = "docker exec object_detection python3 main.py -i %s "%(all_streams) 
    threads += global_manager.broadcast(cmd, global_manager.edge_managers,sync = False)

    for thread in threads:
        thread.join()
    # for edge_manager in global_manager.edge_managers:
    #     cmd = "docker exec xxx"
    #     edge_manager.exec_command(cmd)


def run_anomlyDetection(args):
    pass

def main(args):
    initialize(args)
    if(args.services == 'all'):
        run_objDetection(args)
        run_anomlyDetection(args)
    elif args.services == 'objDetection':
        run_objDetection(args)
    elif args.services == 'anomlyDetection':
        run_anomlyDetection(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--services", help = "testing service", default = "all", choices = ['all','objDetection','anomlyDetection'])
    parser.add_argument("-c","--configfile",help = "global config file", default = "global_config.toml")
    args = parser.parse_args()
    main(args)