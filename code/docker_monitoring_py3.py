from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from pod_control.docker_interface_py3 import Docker_Interface
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
import json 
import time

class Monitor_Containers(object):
   def __init__(self,processor_node, package_node, generate_handlers):
      
       services = set(processor_node["services"])
       containers = set(processor_node["containers"])
       containers = containers.union(services)
       self.container_list = list(containers)     
       print("containers",containers)       
       self.docker_interface =  Docker_Interface()        
       
       data_structures = package_node["data_structures"]
       
       #print(data_structures.keys())
       self.ds_handlers = {}
       self.ds_handlers["ERROR_STREAM"]        = generate_handlers.construct_redis_stream_writer(data_structures["ERROR_STREAM"])
       self.ds_handlers["ERROR_STATE"]        = generate_handlers.construct_hash(data_structures["ERROR_HASH"])
       self.ds_handlers["WEB_COMMAND_QUEUE"]   = generate_handlers.construct_job_queue_server(data_structures["WEB_COMMAND_QUEUE"])
       self.ds_handlers["ERROR_STATE"].delete_all()
       self.setup_environment()
       self.check_for_allocated_containers()

          
      
   def setup_environment(self):
        for i in self.container_list:
           self.ds_handlers["ERROR_STATE"].hset(i,{"name":i,"enabled":True,"active":True,"error":False,"defined":True})
           
   def check_for_allocated_containers(self):
       existing_containers = self.docker_interface.containers_ls_all()
       print("exiting_containers",existing_containers)
       for i in self.container_list:
           #print(i)
           if i not in existing_containers:
               print("container not found",i)
               self.ds_handlers["ERROR_STREAM"].push( data = { "container": i, "error_output" :"container not found", "time":time.time() } )
               temp = self.ds_handlers["ERROR_STATE"].hget(i)
               temp["defined"] = False
               self.ds_handlers["ERROR_STATE"].hset(i,temp)
           
   
   def monitor(self,*unused):
       running_containers = self.docker_interface.containers_ls_runing()
       for i in self.container_list:
           #print(i)
           temp = self.ds_handlers["ERROR_STATE"].hget(i)
           if i not in running_containers:
               print("container not running",i)
               if (temp["defined"] == True) and (temp["enabled"] == True) :
                  if temp["active"] == True:
                     self.ds_handlers["ERROR_STREAM"].push( data = { "container": i, "error_output" :"container not running", "time":time.time() } )
                     temp["active"] = False
                     
                  self.docker_interface.container_start(i) # try to restart container
           
           else:          
               if temp["active"] == False:
                  temp["active"] = True

           temp = self.ds_handlers["ERROR_STATE"].hget(i)              
           
   def process_web_queue( self, *unused ):
       data = self.ds_handlers["WEB_COMMAND_QUEUE"].pop()
       
       if data[0] == True :
           for container,item in data[1].items():
               temp = self.ds_handlers["ERROR_STATE"].hget(container)
               if temp["defined"] == False:
                   continue #cannot start a nonexitant container
               try:
                  
                   if item["enabled"] == True:
                      
                        if temp["enabled"] == False:
                           temp["enabled"] = True 
                           temp["active"] = False
                           self.ds_handlers["ERROR_STREAM"].push( data = { "container": i, "error_output" :"container enabled for running", "time":time.time() } )
                           self.docker_interface.container_start(i) # try to start container
                   else:
                       if temp["enabled"] == True:
                          temp["enabled"] = False
                          self.ds_handlers["ERROR_STREAM"].push( data = { "container": i, "error_output" :"container disabled from running", "time":time.time() } )
                          self.docker_interface.container_stop(i)
                   self.ds_handlers["ERROR_STATE"].hset(container,temp)
               except:
                   pass
          
           


      
   def add_chains(self,cf):


       cf.define_chain("monitor_web_command_queue", True)
       cf.insert.wait_event_count( event = "TIME_TICK", count = 1)
       cf.insert.one_step(self.process_web_queue)
       cf.insert.reset()
       
       cf.define_chain("monitor_active_processes",True)
       cf.insert.wait_event_count( event = "TIME_TICK",count = 30)
       cf.insert.one_step(self.monitor)
       
       cf.insert.reset()




 
  

if __name__ == "__main__":
   
   cf = CF_Base_Interpreter()
    #
    #
    # Read Boot File
    # expand json file
    # 
   #time.sleep(20) # wait for mqtt server get started
   file_handle = open("/mnt/ssd/site_config/redis_server.json")
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)
  
   #print("--",site_data["site"],site_data["local_node"],container_name)
   qs = Query_Support( site_data )
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   
   node_sets, node_processes = qs.match_list(query_list)
   
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_relationship( query_list,relationship="DOCKER_MONITOR")
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "DATA_STRUCTURES" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
   
   #print("package_nodes",package_nodes)
   
   generate_handlers = Generate_Handlers(package_nodes[0],qs)
 
   system_control = Monitor_Containers(node_processes[0],package_nodes[0],generate_handlers)
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



