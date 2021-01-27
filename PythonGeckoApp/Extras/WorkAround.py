import os
import sys
import numpy as np
import time as t
import csv
import pandas as pd
import xarray
import matplotlib.pyplot as plt
from SweepClass import SweepClass,losses
from GISMSParameters_phi import GISMSParameters_phi
import subprocess
import glob

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
global ginst
ginst = Inst.startNewRemoteInstance(GECKOPORT)
dt_step = 100e-9
t_end = 300e-3

# Open the simulation file.  Use java-strings:
print(simfilepath)
fname = JString(simfilepath)
print(fname)
ginst.openFile(fname)        
               

parameter = SweepClass()
parameter.vDC = [216,400,320]
parameter.loadS = [40000]
parameter.loadphi = [32,12,-32,25]
parameter.fS =  [7200,2000]
parameter.tHS = [95,100]
parameter.fOut = [50]
parameter.transistorArray = ["F3L300R07PE4_T_new"]
parameter.revDiodeArray = ["F3L300R07PE4_RD_new"]
parameter.fwdiodeArray = ["F3L300R07PE4_RD_new"]
from parasweep import run_sweep, CartesianSweep
sweep_params = {'Transistor':parameter.transistorArray,
                'Transistor_revD':parameter.revDiodeArray,
                'Transistor_fwD':parameter.fwdiodeArray,
                'V_DC':parameter.vDC,
                'Load_S':parameter.loadS,
                'Load_phi':parameter.loadphi,
                'f_s':parameter.fS,
                'T_HS':parameter.tHS,
                'f_out':parameter.fOut}
simName = 'params'

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

sweep = CartesianSweep(sweep_params)
mapping = run_sweep(command='echo {sim_id}>> D:\\thesis-research\\VS_code\\PythonGecko\\ParamsList\\fileSimId.txt',
                    configs=['D:\\thesis-research\\VS_code\\PythonGecko\\ParamsList\\gecko_{sim_id}.dat'],
                    templates=['D:\\thesis-research\\VS_code\\PythonGecko\\paramsTemplate.txt'],
                    sweep=sweep,
                    wait =True,verbose=False, sweep_id=simName)
print(mapping)
       
def startSIM(simId): 
        #ginst.connectToGecko()
        fileName =  'gecko_'+simId+'.dat'
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
        #ginst.saveFileAs(JString("D:\\thesis-research\\VS_code\\PythonGecko\\ParamsList\\3NPC_new.ipes"))
        ginst.set_dt(dt_step)  # Simulation time step
        ginst.set_Tend(t_end)  # Simulation time

        ginst.runSimulation()
        Indvd_losses = {}
        t_end_new = ginst.get_Tend()
        t_start = t_end_new-20e-3
        for x in loss_keys:
            Indvd_losses[x] = ginst.getSignalData(x,t_start,t_end_new,0)
        time = ginst.getTimeArray('D13_con',t_start,t_end_new,0);

        #print(IGBT_losses)
        

        with open("D:\\thesis-research\\VS_code\\PythonGecko\\GeckoExport\\"+simId+".csv", 'w') as csvfile: 
            writer = csv.writer(csvfile) 
            writer.writerow(loss_keys)
            writer.writerows(zip(*Indvd_losses.values())) 

#Read parameters from the generated files which represents the corresponding sweep operating conditions     
with open('D:\\thesis-research\\VS_code\\PythonGecko\\ParamsList\\fileSimId.txt') as simIdfile:
    for line in simIdfile: 
        simId = line.strip() #or some other preprocessing
        print(simId)
        #startSIM(simId)
#ginst.shutdown()


global count
count = 0
def get_output(sim_id):
    #print({sim_id})

    #df = pd.read_csv("D:\\thesis-research\\VS_code\\PythonGecko\\GeckoExport\\"+sim_id+".csv") 
    #df.fillna(0,inplace=True)
    #data = df.values
    #print('4*8 array stored in csv/txt file:')
    #print(data)
    data = losses()
    #count = count + 1,
    #filename = f'D:\\thesis-research\\VS_code\\PythonGecko\\GeckoExport\\'+sim_id+'.csv'
    #data = np.loadtxt(filename, delimiter=',', skiprows=1)
    return data

#lyap = mapping.to_dataframe(name=None, dim_order=None)

lyap = xarray.apply_ufunc(get_output, mapping,vectorize=True)
print(lyap)
#lyap.isel(Load_phi=1).to_netcdf('ROMS_example.nc', mode='w')




        
















