import psutil
import platform
from datetime import datetime
import json
from pymemcache.client.base import Client
from pymemcache import serde

######################################################################
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


################# SYSTEM INFO #################
uname = platform.uname()

# Boot Time
boot_time_timestamp = psutil.boot_time()
bt = datetime.fromtimestamp(boot_time_timestamp)

boot_t = f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
systemInfo =    {'system' : uname.system,
                'name' : uname.node,
                'version' : uname.version,
                'machine' : uname.machine,
                'boot' : boot_t}


######################## CPU information ######################
cpufreq = psutil.cpu_freq()

coresInfo = {}
for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    coresInfo[i] = percentage 

cpuInfo =  {'cores' : psutil.cpu_count(logical=False),
            'logical_cores' : psutil.cpu_count(logical=True),
            'usage' : coresInfo, 
            'total' : psutil.cpu_percent()}


########################## Memory Information ##############################
svmem = psutil.virtual_memory()

memoryInfo = {'total' : get_size(svmem.total),
              'available' : get_size(svmem.available),
              'used' : get_size(svmem.used)}



########################################################
data = {'system' : systemInfo,
        'cpu' : cpuInfo,
        'memory' : memoryInfo}
        
with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)

class JsonSerde(object):
    def serialize(self, key, value):
        if isinstance(value, str):
            return value, 1
        return json.dumps(value), 2

    def deserialize(self, key, value, flags):
       if flags == 1:
           return value
       if flags == 2:
           return json.loads(value)
       raise Exception("Unknown serialization format")

client = Client("127.0.0.1:9999",  serde=serde.pickle_serde)
client.set('data', data)
result = client.get('data')
print(result)