
def GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out_inv, Filter_L, Filter_C, Load_S, Load_phi_degree, plotbit):
   #[out] = GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out_inv, Filter_L, Filter_C, Load_S, Load_phi_degree, plotbit)        
   #Input parameters:      
   # V_DC_inv       
   # V_LL_inv
   # f_out_inv
   # Filter_L (single phase element)
   # Filter_C (single phase element)
   # Load_S
   # Load_phi_degree (pos. = ind. Load, neg. = cap. load)
   # plotbit =1: output display enabled, =0: output display disabled

   #Output parameters:     
   #out.m 
   #out.phi_degree_inv 
   #out.cos_phi_inv 
   #out.I_Peak_inv 
   #out.Q_Filter_C 
   #out.Q_Filter_L 
   #out.S_inv 
   #out.P_inv 
   #out.Q_inv 
   #out.S_Load
   #out.P_Load 
   #out.Q_Load
    import cmath
    import math
    out = {
        "S_inv":0,
        "P_inv":0,
        "Q_inv":0,
        "S_Load":0,
        "P_Load":0,
        "Q_Load":0,
        "Q_Filter_C":0,
        "Q_Filter_L":0,
        "m":0,
        "phi_degree_inv":0,
        "cos_phi_inv":0,
        "I_Peak_inv":0,
        }     
    U_Load = U_Load_LL/math.sqrt(3)
    Load_phi_rad = math.radians(Load_phi_degree)
    Z_Filter_C = 1/complex(0,2*math.pi*f_out_inv*Filter_C)
    Z_Filter_L = complex(0,2*math.pi*f_out_inv*Filter_L)
    S_Load = complex(Load_S*math.cos(Load_phi_rad), -Load_S*math.sin(Load_phi_rad))/3 # divided by 3 due to 3 phase system
    Z_Load = U_Load*U_Load / S_Load
    I_Load = U_Load/Z_Load

    # Current in Filter Capacitor
    I_Filter_C = U_Load/Z_Filter_C

    # RL-Load including Filter Capacitor
    Y_RLC = 1/Z_Load + 1/Z_Filter_C
    Z_RLC = 1/Y_RLC

    # RL-Load + LC-Filter
    Z_Inverter = Z_RLC + Z_Filter_L

    # Voltage Filter L
    I_RLC = U_Load / Z_RLC
    U_Filter_L = Z_Filter_L * I_RLC

    # Input Voltage, given by inverter
    U_Inverter = U_Load + U_Filter_L

    # Display paramters
    #print("+-----------------------------+")
    #print("+       output values         +")
    #print("+-----------------------------+")
    I_RMS_Load = abs(I_Load)
    I_RMS_RLC = abs(I_RLC)
    I_Peak_RLC = math.sqrt(2) * abs(I_RLC)


    U_RMS_U_Load = abs(U_Load)
    U_RMS_U_Filter_L = abs(U_Filter_L)
    U_RMS_Inverter = abs(U_Inverter)


    #print("+--------- Voltage ----------+")
    U_Peak_Inverter = math.sqrt(2) * abs(U_Inverter)
    #print("+-------- Current RLC --------+")
    I_RMS_RLC = abs(I_RLC)
    I_Peak_RLC = math.sqrt(2) * abs(I_RLC)
    #print("+-------- Current C ----------+")
    I_RMS_Filter_C = abs(I_Filter_C)

    #print("+----------- Misc ------------+")
    phi_rad_Inverter = cmath.phase(U_Inverter) - cmath.phase(I_RLC)
    out["phi_degree_inv"] = math.degrees(phi_rad_Inverter)
    out["cos_phi_inv"]= math.cos(phi_rad_Inverter)
    out["m"] = math.sqrt(2) * U_RMS_Inverter / (U_DC_inv / 2)
    out["I_Peak_inv"] = I_Peak_RLC
    

    #print("+-----------------------------+")
    #print("+  output for double check    +")
    #print("+-----------------------------+")
    #print("+----- Power (3 Phase) -------+")
    out["S_inv"] = 3* abs(I_RMS_RLC * U_RMS_Inverter)
    out["P_inv"] = 3* abs(I_RMS_RLC * U_RMS_Inverter) * math.cos(phi_rad_Inverter)
    out["Q_inv"] = 3* abs(I_RMS_RLC * U_RMS_Inverter) * math.sin(phi_rad_Inverter)

    out["S_Load"] = 3* abs(U_Load*U_Load/Z_Load)
    out["P_Load"] = 3* abs(U_Load*U_Load/Z_Load) * math.cos(Load_phi_rad)
    out["Q_Load"] = 3* abs(U_Load*U_Load/Z_Load) * math.sin(Load_phi_rad)

    out["Q_Filter_C"] = 3 * abs(U_Load * U_Load/Z_Filter_C)
    out["Q_Filter_L"] = 3 * abs(U_Filter_L * I_RLC)
    #print("+-----------------------------+")
    #print("+  output if display bit is 1 +")
    #print("+-----------------------------+")
    out["I_RMS_Filter_C"] = I_RMS_Filter_C
    out["U_RMS_U_Load"] = U_RMS_U_Load
    out["Z_Load"] = Z_Load
    out["U_RMS_U_Filter_L"] = U_RMS_U_Filter_L
    if plotbit == 1 :
        print("RMS Load Voltage     : ", str(U_RMS_U_Load))
        print("RMS Filter-L Voltage : ", str(U_RMS_U_Filter_L))
        print("RMS Inverter Voltage : ", str(U_RMS_Inverter))
        print("RMS Inverter peakVtge: ", str(U_Peak_Inverter))
        print("RMS RLC current      : ", str(I_RMS_RLC))
        print("RMS RLC peak current : ", str(I_Peak_RLC))
        print("RMS Filter-C current : ", str(I_RMS_Filter_C))
        print("Inverter DC output   : ", str(U_DC_inv))
        print("Load Impedance       : ", str(Z_Load))
  
    return out