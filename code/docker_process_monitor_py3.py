
  def assemble_vsz(self,*args):
      for i in self.container_list
          self.assemble_vsz_container(i)
       return "DISABLE"
       
   def assemble_rss(self,*args):
       for i in self.container_list
          self.assemble_rss_container(i)
       return "DISABLE"
       
       
  def assemble_vsz_container(self,container_id):
       data = self.vsz_handler(container_id)
       # get data structure
       self.ds_handlers["PROCESS_VSZ"].push( data =  data,local_node = self.site_node )
       return "DISABLE"
       
   def assemble_rss_container(self,container_id ):
       data = self.rss_handler(container_id)
       #get data structure
       self.ds_handlers["PROCESS_RSS"].push( data = data,local_node = container_name )
       return "DISABLE"
       
       
  def vsz_handler( self , container_id  ):
       container_name = xxx
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python")
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
                       return_value[key] = temp_value["VSZ"]
       
       return return_value
       
   def rss_handler( self , container_id  ):
       container_name = xxx
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("docker ps "+docker_container + "-aux | grep python")
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
                       return_value[key] = temp_value["RSS"]
       
       return return_value


   def construct_chains(self,*args):

       cf = CF_Base_Interpreter()
       cf.define_chain("pi_monitor", True)
       cf.insert.log("starting docker measurements")

      
       cf.insert.one_step(self.assemble_vsz)
       cf.insert.one_step(self.assemble_rss)
 
       cf.insert.log("ending docker measurements")
       cf.insert.wait_event_count( event = "MINUTE_TICK",count = 15)
       cf.insert.reset()
       cf.execute()
        
    
if __name__ == "__main__":
   
   
    #
    #
    # Read Boot File
    # expand json file
    # 
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)

  
   qs = Query_Support( site_data ) 
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "SYSTEM_MONITORING" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
  
   
   generate_handlers = Generate_Handlers(package_nodes[0],qs)
   pi_monitor = PI_MONITOR(package_nodes[0],generate_handlers,site_data["local_node"])
   
   
else:
   pass