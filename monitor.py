#coding=utf-8
import uuid
import socket
import time
import datetime
import psutil as ps
import threading
class DeviceStatus:
    def __init__(self):
        self.MAC = None
        self.IP = None
        self.cpu = {}
        self.mem = {}
        self.process = {}
        self.network = {}
        self.status = []
        self.get_init_info()
        self.get_status_info()
    
    def run(self):
        self.get_status_info()
        self.save_satus_to_db()
    
    def save_status_to_db(self):
        print(self.status)

    def get_init_info(self):
        self.cpu = {'cores' : 0,            #  cpu cores number
                    'percent' : 0,          #  cpu utilization
                    'system_time' : 0,      #  system time in kernel space
                    'user_time' : 0,        #  system time in user space
                    'idle_time' : 0,        #  idle time
                    'nice_time' : 0,        #  nice time (time spent on changing processes' priority)
                    'softirq' : 0,          #  软件中断时间
                    'irq' : 0,              #  中断时间
                    'iowait' : 0}           #  IO等待时间
        self.mem = {'percent' : 0,
                    'total' : 0,
                    'vailable' : 0,
                    'used' : 0,
                    'free' : 0,
                    'active' : 0}
        self.process = {'count' : 0,        #  进程数目
                        'pids' : 0}         #  进程识别号
        self.network = {'count' : 0,        #  连接总数
                        'established' : 0}  #  established连接数
        self.status = [0, 0, 0, 0]          #  cpu使用率，内存使用率， 进程数， established连接数
        self.get_mac_address()
        self.get_ip_address()

    def get_status_info(self):
        self.get_cpu_info()
        self.get_mem_info()
        # self.get_process_info()
        self.get_network_info()
        self.status[0] = self.cpu['percent']
        self.status[1] = self.mem['percent']
        self.status[2] = self.process['count']
        self.status[3] = self.network['established']

    #  获取mac
    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        self.MAC = ":".join([mac[e : e+2] for e in range(0, 11, 2)])

    #  获取ip
    def get_ip_address(self):
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tempSock.connect(('8.8.8.8', 80))
        addr = tempSock.getsockname()[0]
        tempSock.close()
        self.IP = addr

    #  获得cpu信息
    def get_cpu_info(self):
        self.cpu['cores'] = ps.cpu_count()
        self.cpu['percent'] = ps.cpu_percent(interval=1)
        cpu_times = ps.cpu_times()
        self.cpu['system_time'] = cpu_times.system
        self.cpu['user_time'] = cpu_times.user
        self.cpu['idle_time'] = cpu_times.idle
        self.cpu['nice_time'] = cpu_times.nice
        self.cpu['softirq'] = cpu_times.softirq
        self.cpu['irq'] = cpu_times.irq
        self.cpu['iowait'] = cpu_times.iowait

    #  获得memory信息
    def get_mem_info(self):
        mem_info = ps.virtual_memory()
        self.mem['percent'] = mem_info.percent
        self.mem['total'] = mem_info.total
        self.mem['vailable'] = mem_info.available
        self.mem['used'] = mem_info.used
        self.mem['free'] = mem_info.free
        self.mem['active'] = mem_info.active

    # #  获取进程信息
    # def get_process_info(self):
    #    pids = ps.pids()
    #    self.process['pids'] = pids
    #    self.process['count'] = len(pids)
    #  获取网络数据
    def get_network_info(self):
        conns = ps.net_connections()
        self.network['count'] = len(conns)
        count = 0
        for conn in conns:
           if conn.status is 'ESTABLISHED':
               count = count + 1
        self.network['established'] = count
    def get_nic_state(self):
        key_info = ps.net_io_counters(pernic=True).keys()  # 获取网卡名称
        recv = {}
        sent = {}
        for key in key_info:
            recv.setdefault(key, ps.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
            sent.setdefault(key, ps.net_io_counters(pernic=True).get(key).bytes_sent)  # 各网卡发送的字节数x
        return key_info, recv, sent

    def get_network_IO_rate(self,nic_key = 'eno1'):
        key_info, old_recv, old_sent = self.get_nic_state()
        time.sleep(1)
        key_info, now_recv, now_sent = self.get_nic_state()
        net_in = {}
        net_out = {}
        if(not nic_key in key_info):
            return None
        net_in.setdefault(nic_key, (now_recv.get(nic_key) - old_recv.get(nic_key)) / 1024)  # 每秒接收速率
        net_out.setdefault(nic_key, (now_sent.get(nic_key) - old_sent.get(nic_key)) / 1024) # 每秒发送速率
        return [net_in.get(nic_key), net_out.get(nic_key)]

    def getProcessInfo(self, p): 
        try:
            cpu = p.cpu_percent(interval=0)
            mem = p.memory_info() 
            name = p.name() 
            pid = p.pid
        except p.NoSuchProcess:
            name = "Closed_Process"
            pid = 0
            mem = 0
            cpu = 0
        return [name.upper(), pid, mem.rss, cpu]

    def getAllProcessInfo(self):
        """
        取出全部进程的进程名，进程ID，进程实际内存, 虚拟内存,CPU使用率
        """
        instances = []
        all_processes = list(ps.process_iter()) 
        for proc in all_processes: 
            proc.cpu_percent(interval=0) 
        #此处sleep1秒是取正确取出CPU使用率的重点
        time.sleep(1) 
        for proc in all_processes: 
            instances.append(self.getProcessInfo(proc))
        return instances

    def get_cpu_utilization(self):
        instances = self.getAllProcessInfo()
        utilization = 0
        for instance in instances:
            utilization += instance[-1]
        return int(utilization)

if __name__ == '__main__':
    DS = DeviceStatus()
    utilization = DS.get_cpu_utilization()
    network_load = DS.get_network_IO_rate()
    print(utilization)
    print(network_load)

        