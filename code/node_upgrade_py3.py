
import json
import time
import os



redis_site_file = "/mnt/ssd/site_config/redis_server.json"
reboot_file = "/mnt/ssd/site_config/reboot_file.json"


container_run_script = "docker run -d  --restart on-failure  --name redis -p 6379:6379 --mount type=bind,source=/mnt/ssd/redis,target=/data  " 
container_run_script = container_run_script + " --mount type=bind,source=/mnt/ssd/redis/config/redis.conf,target=/usr/local/etc/redis/redis.conf redis"

def down_load_any_upgrades():
   
   try:
        file_handle = open(reboot_file,'r')   
        data = file_handle.read()
        file_handle.close()
        return  json.loads(data)
        
   except:
       os.system("rm "+reboot_file)
       exit()  # no file not reset
    
 
def upgrade_handler(input_message):
    
   
    if input_message['pod'][0] == True:
       os.system("./upgrade_pod_control.bsh")
      
     
 
    services = input_message["services"]
    for i in services:
       print("service "+i)
       os.system("docker pull "+i)
    containers = input_message["containers"]
    for i in containers:
       print("container "+i)
       os.system("docker pull "+i) 
    os.system("docker rmi -f $(docker images -qf dangling=true)")
    

 
#
#
# starting point
#
#
reload_data = down_load_any_upgrades()

#print(reload_data)
upgrade_handler(reload_data)






