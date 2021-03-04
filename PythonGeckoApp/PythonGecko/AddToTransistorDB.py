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

topology = 'NPC'
datasheet = 'F3L300R07PE4'
transistor['T1']  = 'F3L300R07PE4_T'
transistor['T2']  = 'F3L300R07PE4_T'
transistor['T3']  = 'F3L300R07PE4_T'                #not required for B6 topology
transistor['T4']  = 'F3L300R07PE4_T'                #not required for B6 topology

bypassDiode['D1']  = 'F3L300R07PE4_RD'
bypassDiode['D2']  = 'F3L300R07PE4_RD'
bypassDiode['D3']  = 'F3L300R07PE4_RD'            #not required for B6 topology
bypassDiode['D4']  = 'F3L300R07PE4_RD'            #not required for B6 topology

#only required for NPC topology
clampingDiode['D5'] = 'F3L300R07PE4_RD'
clampingDiode['D6'] = 'F3L300R07PE4_RD'

if topology == 'TNPC':
    clampingDiode['D5'] = float('NaN')
    clampingDiode['D6'] = float('NaN')
if topology == 'B6':
    transistor['T3']  = float('NaN')                       
    transistor['T4']  = float('NaN')
datasheetInfo = {**transistor , **bypassDiode, **clampingDiode}
datasheetInfo['Datasheet']=datasheet
datasheetInfo['Topology']=topology
if os.path.exists(transistor_db_path):
    df = pd.read_csv(transistor_db_path)
    valueCounts = df[(df['Topology'] == topology) & (df['Datasheet'] == datasheet)]
    if len(valueCounts):
        print("Datasheet exists in database for the selected topology")
        print(df)
    else :
        newdb= pd.DataFrame([datasheetInfo]) 
        newdb.to_csv(transistor_db_path,mode='a', index = False, header=False)
else :
    newdb = pd.DataFrame([datasheetInfo]) 
    newdb.to_csv(transistor_db_path, index=False)

