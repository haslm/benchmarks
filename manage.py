import paramiko
import toml

class Device_Manager:
    """
    the device manager holds the device's basic information
    it also manages an ssh connection, which we can use to send commands
    """
    def __init__(self, ip = None,username = None,password = None,port = None):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.ssh = None
    
    def ssh_connect(self):
        """connect to this device using ssh"""
        paramiko.util.log_to_file("logs/"+"running.log")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname = self.ip, port = self.port, username = self.username, password = self.password)
        # self.exec("pwd")

    def exec(self, command):
        if(self.ssh is None):
            print("Not connected!")
            return
        stdin, stdout, stderr = self.ssh.exec_command(command)
        print(stdout.read())

class Cloud_Manager(Device_Manager):
    def __init__(self, ip = None,username = None, password = None, port = None):
        super(Cloud_Manager,self).__init__(ip,username,password,port)
        self.connected_edges = []

class Edge_Manger(Device_Manager):
    def __init__(self, ip = None,username = None, password = None, port = None):
        super(Edge_Manger,self).__init__(ip,username,password,port)
        self.connected_cloud = None
        self.connected_iots = []
    """asssign the connected cloud"""
    def connect_cloud(self, cloud):
        self.connected_cloud = cloud

class Iot_Manager(Device_Manager):
    def __init__(self, ip = None,username = None, password = None, port = None):
        super(Iot_Manager,self).__init__(ip,username,password,port)
        self.connected_Edge = None
    """assign the connected edge node"""
    def connect_edge(self,edge_node):
        self.connected_Edge = edge_node


class Global_Manager:
    """
    global config
    including ip username, password, port of edge nodes, cloud server and iot
    """
    def __init__(self,global_config_file = None):
        self.cloud_manager = None
        self.edge_number = 0
        self.edge_managers = []
        self.iot_managers = []

        if(not global_config_file == None):
            self.read(global_config_file)

    def get_manager(self, managers_list, ip):
        for manager in managers_list:
            if (manager.ip == ip):
                return manager
        return None

    def read(self,global_config_file):
        # parse global config file
        config = toml.load(open("global_config.toml"))

        #config cloud
        cloud_cfg = config['cloud']
        self.cloud_manager = Cloud_Manager(ip = cloud_cfg['ip'], username = cloud_cfg['username'], \
            password = cloud_cfg['password'], port =  cloud_cfg['port'])
        
        #config edges
        edges_cfg = config['edges']
        self.edge_number == len(edges_cfg['info'])
        for info in edges_cfg['info']:
            edge_manager = Edge_Manger(info[0],info[1],info[2], int(info[3]))
            edge_manager.connect_cloud(self.cloud_manager)
            self.cloud_manager.connected_edges.append(edge_manager)
            self.edge_managers.append(edge_manager)
        
        #config iots
        iot_cfg = config['iots']
        for info in iot_cfg['info']:
            iot_manager = Iot_Manager(info[0],info[1],info[2], int(info[3]))
            connected_edge = self.get_manager(self.edge_managers, info[4])
            if(connected_edge == None):
                continue 
            connected_edge.connected_iots.append(iot_manager)
            iot_manager.connect_edge = connected_edge
            self.iot_managers.append(iot_manager)
    
    def ssh_connect(self):
        """
        connect to all the devices using ssh 
        """
        self.cloud_manager.ssh_connect()
        for edge_manager in self.edge_managers:
            edge_manager.ssh_connect()
        for iot_manager in self.iot_managers:
            iot_manager.ssh_connect()
        print("Connected to all devices")

    def make_and_enter_workspace(self):
        self.cloud_manager.exec("mkdir edgeBench&&cd edgeBench")
        for edge_manager in self.edge_managers:
            edge_manager.exec("mkdir edgeBench&&cd edgeBench")
        for iot_manager in self.iot_managers:
            iot_manager.exec("mkdir edgeBench&&cd edgeBench")

if __name__ == "__main__":
    global_manager = Global_Manager("global_config.toml")
    global_manager.ssh_connect()
    global_manager.make_workspace()