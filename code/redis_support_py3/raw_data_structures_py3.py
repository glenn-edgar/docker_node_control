import msgpack

class Raw_Key_Data_Handlers(object):

   def __init__(self,redis_handle):
       self.redis_handle = redis_handle
       
       
  
   def stream_range(self,key, start_timestamp,end_timestamp):
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)
       temp = self.redis_handle.execute_command("XRANGE", key,start_timestamp,end_timestamp) 
       return_value =[]
       for i in temp:  
         try:
           return_item= {}
           i = list(i)
           i[0] = i[0].decode()
           ids = i[0].split("-")
           return_item["id"] = i[0]
           return_item["timestamp"] = float(ids[0])/1000.
           return_item["sub_id"] = int(ids[1])
           packed_data = i[1][b'data']
           return_item["data"] = msgpack.unpackb(packed_data)
           return_value.append(return_item)
         except:
            print("packed_data",packed_data)
            raise
       return return_value                  
       

   def stream_trim(self,key,length):
       length = int(length)
       #print("key",key,length)
       self.redis_handle.execute_command("XTRIM",key,'MAXLEN','~', length)
      
   def job_queue_trim(self,key,data,length):
       self.redis_handle.ltrim(key,0,length)
  
           
       
   def job_queue_push(self,key,data,length):
       pack_data =  msgpack.packb(data )
       self.redis_handle.lpush(key,pack_data)
       self.redis_handle.ltrim(key,0,length)
  
       
   def job_queue_pop(self,key):
       pack_data = self.redis_handle.rpop(key)
       
       if pack_data == None:
          return  None
       else:
          print("pack_data",pack_data)  
          return msgpack.unpackb(pack_data)     