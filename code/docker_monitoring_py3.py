from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from pod_control.docker_interface_py3 import Docker_Interface
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
import json 
import time
import os

class Monitor_Containers(object):
   def __init__(self,site_data):
       self.site_data = site_data
       self.qs =  Query_Support( site_data )
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
       query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
       node_sets, processor_node = qs.match_list(query_list)
   
   
   
   
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
       query_list = qs.add_match_relationship( query_list,relationship="DOCKER_MONITOR")
       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "DATA_STRUCTURES" )
                                        
                                        
                                           
       package_sets, package_nodes = qs.match_list(query_list)  
   
       #print("package_nodes",package_nodes)
   
       generate_handlers = Generate_Handlers(package_nodes[0],qs)      
       processor_node = processor_node[0]
       services = set(processor_node["services"])
       containers = set(processor_node["containers"])
       containers_list = containers.union(services)
       self.container_list = list(containers)     
          
       self.docker_interface =  Docker_Interface()        
       package_node = package_nodes[0]
       data_structures = package_node["data_structures"]
       
       #print(data_structures.keys())
       self.ds_handlers = {}
       self.ds_handlers["ERROR_STREAM"]        = generate_handlers.construct_redis_stream_writer(data_structures["ERROR_STREAM"])
       self.ds_handlers["ERROR_STATE"]        = generate_handlers.construct_hash(data_structures["ERROR_HASH"])
       self.ds_handlers["WEB_COMMAND_QUEUE"]   = generate_handlers.construct_job_queue_server(data_structures["WEB_COMMAND_QUEUE"])
       self.ds_handlers["ERROR_STATE"].delete_all()
       self.setup_environment()
       self.check_for_allocated_containers()
       
       
       self.docker_performance_data_structures= {}
       self.managed_containter_list = self.determine_managed_containers()
       
       
       for i in self.container_list:
           self.docker_performance_data_structures[i] = self.assemble_container_data_structures(i)
          

   def determine_managed_containers(self):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       query_list = self.qs.add_match_relationship( query_list,relationship="PROCESSOR",label=self.site_data["local_node"] )
       query_list = self.qs.add_match_terminal( query_list,relationship="CONTAINER")
       package_sets, manage_nodes = self.qs.match_list(query_list)
       managed_container_list = []
       for i in manage_nodes:
           managed_container_list.append(i["name"])
       return managed_container_list          

   def assemble_container_data_structures(self,container_name):
       
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site_data["site"] )
       query_list = self.qs.add_match_relationship( query_list,relationship="PROCESSOR",label=self.site_data["local_node"] )
       query_list = self.qs.add_match_relationship( query_list,relationship="CONTAINER",label=container_name)
       query_list = self.qs.add_match_terminal( query_list, 
                                           relationship = "PACKAGE", label = "DATA_STRUCTURES" )

       package_sets, package_nodes = self.qs.match_list(query_list)  
      
 
           
       #print("package_nodes",package_nodes)
   
       generate_handlers = Generate_Handlers(package_nodes[0],self.qs)
       data_structures = package_nodes[0]["data_structures"]
      
       handlers = {}
       handlers["PROCESS_VSZ"]  = generate_handlers.construct_redis_stream_writer(data_structures["PROCESS_VSZ"])
       handlers["PROCESS_RSS"] = generate_handlers.construct_redis_stream_writer(data_structures["PROCESS_RSS"])
       handlers["PROCESS_CPU"]  = generate_handlers.construct_redis_stream_writer(data_structures["PROCESS_CPU"])
       return handlers

      
   def setup_environment(self):
        for i in self.container_list:
           self.ds_handlers["ERROR_STATE"].hset(i,{"name":i,"enabled":True,"active":True,"error":False,"defined":True})
           
   def check_for_allocated_containers(self):
       existing_containers = self.docker_interface.containers_ls_all()
       #print("exiting_containers",existing_containers)
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
       
       cf.define_chain("process_monitor", True)
       cf.insert.log("starting docker process measurements")

      
       cf.insert.one_step(self.measure_container_processes)
       
 
       cf.insert.log("ending docker measurements")
       cf.insert.wait_event_count( event = "MINUTE_TICK",count = 15)
       cf.insert.reset()


   def measure_container_processes(self,*args):
   
       for i in self.container_list:
           self.measure_ps_parameter(i,"%CPU","PROCESS_CPU")
           self.measure_ps_parameter(i,"VSZ","PROCESS_VSZ"),
           self.measure_ps_parameter(i,"RSS","PROCESS_RSS")

   def measure_ps_parameter( self , container_name,field_name,stream_name ):
       handlers = self.docker_performance_data_structures[container_name]
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("docker top "+container_name+ "  -aux | grep python")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = {}
       for i in range(0,len(lines)):
           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               
               if "PARAMETER1" in temp_value:
                   if temp_value["COMMAND"] == "python":
                       key = temp_value["PARAMETER1"]
                       return_value[key] = temp_value[field_name]
                       
                       
       #print(return_value,container_name)  
       handlers[stream_name].push( data = return_value,local_node = container_name )
      
 


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
 
   system_control = Monitor_Containers(site_data)
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



