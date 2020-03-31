import redis
import json
import time
from pod_control.docker_interface_py3 import Docker_Interface
from redis_support_py3.graph_query_support_py3 import  Query_Support


redis_site_file = "/mnt/ssd/site_config/redis_server.json"
password_file   = "passwords.py"

predefined_containers= {}
predefined_containers["redis"] =["redis",'/home/pi/pod_control/code/startup_scripts/redis_run.bsh']
predefined_containers["postgres"] =["postgres",'/home/pi/pod_control/code/startup_scripts/postgres_run.bsh']
predefined_containers["pod_construct_graph"] =["pod_utility_function",'/home/pi/pod_control/code/startup_scripts/pod_util_construct_graph.bsh']
predefined_containers["pod_util_set_passwords"] =["pod_utility_function",'/home/pi/pod_control/code/startup_scripts/pod_util_set_passwords.bsh']
predefined_containers["pod_util_echo"] =["pod_utility_function",'/home/pi/pod_control/code/startup_scripts/pod_util_echo.bsh']
predefined_containers["monitor_redis"] =["monitor_redis",'/home/pi/pod_control/code/startup_scripts/redis_monitoring.bsh']


def start_postgres_container():
    data = predefined_containers["postgres"]
    docker_control.container_up(data[0],data[1])


def start_redis_container():
    data = predefined_containers["redis"]
    docker_control.container_up(data[0],data[1])
    
def start_utility_pod():
    data = predefined_containers["pod_construct_graph"]
    docker_control.container_up(data[0],data[1])
    data = predefined_containers["pod_util_set_passwords"]
    docker_control.container_up(data[0],data[1])   
    data = predefined_containers["pod_util_echo"]
    docker_control.container_up(data[0],data[1])    
def run_utility_functions():
    pass
    

def wait_for_redis_db(site_data):
    while True:
        try:
            redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["graph_db"])
            return
        except:
           time.sleep(10)
           pass



def start_slave_pod_container(site_data):
   qs = Query_Support( site_data )
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   processor_sets, processor_nodes = qs.match_list(query_list)
   containers = processor_nodes[0]["containers"]
   print("containers",containers)
   for i in containers:
       data = predefined_containers[i]
       docker_control.container_up(data[0],data[1])





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
   start_postgres_container()
   start_redis_container()
   start_utility_pod()
   run_utility_functions()
   #start_master_pod_controller()
   
else:
  wait_for_redis_db(site_data)


start_slave_pod_container(site_data)








