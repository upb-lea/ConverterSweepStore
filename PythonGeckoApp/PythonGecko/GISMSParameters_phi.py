
def GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out_inv, Filter_L, Filter_C, Load_S, Load_phi_degree, Transformer_Rfe, Transformer_Rs,
                                    l_par, plotbit):
    """
    author: Nikolas Foerster
     * Date of creation: xx.xx.2020
     * Last modified by: Nikolas Foerster
     * Date of modification: 30.12.2020
     * Version: 2.0.0
     * Compatibility: Python
     * Other files required: No
     * Link to function:
    Syntax:
    [out] = ups_calculations.py(u_DC_inv, u_Load_LL, f_out_inv, filter_L, filter_C, load_S, load_phi_degree,
                                              Kt_Transformer, r_Fe_Transformer, r_S_Transformer, L_par, plotbit)

    Description:
    Calculates inverter output current, phi and modulation degree, depending on the input parameters. Function is internally
    calculating with complex RMS values in star equivalent circuit. For transformer, use the values R_Fe, L_par, R_S, filter_L

    ---+------+--------R_S - ----filter_L - --+--------------+
       |      |                               |              |
       R_Fe   L_par                           filter_C       z_load
       |      |                               |              |
    ---+------+-------------------------------+--------------+

    Input parameters:
     * V_DC_inv
     * V_LL_inv
     * f_out_inv
     * filter_L(single phase element)
     * filter_C(single phase element)
     * load_S
     * load_phi_degree(pos. = ind.Load, neg. = cap.load)
     * r_Fe_Transformer Transfomer iron resistance(star equivalent circuit)
     * r_S_Transformer Transfomer series resistance(star equivalent circuit)
     * L_par Transformer parallel inductance
     * plotbit = 1: output display enabled, = 0: output display disabled

    Output parameters:
      * u_inverter
      * i_inverter
      * phi_rad_inverter
      * phi_degree_inv
      * i_rms_inv
      * i_peak_inv
      * u_rms_inv
      * m
      * s_inv_compl
      * s_inv
      * p_inv
      * q_inv
      * p_mag_transformer
      * p_s_transformer
      * p_transformer
      * s_load_compl
      * s_load
      * p_load
      * q_load
      * Z_load
      * q_filter_c
      * q_filter_l
    Example:

    Known Bugs:

    Changelog:
    VERSION / DATE / NAME: Comment
      * 1.0.0 / xx.xx.2020 / N.Foerster: Initial Version
      * 1.0.x / xx.xx.2020 / N.Foerster: various changes
      * 1.1.0 / 17.11.2020 / N.Foerster: fix problem with capacitive laods
      * 1.1.1 / 19.11.2020 / N.Foerster: Add Plotbit as input parameter
      * 1.1.2 / 11.12.2020 / N.Foerster: Add u_rms_inv and complex diagrams
      * 1.2.0 / 16.12.2020 / N.Foerster: Add transformer losses
      * 1.2.1 / 17.12.2020 / N.Foerster: Add i_peak_inv
      * 2.0.0 / 30.12.2020 / N.Foerster: Rewrite function in python, remove kt_transformer (unused)
    """
    import cmath
    import math
    import numpy as np
    out = {}     
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
    U_Transformer_RS =  Transformer_Rs * I_RLC
    # Input Voltage, given by inverter
    U_Inverter = U_Load + U_Filter_L + U_Transformer_RS
    I_Transformer_Rfe = U_Inverter / Transformer_Rfe
    I_Transformer_l_par = U_Inverter / complex(0,2 * math.pi * f_out_inv * l_par)

    I_Inverter = I_RLC + I_Transformer_Rfe + I_Transformer_l_par
    # Display paramters
    #print("+-----------------------------+")
    #print("+       output values         +")
    #print("+-----------------------------+")
    phi_rad_Inverter = cmath.phase(U_Inverter) - cmath.phase(I_Inverter)
    phi_degree_inv = math.degrees(phi_rad_Inverter)
    U_RMS_Inverter = abs(U_Inverter)
    I_RMS_Inv = abs(I_Inverter)
    I_Peak_Inv = math.sqrt(2) * abs(I_Inverter)
    
    
    m = math.sqrt(2) * abs(U_Inverter) / (U_DC_inv / 2)
    out["m"] = m
    out["phi_degree_inv"] = phi_degree_inv
    out["I_Peak_inv"] = I_Peak_Inv
    out["cos_phi_inv"] = math.cos(phi_rad_Inverter)

    S_Inv_Compl = 3 * U_Inverter * I_Inverter.conjugate()
    S_Inv = abs(S_Inv_Compl)
    P_Inv = S_Inv_Compl.real
    Q_Inv = S_Inv_Compl.imag

    # Transformer output
    # Calculating open circuit power losses(Leerlauf - Verluste)
    P_Mag_Transformer = 3 * abs(U_Inverter) ** 2 / Transformer_Rfe

    # Calculating series resistance losses
    # Note: Series impedance is responsable for losses.Due to series
    # connection, the apparent power ( and the apparent current) contributes
    # to the losses, not the active power.
    P_S_Transformer = 3 * Transformer_Rs * abs(I_RLC) ** 2

    # Calculating total transformer losses
    P_Transformer = P_Mag_Transformer + P_S_Transformer

    # Load output
    S_Load_Compl = 3 * U_Load * I_Load.conjugate()
    S_Load = abs(S_Load_Compl)
    P_Load = S_Load_Compl.real
    Q_Load = S_Load_Compl.imag


  
    #print("+-----------------------------+")
    #print("+  output for double check    +")
    #print("+-----------------------------+")
    #print("+----- Power (3 Phase) -------+")
    out["S_inv"] = S_Inv
    out["P_inv"] = P_Inv
    out["Q_inv"] = Q_Inv
    out["P_Transformer"] = P_Transformer
    out["S_Load"] = S_Load
    out["P_Load"] = P_Load
    out["Q_Load"] = Q_Load

    out["Q_Filter_C"] = 3 * abs(U_Load * U_Load / Z_Filter_C)
    out["Q_Filter_L"] = 3 * abs(U_Filter_L * I_RLC)
    
    out["Z_Load"] = Z_Load
    out["U_RMS_inv"] = U_RMS_Inverter
    out["I_Filter_C"] = abs(I_Filter_C)
    out["U_Filter_L"] = abs(U_Filter_L)
    #print("+-----------------------------+")
    #print("+  output if display bit is 1 +")
    #print("+-----------------------------+")
    if plotbit == 1:
        print(f"P_Transformer = {round(P_Transformer)} W")
        print(f"P_Inv = {round(P_Inv)} W")
        print(f"Modulation degree m = {round(m, 2)}")
        print(f"I_RMS_inv = {round(I_RMS_Inv,2)} A")
        print(f"U_RMS_inv = {round(U_RMS_Inverter,2)} V")
        print(f"U_RMS_LL_inv = {round(U_RMS_Inverter*math.sqrt(3), 2)} V")
        print(f"phi_degree_inv = {round(phi_degree_inv)}°")
        print(f"cos(phi)_inv = {round(math.cos(phi_rad_Inverter),2)}")

    return out