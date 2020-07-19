import time
import json
import redis
import subprocess
from subprocess import Popen, check_output
import shlex
import os
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
import msgpack
import pickle
import zlib

redis_site_file = "/mnt/ssd/site_config/redis_server.json"
reboot_file = "/mnt/ssd/site_config/reboot_file.json"
construct_graph = 'docker run   -it --network host --rm  --name pod_utility_function  --mount type=bind,source=/mnt/ssd/site_config,target=/data/ nanodatacenter/pod_utility_function /bin/bash construct_graph.bsh'

def find_container_image(service):
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    query_list = qs.add_match_terminal( query_list,relationship="CONTAINER",label=service )
    service_sets, service_nodes = qs.match_list(query_list)
    container_image = service_nodes[0]["container_image"]
  
    return container_image
    



def find_service_image(service):
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
    query_list = qs.add_match_terminal( query_list,relationship="SERVICE",label=service )
    service_sets, service_nodes = qs.match_list(query_list)
    print("service",service)
    container_image = service_nodes[0]["container_image"]
    print("container_image",container_image)
    return container_image
    

  


def time_out_function():
     print("null message")       

def upgrade_handler(input_message):
    
    
    if input_message['pod'] == True:
       input_message['pod'] = [True,'https://github.com/glenn-edgar/docker_node_control.git']
    else:
       input_message["pod"] = [False]
       
    if input_message['graph'] == True:
       input_message['graph'] = [True,'nanodatacenter/pod_utility_function',construct_graph]
    else:
       input_message['graph'] = [False]       
    services = input_message["services"]
    temp =  []
    for i in services:    
       temp.append(find_service_image(i))
    input_message["services"] = temp
    containers = input_message["containers"]
    temp =  []
    for i in containers:    
       temp.append(find_container_image(i))
    input_message["containers"] = temp
    
    input_message_json = json.dumps(input_message)
    print(input_message_json)
 
    
    f = open(reboot_file,"w")
    f.write(input_message_json)
    f.close()
    reboot_hash.hset("REBOOT_FLAG","REBOOT")
    return True




    
if __name__ == "__main__":
   
   
   file_handle = open("/mnt/ssd/site_config/redis_server.json")
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)
   
   #print("--",site_data["site"],site_data["local_node"],container_name)
   qs = Query_Support( site_data )

   
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_relationship( query_list,relationship="DOCKER_MONITOR" )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "DATA_STRUCTURES" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
   
   #print("package_nodes",package_nodes)
   
   generate_handlers = Generate_Handlers(package_nodes[0],qs)
   data_structures = package_nodes[0]["data_structures"]
   
   reboot_hash = generate_handlers.construct_hash(data_structures["REBOOT_DATA"])
   rpc_server = generate_handlers.construct_rpc_sever(data_structures["DOCKER_UPDATE_QUEUE"])
   rpc_server.add_time_out_function(time_out_function)
   rpc_server.register_call_back( "Upgrade", upgrade_handler)
   rpc_server.start()    


else:
   pass


