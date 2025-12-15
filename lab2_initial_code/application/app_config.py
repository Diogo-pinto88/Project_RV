#!/usr/bin/env python
# #####################################################################################################
# APP CONFIGURATION PARAMETERS -
#######################################################################################################

# #####################################################################################################
# Other layers debug options usefull to test the application
# #####################################################################################################
# print location
debug_location = 0             #print nodes coordinates

# print application data
debug_app = 1                   #print information of the commands executed (rsu and obu)
debug_rsu = 1                   #print information of the rsu commands executed 
debug_obu = 1                   #print information of the obu commands executed 
debug_app_ca = 0                #print ca messages trigerred and received (application layer)
debug_app_den = 0               #print den messages sent and received (application layer)
debug_app_spat = 0              #print spat messages sent and received (application layer)
debug_app_ivim = 0              #print ivim messages sent and received (application layer)

debug_geo_net = 0               #print geo_networking messages
debug_beacon = 0                #print beaconing messages
debug_multicast = 0             #print multicast packets received and send  
debug_physical_layer = 0        #print physical layer emulation messages

# print control data
debug_gpio = 0                  #print gpio functions (car_motor_functions and rsu_control_functions)
debug_obu_control = 0           #print  high level obu control information (car_motor_functions)
debug_rsu_control = 0           #print rsu high level control information (car_motor_functions  rsu_control_functions)level rsu control information (rsu_control_functions)

# print sys data
debug_sys = 0                   #print SO-related information

# #####################################################################################################
# Local test (laptop) or SmartMob platform test
# local_test = 0 if code when using the raspberry pies
# #####################################################################################################
local_test = 1

#------------------------------------------------------------------------------------------
#include here any specific configuration of the application
#------------------------------------------------------------------------------------------
time_interval = 1           #wait time between consecutive movements updates
  