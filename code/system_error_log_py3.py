
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
import time
class System_Error_Logging(object):
   def __init__(self,qs,container,site_data):
       self.container = container
       self.site_data = site_data
       self.qs = qs
       
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="SYSTEM_MONITOR" )
       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"SYSTEM_MONITOR"} )
                                           
       package_sets, package_sources = qs.match_list(query_list) 
       data_structures = package_sources[0]["data_structures"]
       generate_handlers = Generate_Handlers(package_sources[0],self.qs)
       self.handlers = {}
       self.handlers["SYSTEM_STATUS"] = generate_handlers.construct_hash(data_structures["SYSTEM_STATUS"])
       self.handlers["SYSTEM_ALERTS"] = generate_handlers.construct_stream_writer(data_structures["SYSTEM_ALERTS"] )

	
	
   def log_error_message(self,message):
        log_value = {}
        #print(self.site_data)
        log_value["processor"] = self.site_data["local_node"]
        log_value["container"] = self.container
        log_value["error_msg"] = message
        log_value["time"] = time.time()
		
        self.handlers["SYSTEM_STATUS"].hset(self.container,log_value)
        self.handlers["SYSTEM_ALERTS"].push( log_value )