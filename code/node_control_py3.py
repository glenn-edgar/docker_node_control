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

from process_control_py3 import System_Control




 
  

if __name__ == "__main__":
   
   cf = CF_Base_Interpreter()
    #
    #
    # Read Boot File
    # expand json file
    # 
   #time.sleep(20) # wait for redis server get started
   file_handle = open("/mnt/ssd/site_config/redis_server.json")
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)
   
   #print("--",site_data["site"],site_data["local_node"],container_name)
   qs = Query_Support( site_data )
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal( query_list,relationship="NODE_SYSTEM")
   node_sets, node_processes = qs.match_list(query_list)
  
   
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_relationship( query_list,relationship="NODE_SYSTEM" )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label ="DOCKER_MONITORING" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
   

   generate_handlers = Generate_Handlers(package_nodes[0],qs)
 
   system_control = System_Control(node_processes[0],package_nodes[0],generate_handlers)
   cf = CF_Base_Interpreter()
   system_control.add_chains(cf)
   #
   # Executing chains
   #
   try: 
       cf.execute()
   except:
      
       raise
else:
   pass


