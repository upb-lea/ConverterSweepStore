import pandas as pd
import os
#NPC topology requires T1,T2,T3,T4, D1,D2,D3,D4,D5,D6 characterisctics 
#and energy loss look up tables in scl format.

#TNPC topology requires T1,T2,T3,T4, D1,D2,D3,D4
#characterisctics and energy loss look up tables in scl format.
#D5 and D6 should be assigned with NaN while writing to database.

#B6 topology requires T1,T2, D1,D2 characterisctics and energy loss look up tables in scl format
#rest will be replaced with NaN while writing to database
transistor_db_path = r'calc\Thermal\DatasheetDB.csv'
datasheetInfo = {}
transistor = {}
bypassDiode = {}
clampingDiode = {}
isvalid = False

topology = 'FC-ANPC'
datasheet = '2MBI200XAA065-50'
circuitLevel = 'single-switch'    #Full-Level or single-switch
manufacturer = 'Fuji'

if topology == 'B6':
    transistor['T1']  = 'Fuji_2MBI400XBE065-50_T'
    transistor['T2']  = 'Fuji_2MBI400XBE065-50_T'
    bypassDiode['D1']  = 'Fuji_2MBI400XBE065-50_RD'
    bypassDiode['D2']  = 'Fuji_2MBI400XBE065-50_RD'
if topology == 'NPC':
    transistor['T1']  = 'SEMiX405MLI07E4_T1T4'
    transistor['T2']  = 'SEMiX405MLI07E4_T2T3'
    transistor['T3']  = 'SEMiX405MLI07E4_T2T3'                
    transistor['T4']  = 'SEMiX405MLI07E4_T1T4' 
    bypassDiode['D1']  = 'SEMiX405MLI07E4_D1D4'
    bypassDiode['D2']  = 'SEMiX405MLI07E4_D2D3'
    bypassDiode['D3']  = 'SEMiX405MLI07E4_D2D3'            
    bypassDiode['D4']  = 'SEMiX405MLI07E4_D1D4'            
    clampingDiode['D5'] = 'SEMiX405MLI07E4_D5D6'                 #not required for B6 topology
    clampingDiode['D6'] = 'SEMiX405MLI07E4_D5D6'                 #not required for B6 topology
if topology == 'TNPC':
    #outerswitches
    transistor['T1']  = 'SEMiX405TMLI12E4B_T1T4'                  
    transistor['T4']  = 'SEMiX405TMLI12E4B_T1T4'
    bypassDiode['D1']  = 'SEMiX405TMLI12E4B_D1D4'
    bypassDiode['D4']  = 'SEMiX405TMLI12E4B_D1D4'
    #inner switches
    transistor['T2']  = 'SEMiX405TMLI12E4B_T2T3'
    transistor['T3']  = 'SEMiX405TMLI12E4B_T2T3'                 
    bypassDiode['D2']  = 'SEMiX405TMLI12E4B_D2D3'            
    bypassDiode['D3']  = 'SEMiX405TMLI12E4B_D2D3'
if topology == 'FC-ANPC':
    #only required for FC-ANPC topology
    #outer switches
    transistor['T1']  = '2MBI200XAA065-50_T'
    transistor['T2']  = '2MBI200XAA065-50_T'
    transistor['T3']  = '2MBI200XAA065-50_T'                
    transistor['T4']  = '2MBI200XAA065-50_T'
    bypassDiode['D1']  = '2MBI200XAA065-50_RD'
    bypassDiode['D2']  = '2MBI200XAA065-50_RD'                    
    bypassDiode['D3']  = '2MBI200XAA065-50_RD'            
    bypassDiode['D4']  = '2MBI200XAA065-50_RD'  
    #inner switches
    transistor['T5']  = '2MBI200XAA065-50_T'
    transistor['T6']  = '2MBI200XAA065-50_T'
    transistor['T7']  = '2MBI200XAA065-50_T'                
    transistor['T8']  = '2MBI200XAA065-50_T'
    bypassDiode['D5']  = '2MBI200XAA065-50_RD'
    bypassDiode['D6']  = '2MBI200XAA065-50_RD'                    
    bypassDiode['D7']  = '2MBI200XAA065-50_RD'            
    bypassDiode['D8']  = '2MBI200XAA065-50_RD'            
    

datasheetInfo = {**transistor , **bypassDiode, **clampingDiode}
datasheetInfo['Datasheet']=datasheet
datasheetInfo['Topology']=topology
datasheetInfo['Circuit-Level'] =circuitLevel
datasheetInfo['Manufacturer'] =manufacturer
if os.path.exists(transistor_db_path):
    df = pd.read_csv(transistor_db_path)
    indx = df.index[(df['Topology'] == topology) & (df['Datasheet'] == datasheet)].tolist()
    if len(indx)==1:
        print("Datasheet exists in database for the selected topology")
        val = input("Do you want to Overwrite ? y/n :")
        if val =='y' or val=='Y':
            df.drop(indx,inplace=True)
            df = df.append(datasheetInfo, ignore_index=True)
            df.to_csv(transistor_db_path,index=False)
        elif val=='n' or val=='N':
            print('Terminating...')
        else :
            print('Invalid input! Terminating...')
    elif len(indx)>1:
        print("Invalid Database!!")
    else :
        newdb= pd.DataFrame([datasheetInfo]) 
        newdb.to_csv(transistor_db_path,mode='a', index = False, header=False)
        print(newdb)
else :
    newdb = pd.DataFrame([datasheetInfo]) 
    newdb.to_csv(transistor_db_path, index=False)
    print(newdb)

