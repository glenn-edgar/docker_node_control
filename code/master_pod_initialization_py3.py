import redis
import json
from pod_control.docker_interface_py3 import Docker_Interface

redis_site_file = "/mnt/ssd/site_config/redis_server.json"
password_file   = "passwords.py"

predefined_containers= {}
predefined_containers["redis"] =["redis",'/home/pi/pod_control/code/startup_scripts/redis_run.bsh']

def start_redis_container():
    data = predefined_containers["redis"]
    docker_control.container_up(data[0],data[1])
    
def start_utility_pod():
    pass
    
    
def run_utility_functions():
    pass
    

def wait_for_redis_db(site_data):
    while True:
        try:
            redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["graph_db"])
            return
        except:
           pass

def start_master_pod_controller():
    pass

def start_slave_pod_container():
    pass


docker_control = Docker_Interface()
file_handle = open(redis_site_file,'r')
try:    
    data = file_handle.read()
    file_handle.close()
    site_data = json.loads(data)
except:
    # post appropriate error message
    raise    

if "master" not in site_data:
   status["master"] = False
                  

if site_data["master"]:
   
   start_redis_container()
   start_utility_pod()
   run_utility_functions()
   start_master_pod_controller()
   
else:
  wait_for_redis_db(site_data)


start_slave_pod_container()








