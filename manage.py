import paramiko
import toml

class Device_Config:
    def __init__(self, ip = None,username = None,password = None,port = None):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port 

class Global_Config:
    """
    global config, including ip username, password, port of edge nodes and cloud
    """
    def __init__(self,global_config_file):
        self.cloud_config = None
        self.edge_number = 0
        self.edge_configs = []
        self.read(global_config_file)

    def read(self,global_config_file):
        config = toml.load(open("global_config.toml"))
        cloud_cfg = config['cloud']
        self.cloud_config = Device_Config(cloud_cfg['ip'], cloud_cfg['username'], \
            cloud_cfg['password'], cloud_cfg['port'])
        edges_cfg = config['edges']
        self.edge_number = int(edges_cfg['number'])
        assert(self.edge_number == len(edges_cfg['info']))
        for info in edges_cfg['info']:
            self.edge_configs.append(Device_Config(info[0],info[1],info[2], int(info[3])))
        

def sshclient_execmd(hostname, port, username, password, execmd):
    paramiko.util.log_to_file("running.log")

    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    s.connect(hostname = hostname, port = port, username = username, password = password)
    stdin, stdout, stderr = s.exec_command(execmd)
    # stdin.write("Y")

    print(stdout.read())
    s.close()

def main():
    global_config = Global_Config("global_config.toml")
    
    # sshclient_execmd(hostname, port, username, password, execmd)


if __name__ == "__main__":
    main()