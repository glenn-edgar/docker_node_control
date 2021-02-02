import redis
import json
import time
import os
from docker_control.docker_interface_py3 import Docker_Interface
from redis_support_py3.graph_query_support_py3 import  Query_Support
redis_site_file = "/mnt/ssd/site_config/redis_server.json"

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

def find_container_scripts(qs,service):
    qs = Query_Support( site_data )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    query_list = qs.add_match_terminal( query_list,relationship="CONTAINER",label=service )
    service_sets, service_nodes = qs.match_list(query_list)
    command_script = service_nodes[0]["startup_command"]
  
    return command_script
 

def start_container_applications(site_data):
   qs = Query_Support( site_data )
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   processor_sets, processor_nodes = qs.match_list(query_list)
   containers = processor_nodes[0]["containers"]
   
   print("containers",containers)
  
   for i in containers:
       starting_script = find_container_scripts(qs,i)
       docker_control.container_up(i,starting_script)


def find_starting_service_script(qs,service):
    qs = Query_Support( site_data )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    query_list = qs.add_match_terminal( query_list,relationship="SERVICE",label=service )
    service_sets, service_nodes = qs.match_list(query_list)
    command_script = service_nodes[0]["command_list"]
  
    return command_script
    
def start_site_services(site_data):
    
    
    qs = Query_Support( site_data )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    processor_sets, processor_nodes = qs.match_list(query_list)
    services = processor_nodes[0]["services"]
    
   
    for i in services:
       if i == "redis":
           continue
       starting_script = find_starting_service_script(qs,i)
       docker_control.container_up(i,starting_script)
  

def verify_services(site_data):
    qs = Query_Support( site_data )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    processor_sets, processor_nodes = qs.match_list(query_list)
    services = processor_nodes[0]["services"]
    #print("services",services)
    for i in services:
       check = docker_control.get(i)
      
       if check == None:
          raise ValueError("container "+i+" is not define")

def verify_containers(site_data):
    qs = Query_Support( site_data )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    processor_sets, processor_nodes = qs.match_list(query_list)
    containers = processor_nodes[0]["containers"]
    #print("containers",containers)
    for i in containers:
       check = docker_control.get(i)
       print(i,check)
       if check == None:
          raise ValueError("container "+i+" is not define")   
#
#
# starting point
#
#


#time.sleep(15) # let docker engine get running
docker_control = Docker_Interface()





file_handle = open(redis_site_file,'r')
try:    
    data = file_handle.read()
    file_handle.close()
    site_data = json.loads(data)
except:
    # post appropriate error message
    raise    


      
wait_for_redis_db(site_data)

start_site_services(site_data)
verify_services(site_data)


start_container_applications(site_data)
verify_containers(site_data)
# start the runtime processes















