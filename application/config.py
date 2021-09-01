


#### Secret key config for running on cloud serve. Un-comment this to run application on remote server ######

# import os 
# import json 

# with open('/etc/config.json') as config_file:
#      config = json.load(config_file)
     
# class Config:
#     SECRET_KEY = config.get('SECRET_KEY')









### Secret key config for running on local machine. Leave this uncommented to run locally ####
 
import os 

class Config:
    SECRET_KEY = os.urandom(32)
