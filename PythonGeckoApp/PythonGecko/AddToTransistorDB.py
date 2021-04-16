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
datasheet = 'F3L300R07PE4'
circuitLevel = 'single-switch'

if topology == 'B6':
    transistor['T1']  = 'FF300R06KE3_T1T2'
    transistor['T2']  = 'FF300R06KE3_T1T2'
    bypassDiode['D1']  = 'FF300R06KE3_D1D2'
    bypassDiode['D2']  = 'FF300R06KE3_D1D2'
if topology == 'NPC':
    transistor['T1']  = 'FF300R06KE3_T1T2'
    transistor['T2']  = 'FF300R06KE3_T1T2'
    transistor['T3']  = 'FF300R06KE3_T1T2'                
    transistor['T4']  = 'FF300R06KE3_T1T2' 
    bypassDiode['D1']  = 'FF300R06KE3_D1D2'
    bypassDiode['D2']  = 'FF300R06KE3_D1D2'
    bypassDiode['D3']  = 'FF300R06KE3_D1D2'            
    bypassDiode['D4']  = 'FF300R06KE3_D1D2'            
    clampingDiode['D5'] = 'F3L300R07PE4_RD'                 #not required for B6 topology
    clampingDiode['D6'] = 'F3L300R07PE4_RD'                 #not required for B6 topology
if topology == 'TNPC':
    #outerswitches
    transistor['T1']  = 'FF300R06KE3_T1T2'                  
    transistor['T4']  = 'FF300R06KE3_T1T2'
    bypassDiode['D1']  = 'FF300R06KE3_D1D2'
    bypassDiode['D2']  = 'FF300R06KE3_D1D2'
    #inner switches
    transistor['T2']  = 'FF300R06KE3_T1T2'
    transistor['T3']  = 'FF300R06KE3_T1T2'                 
    bypassDiode['D3']  = 'FF300R06KE3_D1D2'            
    bypassDiode['D4']  = 'FF300R06KE3_D1D2'
if topology == 'FC-ANPC':
    #only required for FC-ANPC topology
    #outer switches
    transistor['T1']  = 'F3L300R07PE4_T'
    transistor['T2']  = 'F3L300R07PE4_T'
    transistor['T3']  = 'F3L300R07PE4_T'                
    transistor['T4']  = 'F3L300R07PE4_T'
    bypassDiode['D1']  = 'F3L300R07PE4_RD'
    bypassDiode['D2']  = 'F3L300R07PE4_RD'                    
    bypassDiode['D3']  = 'F3L300R07PE4_RD'            
    bypassDiode['D4']  = 'F3L300R07PE4_RD'  
    #inner switches
    transistor['T5']  = 'F3L300R07PE4_T'
    transistor['T6']  = 'F3L300R07PE4_T'
    transistor['T7']  = 'F3L300R07PE4_T'                
    transistor['T8']  = 'F3L300R07PE4_T'
    bypassDiode['D5']  = 'F3L300R07PE4_RD'
    bypassDiode['D6']  = 'F3L300R07PE4_RD'                    
    bypassDiode['D7']  = 'F3L300R07PE4_RD'            
    bypassDiode['D8']  = 'F3L300R07PE4_RD'            
    

datasheetInfo = {**transistor , **bypassDiode, **clampingDiode}
datasheetInfo['Datasheet']=datasheet
datasheetInfo['Topology']=topology
datasheetInfo['Circuit-Level'] =circuitLevel
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

