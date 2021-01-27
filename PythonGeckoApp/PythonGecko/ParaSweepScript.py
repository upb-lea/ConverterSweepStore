
import os
import sys
import numpy as np
import time as t
import csv
import pandas as pd
from retrying import retry
from GISMSParameters_phi import GISMSParameters_phi
import glob
import psweep as ps
import subprocess

files = glob.glob('D:\\thesis-research\\VS_code\\PythonGecko\\ParamsList\\*')
for f in files:
    os.remove(f)
"""
USER CONFIG:
"""
# The GeckoCIRCUITS simulation file.  Make sure to provide an absolute path
# (this is taken care of by the script below)
SIM_FILE_PATH = "3level_npc_therm.ipes"
# Gecko communicates using sockets.  Provide a port:
GECKOPORT = 43036

"""
SCRIPT IMPLEMENTATION:
"""
# Get the current path of GeckoCIRCUITS:
curdir = os.path.dirname(os.path.abspath(__file__ + '\..\..'))
geckopath = curdir + "\GeckoCIRCUITS\GeckoCIRCUITS.jar"
simfilepath = curdir + "\\GeckoCIRCUITS\\" + SIM_FILE_PATH
lossfilepath = curdir+"\\workspace"
# For java.  This must be before the jnius-imports:
os.environ['CLASSPATH'] = geckopath

igbtLen = 12
dfwLen = 6
def retry_if_result_none(result):
    return result is None

from jnius import autoclass

# The class to control GeckoCIRCUITS:
Inst = autoclass('gecko.GeckoRemoteObject')
# Note that parameters must be passed as java-strings to Gecko, as it otherwise
# throws a fit:
JString = autoclass('java.lang.String')

# Start GeckoCIRCUITS.  This opens the Gecko window:
global ginst
@retry(retry_on_result=retry_if_result_none)
def intiateConnection():
    t.sleep(1)
    connect = Inst.startNewRemoteInstance(GECKOPORT)
    return connect

# Open the simulation file.  Use java-strings:
fname = JString(simfilepath)
ginst = intiateConnection()
ginst.openFile(fname)        

#time step and simulation time
dt_step = 100e-9
t_end = 300e-3

#parameter goes in here
vDC = [216]
loadS = [40000]
loadphi = [32]
fS =  [7200]
tHS = [95]
fOut = [50]
transistorArray = ["F3L300R07PE4_T_new"]
revDiodeArray = ["F3L300R07PE4_RD_new"]
fwdiodeArray = ["F3L300R07PE4_RD_new"]

igbtList = ps.plist('Transistor',transistorArray)
revDiodeList = ps.plist('Transistor_revD',revDiodeArray)
fwDiodeList = ps.plist('Transistor_fwD',fwdiodeArray)
dcVoltage = ps.plist('V_DC',vDC)
loadS = ps.plist('Load_S',loadS)
cosPhi = ps.plist('Load_phi',loadphi)
switchFreq = ps.plist('f_s',fS)
temp = ps.plist('T_HS',tHS)
fOut = ps.plist('f_out',fOut)
#file = ps.plist('file',file)
paramsList = ps.pgrid(igbtList,revDiodeList,fwDiodeList,dcVoltage,loadS,cosPhi,switchFreq,temp,fOut)

Filter_C = 3.516e-3
Filter_L = 117.33e-6
U_Load_LL = 115
R_jc = 0.16
Rd_jc = 0.32
Cth_ig = 0.2381
Cth_d = 0.1233
R_th = 0.063
loss_keys = ['IG1_con','IG3_con','IG1_sw','IG3_sw','IG2_con','IG4_con','IG2_sw','IG4_sw','D1_con','D3_con','D1_sw','D3_sw','D2_con','D4_con','D2_sw','D4_sw',
                  'D13_con','D14_con','D13_sw','D14_sw']


def startSIM(pset): 
        #ginst.connectToGecko()
        params = {}
        saveData = False;
        params["Transistor"] = pset["Transistor"]
        params["Transistor_revD"] = pset["Transistor_revD"]
        params["Transistor_fwD"] = pset["Transistor_fwD"]
        params["V_DC"] = float(pset["V_DC"])
        params["Load_S"] = float(pset["Load_S"])
        params["Load_phi"] = float(pset["Load_phi"])
        params["f_s"] = float(pset["f_s"])
        params["T_HS"] = int(pset["T_HS"])
        params["f_out"] = int(pset["f_out"])

        
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
        # setting the thermanl network parameters
        parname = JString("$R_JC")
        ginst.setGlobalParameterValue(parname,R_jc)
        parname = JString("$Rd_JC")
        ginst.setGlobalParameterValue(parname,Rd_jc)
        parname = JString("$R_CS")
        ginst.setGlobalParameterValue(parname,R_th)
        parname = JString("$Cth_ig")
        ginst.setGlobalParameterValue(parname,Cth_ig)
        parname = JString("$Cth_d")
        ginst.setGlobalParameterValue(parname,Cth_d)
        
        #calculation og GISMS parameters and assigning to global parameters in GECKO circuits
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
        #if required to save this sweep file
        #ginst.saveFileAs(JString("D:\\thesis-research\\VS_code\\PythonGecko\\IPESFolder\\3NPC_sweep_"+pset['_pset_id']+".ipes"))
        ginst.set_dt(dt_step)  # Simulation time step
        ginst.set_Tend(t_end)  # Simulation time

        ginst.runSimulation()
        meanLosses = {}
        t_end_new = ginst.get_Tend()
        t_start = t_end_new-20e-3
        saveLossData = {}
        for x in loss_keys:
             losses = ginst.getSignalData(x,t_start,t_end_new,0)
             lossesArray = np.array(losses)
             if saveData :
                saveLossData[x] = losses                
             meanLosses[x] = np.mean(lossesArray)
            #print(meanLosses[x])
        time = ginst.getTimeArray('D13_con',t_start,t_end_new,0);
        #set saveData to True if required to save the simulated loss data over the time range in CSV format
        if saveData:
            fn = os.path.join(pset['_calc_dir'],
                      pset['_pset_id'])
            cmd = "mkdir {fn}".format(fn=fn)
            subprocess.run(cmd, shell=True)
            with open(fn+"\\losses.csv", 'w') as csvfile: 
                writer = csv.writer(csvfile) 
                writer.writerow(loss_keys)
                writer.writerows(zip(*saveLossData.values())) 
            meanLosses['file'] = fn+"\\losses.csv"
        else :
            meanLosses['file'] = "NA";
        return meanLosses

df = ps.run(startSIM, paramsList)
print(df)




        
















