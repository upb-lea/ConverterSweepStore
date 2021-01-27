"""
PyGeckoExample.py
GNU GPLv3
Copyright Mario Mauerer 2019
"""

import os
import sys
import numpy as np
import time as t
import csv
import matplotlib.pyplot as plt
from SweepClass import SweepClass
from GISMSParameters_phi import GISMSParameters_phi
"""
USER CONFIG:
"""
# The GeckoCIRCUITS simulation file.  Make sure to provide an absolute path
# (this is taken care of by the script below)
SIM_FILE_PATH = "3level_npc.ipes"
# Gecko communicates using sockets.  Provide a port:
GECKOPORT = 43036

"""
SCRIPT IMPLEMENTATION:
"""
# Get the current path of GeckoCIRCUITS:
curdir = os.path.dirname(os.path.abspath(__file__ + '\..\..'))
geckopath = curdir + "\GeckoCIRCUITS\GeckoCIRCUITS.jar"
simfilepath = curdir + "\\GeckoCIRCUITS\\" + SIM_FILE_PATH
lossfilepath = "D:\\thesis-research\\VS_code\\workspace"
# For java.  This must be before the jnius-imports:
os.environ['CLASSPATH'] = geckopath

igbtLen = 12
dfwLen = 6


from jnius import autoclass

# The class to control GeckoCIRCUITS:
Inst = autoclass('gecko.GeckoRemoteObject')
# Note that parameters must be passed as java-strings to Gecko, as it otherwise
# throws a fit:
JString = autoclass('java.lang.String')

# Start GeckoCIRCUITS.  This opens the Gecko window:
ginst = Inst.startNewRemoteInstance(GECKOPORT)
t.sleep(5)
dt_step = 0.005
t_end = 0.02
ginst.set_dt(dt_step)  # Simulation time step
ginst.set_Tend(t_end)  # Simulation time
# No pre-simulation:
ginst.set_dt_pre(0)
ginst.set_Tend_pre(0)
# Open the simulation file.  Use java-strings:
print(simfilepath)
fname = JString(simfilepath)
print(fname)
ginst.openFile(fname)

Filter_C = 3.516e-3
Filter_L = 117.33e-6
U_Load_LL = 115

IGBT_loss_keys = ['IG1_con','IG3_con','IG1_sw','IG3_sw','IG2_con','IG4_con','IG2_sw','IG4_sw']
DREV_loss_keys = ['D1_con','D3_con','D1_sw','D3_sw','D2_con','D4_con','D2_sw','D4_sw']
DFW_loss_keys = ['D13_con','D14_con','D13_sw','D14_sw']
#Read parameters from the generated files which represents the corresponding sweep operating conditions
simId = sys.argv[1]
print(simId)
fileName =  'gecko_'+sys.argv[1]+'.dat'
fileObj = open('D:\\thesis-research\\VS_code\\PythonGecko\\ParamsList\\'+fileName)
params = {}
for line in fileObj:
    line = line.strip()
    if not line.startswith("#"):
        key_value = line.split("=")
        if len(key_value) == 2:
            params[key_value[0].strip()] = key_value[1].strip()

params["Transistor"] = str(params["Transistor"])
params["Transistor_revD"] = str(params["Transistor_revD"])
params["Transistor_fwD"] = str(params["Transistor_fwD"])
params["V_DC"] = float(params["V_DC"])
params["Load_S"] = float(params["Load_S"])
params["Load_phi"] = float(params["Load_phi"])
params["f_s"] = float(params["f_s"])
params["T_HS"] = int(params["T_HS"])
params["f_out"] = int(params["f_out"])

#intialization starts from here
for igI in range(igbtLen):
    ginst.doOperation(JString("IGBT."+ str(igI+1)),JString("setLossFile"),JString(lossfilepath+"\\"+ params["Transistor"]+".scl"))
    ginst.doOperation(JString("D."+str(igI+1)),JString("setLossFile"),JString(lossfilepath+"\\"+params["Transistor_revD"]+".scl"))
for fdI in range(dfwLen):
    ginst.doOperation(JString("D."+str(fdI+13)),JString("setLossFile"),JString(lossfilepath+"\\"+params["Transistor_fwD"]+".scl"))
# Set the global parameters in the simulation file: These parameters must be
# defined in Tools->Set Parameters in
# the GUI.
# This is how the simulation file can be adapted/scripted.
out = GISMSParameters_phi(params["V_DC"], U_Load_LL, params["f_out"], Filter_L, Filter_C, params["Load_S"], params["Load_phi"], 1)
parname = JString("$fout")
ginst.setGlobalParameterValue(parname,params["f_out"])
parname = JString("$fsw")
ginst.setGlobalParameterValue(parname,params["f_s"])
parname = JString("$Udc")
ginst.setGlobalParameterValue(parname,(params["V_DC"]) / 2)
parname = JString("$uDC_t")
ginst.setGlobalParameterValue(parname,params["T_HS"])
parname = JString("$uDC_rd")
ginst.setGlobalParameterValue(parname,params["T_HS"])
parname = JString("$uDC_fd")
ginst.setGlobalParameterValue(parname,params["T_HS"])
parname = JString("$m")
ginst.setGlobalParameterValue(parname,out["m"])
parname = JString("$Ipeak_inv")
ginst.setGlobalParameterValue(parname,out["I_Peak_inv"])
for i in range (3):
    ginst.setParameter(JString("Iout."+ str(i+1)),"phase",out["phi_degree_inv"]+(i)*120)
ginst.runSimulation()
IGBT_losses = {}
Drev_losses = {}
FD_losses = {}
for x in IGBT_loss_keys:
    IGBT_losses[x] = ginst.getSignalData(x,0,t_end,0)
for y in IGBT_loss_keys:
    Drev_losses[x] = ginst.getSignalData(y,0,t_end,0)
for z in IGBT_loss_keys:
    FD_losses[x] = ginst.getSignalData(z,0,t_end,0)
time = ginst.getTimeArray('D13_con',0,t_end,0);

print(IGBT_losses)
ginst.disconnectFromGecko()
ginst.shutdown()
print(simId)

with open("D:\\thesis-research\\VS_code\\PythonGecko\\GeckoExport\\"+simId+".csv", 'w') as csvfile: 
    writer = csv.writer(csvfile) 
    writer.writerow(IGBT_loss_keys)
    writer.writerows(zip(*IGBT_losses.values())) 






