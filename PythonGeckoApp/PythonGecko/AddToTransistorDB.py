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

topology = 'B6'
datasheet = 'FF300R06KE3'
transistor['T1']  = 'FF300R06KE3_T1T2'
transistor['T2']  = 'FF300R06KE3_T1T2'
transistor['T3']  = 'FF300R06KE3_T1T2'                #not required for B6 topology
transistor['T4']  = 'FF300R06KE3_T1T2'                #not required for B6 topology

bypassDiode['D1']  = 'FF300R06KE3_D1D2'
bypassDiode['D2']  = 'FF300R06KE3_D1D2'
bypassDiode['D3']  = 'FF300R06KE3_D1D2'            #not required for B6 topology
bypassDiode['D4']  = 'FF300R06KE3_D1D2'            #not required for B6 topology

#only required for NPC topology
clampingDiode['D5'] = 'F3L300R07PE4_RD'
clampingDiode['D6'] = 'F3L300R07PE4_RD'

if topology == 'TNPC':
    clampingDiode['D5'] = float('NaN')
    clampingDiode['D6'] = float('NaN')
if topology == 'B6':
    transistor['T3']  = float('NaN')                       
    transistor['T4']  = float('NaN')
    bypassDiode['D3']  = float('NaN')            #T1T2 and D1D2 info sufficient for B6 topology
    bypassDiode['D4']  = float('NaN') 
    clampingDiode['D5'] = float('NaN')
    clampingDiode['D6'] = float('NaN')

datasheetInfo = {**transistor , **bypassDiode, **clampingDiode}
datasheetInfo['Datasheet']=datasheet
datasheetInfo['Topology']=topology
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

