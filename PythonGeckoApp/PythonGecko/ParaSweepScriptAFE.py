

import os
import sys
import numpy as np
import time as t
import csv
import pandas as pd
from retrying import retry
from AFEParameters import AFE_Parameters
import glob
import psweep as ps
import subprocess

thermal_file_path = r'calc\Thermal\params.csv'

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
geckopath = curdir + "\\GeckoCIRCUITS\\GeckoCIRCUITS.jar"
simfilepath = curdir + "\\InverterModels\\" + SIM_FILE_PATH
lossfilepath = curdir+"\\workspace"
# For java.  This must be before the jnius-imports:
os.environ['CLASSPATH'] = geckopath

igbtLen = 12
dfwLen = 6
def retry_if_result_none(result):
    return result is None
try :
    from jnius import autoclass
except :
    os.environ['JDK_HOME'] = "C:\\Program Files\\Java\\jdk1.8.0_281"
    os.environ['JAVA_HOME'] = "C:\\Program Files\\Java\\jdk1.8.0_281"
    os.environ['PATH'] += ';C:\\Program Files\\Java\\jdk1.8.0_281\\jre\\bin\\server\\;C:\\Program Files\\Java\\jdk1.8.0_281\\bin\\;E:\\mnagella_data\\PyGeckoCircuits\\GeckoCIRCUITS\\GeckoCIRCUITS.jar'
    from jnius import autoclass
# The class to control GeckoCIRCUITS:
Inst = autoclass('gecko.GeckoRemoteObject')
# Note that parameters must be passed as java-strings to Gecko, as it otherwise
# throws a fit:
JString = autoclass('java.lang.String')
       
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
MainsApp = [25000]
MainsPhi = [0]
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
MainsS = ps.plist('Mains_S',MainsApp)
MainscosPhi = ps.plist('Mains_phi',MainsPhi)
switchFreq = ps.plist('f_s',fS)
temp = ps.plist('T_HS',tHS)
fOut = ps.plist('f_out',fOut)
#file = ps.plist('file',file)
paramsList = ps.pgrid(igbtList,revDiodeList,fwDiodeList,dcVoltage,MainsS,MainscosPhi,switchFreq,temp,fOut)
Filter_C = 3.516e-3
Filter_L = 117.33e-6
U_Load_LL = 115
#Transformer values
Kt_Transformer = 1.377;
R_Fe_Transformer = 52;
R_S_Transformer = 10.88e-3 * Kt_Transformer;
L_par = 20e-3;

loss_keys = ['IG1_con','IG1_sw','IG3_con','IG3_sw','IG2_con','IG2_sw','IG4_con','IG4_sw','D1_con','D1_sw','D3_con','D3_sw','D2_con','D2_sw','D4_con','D4_sw',
                          'D13_con','D13_sw','D14_con','D14_sw']
temp_keys = ['Igbt1Temp','Igbt2Temp','D1Temp','D2Temp','DcTemp']

def startSIM(pset): 
       #ginst.connectToGecko()
    saveData = False
    params = {}
    thermalSet = {}
    params["Transistor"] = pset["Transistor"]
    params["Transistor_revD"] = pset["Transistor_revD"]
    params["Transistor_fwD"] = pset["Transistor_fwD"]
    params["V_DC"] = float(pset["V_DC"])
    params["Mains_S"] = float(pset["Mains_S"])
    params["Mains_phi"] = float(pset["Mains_phi"])
    params["f_s"] = float(pset["f_s"])
    params["T_HS"] = int(pset["T_HS"])
    params["f_out"] = int(pset["f_out"])
    global thermal_file_path
    df = pd.read_csv(thermal_file_path,index_col =['Datasheet'])
    thermalTransData = df.loc[df.index ==params["Transistor"]].to_dict(orient = 'index')
    thermalRevDiodeData = df.loc[df.index ==params["Transistor_revD"]].to_dict(orient = 'index')
    thermalFWDiodeData = df.loc[df.index ==params["Transistor_fwD"]].to_dict(orient = 'index')
    Rt_jc = thermalTransData[params["Transistor"]]['Rjc']
    Rt_cs = thermalTransData[params["Transistor"]]['Rcs']
    Cth_ig = thermalTransData[params["Transistor"]]['Cth']
    Rev_jc = thermalRevDiodeData[params["Transistor_revD"]]['Rjc']
    Rev_cs = thermalRevDiodeData[params["Transistor_revD"]]['Rcs']
    Cth_rev = thermalRevDiodeData[params["Transistor_revD"]]['Cth']
    Rfw_jc = thermalFWDiodeData[params["Transistor_fwD"]]['Rjc']
    Rfw_cs = thermalFWDiodeData[params["Transistor_fwD"]]['Rcs']
    Cth_fwd = thermalFWDiodeData[params["Transistor_fwD"]]['Cth']
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
    ginst.setGlobalParameterValue(parname,Rt_jc)
    parname = JString("$R_CS")
    ginst.setGlobalParameterValue(parname,Rt_cs)
    parname = JString("$Cth_ig")
    ginst.setGlobalParameterValue(parname,Cth_ig)
    parname = JString("$Rev_JC")
    ginst.setGlobalParameterValue(parname,Rev_jc)
    parname = JString("$Rev_CS")
    ginst.setGlobalParameterValue(parname,Rev_cs)
    parname = JString("$Cth_rev")
    ginst.setGlobalParameterValue(parname,Cth_rev)
    parname = JString("$Rfw_JC")
    ginst.setGlobalParameterValue(parname,Rfw_jc)
    parname = JString("$Rfw_CS")
    ginst.setGlobalParameterValue(parname,Rfw_cs)
    parname = JString("$Cth_fwd")
    ginst.setGlobalParameterValue(parname,Cth_fwd)
    
    
    #calculation og GISMS parameters and assigning to global parameters in GECKO circuits
    out = AFE_Parameters(params["V_DC"], U_Load_LL, params["f_out"], Filter_L, Filter_C, params["Mains_S"], params["Mains_phi"],R_Fe_Transformer,R_S_Transformer,L_par, 1)
    out['U_Load_LL'] = U_Load_LL
    
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
    out["phi_degree_inv"] = 180+out["phi_degree_inv"]
    for i in range (3):
        ginst.setParameter(JString("Iout."+ str(i+1)),"phase",out["phi_degree_inv"]+(i)*120)
    #if required to save this sweep file
    #ginst.saveFileAs(JString("D:\\thesis-research\\VS_code\\PythonGecko\\IPESFolder\\3NPC_sweep_"+pset['_pset_id']+".ipes"))
    ginst.set_dt(dt_step)  # Simulation time step
    ginst.set_Tend(t_end)  # Simulation time
    ginst.runSimulation()
    meanLosses = {}
    meanTemp = {}
    t_end_new = ginst.get_Tend()
    t_start = t_end_new-20e-3
    saveLossData = {}
    saveTempData = {}
    totalLoss = 0
    meanLosses['TransformerLoss'] = out['P_Transformer']
    for x in loss_keys:
        losses = ginst.getSignalData(x,t_start,t_end_new,0)
        lossesArray = np.array(losses)
        if saveData :
            saveLossData[x] = losses            
        meanLosses[x] = np.mean(lossesArray)
        totalLoss = totalLoss + meanLosses[x]
        
    meanLosses['InvTotalLoss'] = totalLoss*3
    length = len(loss_keys)
    i=0
    while i < length:
        key = loss_keys[i+1]
        key = key[:-3] #remove _sw from key
        meanLosses[key] = meanLosses[loss_keys[i]] + meanLosses[loss_keys[i+1]]
        i+=2
    for x in temp_keys:
        temp = ginst.getSignalData(x,t_start,t_end_new,0)
        tempArray = np.array(temp)
        if saveData :
            saveTempData[x] = temp            
        meanTemp[x] = np.mean(tempArray)
            #print(meanLosses[x])
    time = ginst.getTimeArray('D13_con',t_start,t_end_new,0);
    #ginst.disconnectFromGecko()
    #set saveData to True if required to save the simulated loss data over the time range in CSV format
    if saveData:
        fn = os.path.join(pset['_calc_dir'],
                  pset['_pset_id'])
        cmd = "mkdir {fn}".format(fn=fn)
        subprocess.run(cmd, shell=True)
        with open(fn+"\\losses.csv", 'w') as csvfile: 
            writer = csv.writer(csvfile) 
            writer.writerow(loss_keys+temp_keys)
            comboData = {**saveLossData, **saveTempData}
            writer.writerows(zip(*comboData.values())) 
        meanLosses['file'] = fn+"\\losses.csv"
    else :
        meanLosses['file'] = "NA"
    return {**meanLosses, **meanTemp}
      
df = ps.run(startSIM, paramsList, calc_dir='calc_AFE')
      
print(df)