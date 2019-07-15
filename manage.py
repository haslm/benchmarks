import paramiko
import threading
import toml

class Device_Manager:
    """
    the device manager holds the device's basic information
    it also manages an ssh connection, which we can use to send shell commands
    """
    def __init__(self, ip = None,username = None,password = None,port = None):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.ssh = None # hold the ssh connection
    
    def ssh_connect(self):
        """connect to this device using ssh"""
        paramiko.util.log_to_file("logs/"+"running.log")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname = self.ip, port = self.port, username = self.username, password = self.password)

    def exec_command(self,command):
        """
        execute command on remote device through ssh connection
        
        Parameters:
            command - a line of shell command such as `mkdir test`
        Returns:
            None - if ssh connection does't exist
            threading.Thread - a thread instance that runs this command asynchronously
        """

        if(self.ssh is None):
            print("Not connected!")
            return None
        class execThread(threading.Thread):
            def __init__(self, command, ip, ssh):
                threading.Thread.__init__(self)
                self.command = command
                self.ip = ip
                self.ssh = ssh
            def run(self):
                print("RUN COMMAND %s on %s"%(self.command, self.ip))
                stdin, stdout, stderr = self.ssh.exec_command(self.command)
                print("COMMAND %s RETURN %s on %s"%(command, stdout.read(), self.ip))
        thread = execThread(command,self.ip,self.ssh)
        thread.start()
        return thread

class Cloud_Manager(Device_Manager):
    def __init__(self, ip = None,username = None, password = None, port = None):
        super(Cloud_Manager,self).__init__(ip,username,password,port)
        self.connected_edges = []
    def connect_edge(self,edge):
        self.connected_edges.append(edge)

class Edge_Manger(Device_Manager):
    def __init__(self, ip = None,username = None, password = None, port = None):
        super(Edge_Manger,self).__init__(ip,username,password,port)
        self.connected_cloud = None
        self.connected_iots = []

    def connect_cloud(self, cloud):
        self.connected_cloud = cloud
    def connect_iot(self, iot):
        self.connected_iots.append(iot)

class Iot_Manager(Device_Manager):
    def __init__(self, ip = None,username = None, password = None, port = None):
        super(Iot_Manager,self).__init__(ip,username,password,port)
        self.connected_Edge = None
    def connect_edge(self,edge_node):
        self.connected_Edge = edge_node


class Global_Manager:
    """
    global config
    including ip username, password, port of edge nodes, cloud server and iot
    """
    def __init__(self,global_config_file = None):
        self.cloud_managers = []
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
        for info in cloud_cfg['info']:
            cloud_manager = Cloud_Manager(info[0], info[1], info[2], int(info[3]))
            self.cloud_managers.append(cloud_manager)
        #config edges
        edges_cfg = config['edges']
        for info in edges_cfg['info']:
            edge_manager = Edge_Manger(info[0], info[1], info[2], int(info[3]))
            cloud_to_connect = self.get_manager(self.cloud_managers, info[4])
            if(not cloud_to_connect == None):
                cloud_to_connect.connect_edge(edge_manager)
                edge_manager.connect_cloud(cloud_to_connect)
            self.edge_managers.append(edge_manager)
        
        #config iots
        iot_cfg = config['iots']
        for info in iot_cfg['info']:
            iot_manager = Iot_Manager(info[0],info[1],info[2], int(info[3]))
            edge_to_connect = self.get_manager(self.edge_managers, info[4])
            if(not edge_to_connect == None):
                edge_to_connect.connect_iot(iot_manager)
                iot_manager.connect_edge(edge_to_connect)
            self.iot_managers.append(iot_manager)
    
    def ssh_connect(self):
        """
        connect to all the devices using ssh 
        """
        for cloud_manager in self.cloud_managers:
            cloud_manager.ssh_connect()
        for edge_manager in self.edge_managers:
            edge_manager.ssh_connect()
        for iot_manager in self.iot_managers:
            iot_manager.ssh_connect()
        print("Connected to all devices")

    def make_workspace(self):
        for cloud_manager in self.cloud_managers:
            cloud_manager.exec_command("mkdir edgeBench")
        for edge_manager in self.edge_managers:
            edge_manager.exec_command("mkdir edgeBench")
        for iot_manager in self.iot_managers:
            iot_manager.exec_command("mkdir edgeBench")
    
    def broadcast(self, command, devices, sync):
        threads = []
        for device in devices:
            thread = device.exec_command(command)
            threads.append(thread)
        if (sync):
            for thread in threads:
                thread.join()
            return 0
        else:
            return threads

if __name__ == "__main__":
    global_manager = Global_Manager("global_config.toml")
    global_manager.ssh_connect()
    global_manager.make_workspace()
    threads = global_manager.broadcast("pwd",global_manager.iot_managers + global_manager.edge_managers + global_manager.cloud_managers)
    for thread in threads:
        thread.join()