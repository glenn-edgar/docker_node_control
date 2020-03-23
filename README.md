This Repository does the following functions

Run a startup program to do the following
functions.

1.  Read configuration file with describe redis db and master status 

2A.  If the node is a master then 
   A. Start redis server container
   B. Start Utility container to setup graph data base
   C. Run Utility programs from Utility container
   D. Start Master pod container
   E. Start Slave pod container
  
2B.  If node is a slave node then
   A. Wait for redis server
   B. Start Slave pod Container
