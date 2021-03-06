import sys
import re
import os
import numpy as np
import time as t
import csv
import pandas as pd
from retrying import retry
from GISMSParameters_phi import GISMSParameters_phi
from AFEParameters import AFE_Parameters
import glob
import psweep as ps
import subprocess
from PyQt5 import QtCore, QtGui 
from PyQt5.QtCore import QThread,pyqtSignal,QObject
from PyQt5.QtWidgets import QMessageBox
class startConnection(QObject):
    gismsUpdate = pyqtSignal([dict])
    progressUpdate = pyqtSignal(int,str)
    thermal_file_path = r'calc\Thermal\params.csv'
    datasheetpath = r'calc\Thermal\DatasheetDB.csv'
    def __init__(self,dataimport,saveData,isAfeSelected,topology):
        super().__init__()
        self.params = dataimport
        self.saveData = saveData
        self.afeMode = isAfeSelected
        self.topology = {"Topology":topology}
    def eventemit(self):
        print('we are inside')
        print(self.params)
        self.gismsUpdate.emit()

    def getComponentSCLs(self, datasheet) :
            igbtDatasheets = []
            diodeDatasheets = []
            clampDatasheets = []
            df = pd.read_csv(self.datasheetpath)
            topology = self.topology["Topology"]
            deviceSheetInfo = df[(df['Topology'] == topology)&(df['Datasheet']==datasheet)]
            if topology == 'NPC':
                igbtDatasheets = deviceSheetInfo[['T1','T2','T3','T4']].to_dict(orient='records')[0]
                diodeDatasheets = deviceSheetInfo[['D1','D2','D3','D4']].to_dict(orient='records')[0]
                clampDatasheets = deviceSheetInfo[['D5','D6']].to_dict(orient='records')[0]
                return igbtDatasheets,diodeDatasheets,clampDatasheets
            if topology == 'TNPC':
                igbtDatasheets = deviceSheetInfo[['T1','T2','T3','T4']].values.tolist()
                diodeDatasheets = deviceSheetInfo[['D1','D2','D3','D4']].values.tolist()
                return igbtDatasheets,diodeDatasheets
            if topology == 'B6':
                igbtDatasheets = deviceSheetInfo[['T1','T2']].values.tolist()
                diodeDatasheets = deviceSheetInfo[['D1','D2']].values.tolist()
                return igbtDatasheets,diodeDatasheets

    def initiateConnection(self):
        
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
        self.progressUpdate.emit(-1,'Starting Gecko')
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
        if ginst!= None :
            self.progressUpdate.emit(-1,'Connected')
        else :
            self.progressUpdate.emit(-1,'Failed')
        ginst.openFile(fname)        

        # Time step and simulation time
        dt_step = 100e-9
        t_end = 300e-3
       
        # Gathering parameters goes in here
        dataSheets = ps.plist('Datasheet',self.params['dataSheets'])
        dcVoltage = ps.plist('V_DC',self.params['V_DC'])
        switchFreq = ps.plist('f_s',self.params['f_s'])
        temp = ps.plist('T_HS',self.params['T_HS'])
        fOut = ps.plist('f_out',self.params['f_out'])
        if self.afeMode:
            MainsS = ps.plist('Mains_S',self.params['Mains_S'])
            MainsPhi = ps.plist('Mains_phi',self.params['Mains_phi'])
            paramsList = ps.pgrid([self.topology],dataSheets,dcVoltage,MainsS,switchFreq,MainsPhi,temp,fOut)
        else :            
            loadS = ps.plist('Load_S',self.params['Load_S'])
            Phi = ps.plist('Load_phi',self.params['Load_phi'])
            paramsList = ps.pgrid([self.topology],dataSheets,dcVoltage,loadS,switchFreq,Phi,temp,fOut)
        incrementor = 100/len(paramsList)
        # Filter Values
        Filter_C = 3.516e-3
        Filter_L = 117.33e-6
        U_Load_LL = 115
        U_Mains_LL = 115
        # Transformer values
        Kt_Transformer = 1.377;
        R_Fe_Transformer = 52;
        R_S_Transformer = 10.88e-3 * Kt_Transformer;
        L_par = 20e-3;
        count = 0
        def startSimNPC(pset): 
            # Defining loss keys: order is important!
            loss_keys = ['IG1_con','IG1_sw','IG3_con','IG3_sw','IG2_con','IG2_sw','IG4_con','IG4_sw','D1_con','D1_sw','D3_con','D3_sw','D2_con','D2_sw','D4_con','D4_sw',
                          'D13_con','D13_sw','D14_con','D14_sw']
            temp_keys = ['Igbt1Temp','Igbt2Temp','D1Temp','D2Temp','DcTemp']
            #ginst.connectToGecko()
            params = {}
            thermalSet = {}
            nonlocal  count
            count+=1;
            
            # Getting required paramters for either AFE or Inverter mode simulation
            params["Datasheet"] = pset["Datasheet"]
            params["V_DC"] = float(pset["V_DC"])
            params["f_s"] = float(pset["f_s"])
            params["T_HS"] = int(pset["T_HS"])
            params["f_out"] = int(pset["f_out"])
            if self.afeMode:
                params["Mains_S"] = float(pset["Mains_S"])
                params["Mains_phi"] = float(pset["Mains_phi"])
                out = AFE_Parameters(params["V_DC"], U_Mains_LL, params["f_out"], Filter_L, Filter_C, params["Mains_S"], params["Mains_phi"],R_Fe_Transformer,R_S_Transformer,L_par , 1)
                out['U_Mains_LL'] = U_Mains_LL
                out["phi_degree_inv"] = 180+out["phi_degree_inv"]
            else:
                params["Load_S"] = float(pset["Load_S"])
                params["Load_phi"] = float(pset["Load_phi"])
                out = GISMSParameters_phi(params["V_DC"], U_Load_LL, params["f_out"], Filter_L, Filter_C, params["Load_S"], params["Load_phi"],R_Fe_Transformer,R_S_Transformer,L_par , 1)
                out['U_Load_LL'] = U_Load_LL
            
            
            # Setting up simulation parameters
            # Getting the IGBT, diode, loss table names
            thermalTransData = {}
            thermalRevDiodeData = {}
            thermalFWDiodeData = {}
            Rt_jc = {}
            Rt_cs = {}
            Cth_ig = {}
            Rev_jc = {}
            Rev_cs = {}
            Cth_rev = {}
            Rfw_jc = {}
            Rfw_cs = {}
            Cth_fwd = {}
            df = pd.read_csv(self.thermal_file_path,index_col =['Datasheet'])
            igbtDatasheets,diodeDatasheets,clampDatasheets = self.getComponentSCLs(params["Datasheet"])
            for sheet in igbtDatasheets:
                thermalTransData[sheet] = df.loc[df.index == igbtDatasheets[sheet]].to_dict(orient = 'records')[0]
            for sheet in diodeDatasheets:
                thermalRevDiodeData[sheet] = df.loc[df.index ==diodeDatasheets[sheet]].to_dict(orient = 'records')[0]
            for sheet in clampDatasheets:
                thermalFWDiodeData[sheet] = df.loc[df.index ==clampDatasheets[sheet]].to_dict(orient = 'records')[0]
            for sheet in igbtDatasheets:
                Rt_jc[sheet] = thermalTransData[sheet]['Rjc']
                Rt_cs[sheet] = thermalTransData[sheet]['Rcs']
                Cth_ig[sheet] = thermalTransData[sheet]['Cth']
            for sheet in diodeDatasheets:
                Rev_jc[sheet] = thermalRevDiodeData[sheet]['Rjc']
                Rev_cs[sheet] = thermalRevDiodeData[sheet]['Rcs']
                Cth_rev[sheet] = thermalRevDiodeData[sheet]['Cth']
            for sheet in clampDatasheets:
                Rfw_jc[sheet] = thermalFWDiodeData[sheet]['Rjc']
                Rfw_cs[sheet] = thermalFWDiodeData[sheet]['Rcs']
                Cth_fwd[sheet] = thermalFWDiodeData[sheet]['Cth']
            
            # Setting up the IGBT, diode, loss models names
            for leg in range(3):
                for igI,igSheet,dSheet in zip(list(range(len(igbtDatasheets))),list(igbtDatasheets.keys()),list(diodeDatasheets.keys())):
                    ginst.doOperation(JString("IGBT."+ str((igI+1)+4*leg)),JString("setLossFile"),JString(lossfilepath+"\\"+ igbtDatasheets[igSheet]+".scl"))
                    ginst.doOperation(JString("D."+str((igI+1)+4*leg)),JString("setLossFile"),JString(lossfilepath+"\\"+diodeDatasheets[dSheet]+".scl"))
                for fdI,cSheet in zip(list(range(len(clampDatasheets))),list(clampDatasheets)):
                    ginst.doOperation(JString("D."+str((fdI+13)+2*leg)),JString("setLossFile"),JString(lossfilepath+"\\"+clampDatasheets[cSheet]+".scl"))
            # Setting up the current sources and their phase informations
            for i in range (3):
                ginst.setParameter(JString("Iout."+ str(i+1)),"phase",out["phi_degree_inv"]+(i)*120)
            
            # Set the global parameters in the simulation file: These parameters must be
            # defined in Tools->Set Parameters in
            # the GUI.
            # This is how the simulation file can be adapted/scripted.
            # Setting the thermal network parameters
            for igI,igSheet,dSheet in zip(list(range(len(igbtDatasheets))),list(igbtDatasheets.keys()),list(diodeDatasheets.keys())):
                igI = igI+1
                parname = JString("$R_JC_"+str(igI))
                ginst.setGlobalParameterValue(parname,Rt_jc[igSheet])
                parname = JString("$R_CS_"+str(igI))
                ginst.setGlobalParameterValue(parname,Rt_cs[igSheet])
                parname = JString("$Cth_ig_"+str(igI))
                ginst.setGlobalParameterValue(parname,Cth_ig[igSheet])
                parname = JString("$Rev_JC_"+str(igI))
                ginst.setGlobalParameterValue(parname,Rev_jc[dSheet])
                parname = JString("$Rev_CS_"+str(igI))
                ginst.setGlobalParameterValue(parname,Rev_cs[dSheet])
                parname = JString("$Cth_rev_"+str(igI))
                ginst.setGlobalParameterValue(parname,Cth_rev[dSheet])
            for fdI,cSheet in zip(list(range(len(clampDatasheets))),list(clampDatasheets)):
                fdI = fdI+1
                parname = JString("$Rfw_JC_"+str(fdI))
                ginst.setGlobalParameterValue(parname,Rfw_jc[cSheet])
                parname = JString("$Rfw_CS_"+str(fdI))
                ginst.setGlobalParameterValue(parname,Rfw_cs[cSheet])
                parname = JString("$Cth_fwd_"+str(fdI))
                ginst.setGlobalParameterValue(parname,Cth_fwd[cSheet])
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
            self.gismsUpdate.emit(out)

            
            # If required to save this sweep file
            #ginst.saveFileAs(JString("D:\\thesis-research\\VS_code\\PythonGecko\\IPESFolder\\3NPC_sweep_"+pset['_pset_id']+".ipes"))
            ginst.set_dt(dt_step)  # Simulation time step
            ginst.set_Tend(t_end)  # Simulation time
            ginst.runSimulation()  # Run the simulation
         
            ##########------------------------------------------------------------------------#########
            ##########---------------------------------Loss Recordings------------------------#########
            ##########------------------------------------------------------------------------#########
            # Intialization
            meanLosses = {}
            meanTemp = {}
            t_end_new = ginst.get_Tend()
            t_start = t_end_new-20e-3
            saveLossData = {}
            saveTempData = {}
            totalLoss = 0
            meanLosses['TransformerLoss'] = out['P_Transformer'] #transformer losses
            for x in loss_keys:
                 losses = ginst.getSignalData(x,t_start,t_end_new,0)
                 lossesArray = np.array(losses)
                 if self.saveData :
                    saveLossData[x] = losses                
                 meanLosses[x] = np.mean(lossesArray)
                 totalLoss = totalLoss + meanLosses[x]
            
            meanLosses['InvTotalLoss'] = totalLoss*3  #total losses
            length = len(loss_keys)
            i=0
            while i < length:
                key = loss_keys[i+1]
                key = key[:-3] #remove _sw from key
                meanLosses[key] = meanLosses[loss_keys[i]] + meanLosses[loss_keys[i+1]]  #adding sw and con losses
                i+=2
            # Recording device temparatures of only one leg
            for x in temp_keys:
                 temp = ginst.getSignalData(x,t_start,t_end_new,0)
                 tempArray = np.array(temp)
                 if self.saveData :
                    saveTempData[x] = temp                
                 meanTemp[x] = np.mean(tempArray)
            time = ginst.getTimeArray('IG1_con',t_start,t_end_new,0); #get last cycle time stamp ???
            #ginst.disconnectFromGecko()
            # Set saveData to True if required to save the simulated loss data over the time range in CSV format
            if self.saveData:
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
            self.progressUpdate.emit(incrementor*count,'running')
            return {**meanLosses, **meanTemp}
        
        #Check if to start the simulation in AFE mode or Inverter mode
        
        if self.afeMode:
            df = ps.run(startSimNPC, paramsList, calc_dir='calc_AFE')
        else :
            df = ps.run(startSimNPC, paramsList)
        self.progressUpdate.emit(-1,'Done')
        ginst.shutdown()
        print(df)
                
            
        
            
    