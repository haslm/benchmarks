import argparse
from manage import Global_Manager

global_manager = Global_Manager()

def initialize(args):
    config_file = args.configfile
    print("Reading global config from " + config_file)
    global_manager.read(config_file)
    print("Connect to all the devices")
    global_manager.ssh_connect()
    print("Make and enter workspace")
    global_manager.make_and_enter_workspace()
    

def main(args):
    initialize(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--services", help = "testing service", default = "all", choices = ['all','objDetection','anomlyDetection'])
    parser.add_argument("-c","--configfile",help = "global config file", default = "global_config.toml")
    args = parser.parse_args()
    main(args)