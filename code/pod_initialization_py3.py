import redis
import json
import time
from pod_control.docker_interface_py3 import Docker_Interface
from redis_support_py3.graph_query_support_py3 import  Query_Support


redis_site_file = "/mnt/ssd/site_config/redis_server.json"


predefined_containers= {}
predefined_containers["redis"] =["redis",'/home/pi/pod_control/code/startup_scripts/redis_run.bsh']
predefined_containers["pod_construct_graph"] =["pod_utility_function",'/home/pi/pod_control/code/startup_scripts/pod_util_construct_graph.bsh']
predefined_containers["pod_util_set_passwords"] =["pod_utility_function",'/home/pi/pod_control/code/startup_scripts/pod_util_set_passwords.bsh']
predefined_containers["monitor_redis"] =["monitor_redis",'/home/pi/pod_control/code/startup_scripts/redis_monitoring.bsh']
predefined_containers["ethereum"] =["ethereum_go",'/home/pi/pod_control/code/startup_scripts/ethereum_run.bsh']
predefined_containers["manage_contracts"] = ["manage_contracts",'/home/pi/pod_control/code/startup_scripts/manage_contracts.bsh']
predefined_containers["stream_events_to_log"] =["stream_events_to_log",'/home/pi/pod_control/code/startup_scripts/stream_events_to_log.bsh']
predefined_containers["stream_events_to_cloud"] =["stream_events_to_cloud",'/home/pi/pod_control/code/startup_scripts/stream_events_to_cloud.bsh']
predefined_containers["sqlite_server"] =["sqlite_server",'/home/pi/pod_control/code/startup_scripts/sqlite_server.bsh']

    

def wait_for_redis_db(site_data):
   
    while True:
        try:
            redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["graph_db"])
            temp = redis_handle.ping()
            print(temp)
            if temp == True:
              
              
               return
            else:
               raise
        except:
           print("exception")
           time.sleep(10)
           pass



def start_container_applications(site_data):
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


def start_site_services(site_data):
    if 'master' in site_data:
       if site_data["master"] == True:
          docker_control.container_up("redis",'/home/pi/pod_control/code/startup_scripts/redis_run.bsh')
    wait_for_redis_db(site_data)
    qs = Query_Support( site_data )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    processor_sets, processor_nodes = qs.match_list(query_list)
    containers = processor_nodes[0]["services"]
    print("containers",containers)
    for i in containers:
       data = predefined_containers[i]
       docker_control.container_up(data[0],data[1])

#
#
# starting point
#
#



docker_control = Docker_Interface()
file_handle = open(redis_site_file,'r')
try:    
    data = file_handle.read()
    file_handle.close()
    site_data = json.loads(data)
except:
    # post appropriate error message
    raise    


start_site_services(site_data)
wait_for_redis_db(site_data)
start_container_applications(site_data)
# start the runtime processes















