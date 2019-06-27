from datetime import datetime as dt
import time
import numpy as np
import telemanom.helpers as helpers
import telemanom.modeling as models
from telemanom.globals import Config, installGlobalConfig
from telemanom.errors import find_error_sequences
from mqtt.Edge import Edge
import _thread
import pandas as pd

edge = Edge("222.128.10.155",1883)
edge.connect()
scale = 10.0
buffer_size = 200
thresh = 0.3

def get_next():
    while(True):
        if(len(edge.buffer)>0):
            data = edge.buffer[0]
            edge.buffer.pop(0)
            return data
        time.sleep(0.05)

def run( config: Config):
    model = models.get_model(config)
    datas = []
    pred = []
    errors = []
    errors_smoothed = []
    alarm = [False]
    while(True):
        data = get_next()
        data/=scale
        datas.append(data)

        if(len(datas)>buffer_size):
            datas.pop(0)
            pred.pop(0)

        if(len(datas)<config.l_s):
            continue

        if(len(pred)>0):
            errors.append(abs(pred[-1]-datas[-1]))
            # errors_smoothed = list(pd.DataFrame(errors).ewm(span=30).mean().values.flatten())
            if(alarm[0]):
                edge.publish(1,"alarm")
                time.sleep(0.1)
            # print(errors[-1])

        # print (datas[-1])
        period = datas[-config.l_s:]
        period = np.asarray(period,dtype=np.float32)[np.newaxis,...,np.newaxis]
        y_hat = model.predict(period)[0]
        y_hat = max(y_hat[0],0)
        pred.append(y_hat)
        
        if(len(errors)>buffer_size):
            errors.pop(0)



if __name__ == "__main__":
    config = Config( ["common.yaml", 'input.yaml', 'test.yaml'], False)
    installGlobalConfig( config)
    run( config)
