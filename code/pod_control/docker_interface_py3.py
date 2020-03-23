import docker
import os


class Docker_Interface(object):

   def __init__(self):
       self.client = docker.from_env()

   def containers_ls_runing(self): # tested
       container_list = self.client.containers.list()
       return self.look_up_containers(container_list)
       
   def containers_ls_all(self): #tested
       container_list = self.client.containers.list(all=True)
       return self.look_up_containers(container_list)
       
       
   def container_start(self,container): #tested
       i = self.client.containers.get(container)
       i.start()
       
       
   def container_stop(self,container): #tested
       i = self.client.containers.get(container)
       i.stop()
       
   def container_up(self,container,startup_script): #tested
       container_object = self.get(container)
       if container_object == None:
          os.system(startup_script)
       else:
          self.container_start(container)
       
   def container_rm(self,container): # tested
       container_object = self.client.containers.get(container)
       if container_object != None:
          container_object.remove()

   def images(self): #tested
       return self.client.images.list()
   
   def image_rmi(self,deleted_image): # tested
       self.client.images.remove(image=deleted_image)

   def look_up_containers(self,container_list): #tested
       return_value = []
       for container_name in container_list:
           container_object =  self.get(container_name)
           return_value.append(container_object) 
       return return_value    

       
   def get(self,id): # tested
       try:
           i = self.client.containers.get(id)
           temp = {}
           temp["image"] = i.image
           temp["name"]  = i.name
           temp["status"] =i.status
           return temp
       except:
           return None       

   def upgrade_container(self,container,build_script):

       if self.get(container) != None:
           self.container_stop(container)
           self.container_rm(container)
       try:
           self.image_rmi(container)
       except:
          pass
       os.system(build_script)
       
 
          
   
if __name__ == "__main__":
   docker_interface = Docker_Interface()
   #print(docker_interface.containers_ls_runing())
   #print(docker_interface.containers_ls_all())
   #print(docker_interface.get("redis"))
   #print(docker_interface.container_stop("redis"))
   #print(docker_interface.container_start("redis"))
   #print(docker_interface.images())
   #print(docker_interface.look_up_containers(["redis"]))    
   #print(docker_interface.container_rm("redis"))
   print(docker_interface.upgrade_container("redis",'/home/pi/pod_control/docker_images/redis/docker_run.bsh'))
   