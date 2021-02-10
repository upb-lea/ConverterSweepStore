def AFE_Parameters(U_DC_inv, U_mains_LL, f, Filter_L, Filter_C, Mains_P, Mains_phi_degree, Kt_Transformer, R_Fe_Transformer, R_S_Transformer, L_par, plotbit):
    """
     * Initial author: N. Foerster      
     * Date of creation: xx.xx.2020     
     * Last modified by: N. Foerster
     * Date of modification: 21.12.2020             
     * Version: 1.1.2
     * Compatibility: Matlab / GNU Octave       
     * Other files required: Parallel_Serial_Impedance      
     * Link to function:        
     Syntax:         
     [out] = AFE_Parameters(U_DC_inv, U_mains_LL, f, Filter_L, Filter_C, Mains_P, Mains_phi_degree, Kt_Transformer, R_Fe_Transformer, R_S_Transformer, L_par, plotbit)
       
     Description:      
     Calculates the filter and transformer values when using an active front ent (AFE) for supply the dc link instead of a B6 diode bridge       
     Note: All values in the function are RMS values, Calculation in single phase equivalent circuit      
     This function calculates a Z_inv to set phi_mains = 0 degree.

     Input parameters:      
      * U_DC_inv
      * U_mains_LL
      * f
      * Filter_L
      * Filter_C
      * Mains_P
      * Mains_phi_degree
      * Kt_Transformer
      * R_Fe_Transformer
      * R_S_Transformer
      * L_par
      * plotbit
         
     Output parameters:     
      *  R_inv_par
      *  L_inv_par
      *  C_inv_par
      *  delta_phi_rad_inv
      *  delta_phi_degree_inv 
      *  cos_phi_inv 
      *  m 
      *  I_Peak_inv 
      *  V_DC 
      *  S_inv_compl 
      *  S_inv 
      *  P_inv 
      *  Q_inv 
      *  S_Mains_compl 
      *  S_Mains 
      *  P_Mains 
      *  Q_Mains 
      *  P_S_Transformer 
      *  P_mag_Transformer 
      *  P_Transformer 
         
     Example:         
        
       
     Known Bugs:      
     Note: Inductive / capacitive mode working, but not checked due to sign     
      
     Changelog:      
     VERSION / DATE / NAME: Comment     
     1.0.0 / xx.xx.2020 / N. Foerster: Inital version
     1.1.0 / 18.12.2020 / N. Foerster: add transformer losses, fix some power problem
     1.1.1 / 19.12.2020 / N. Foerster: rename P_xx_Transformer due to
     1.1.2 / 21.12.2020 / N. Foerster: fix Transformer losses to real (no imag)

     compatibility to GISMSParameters
    
        ---Filter_L---R_S-----+----------+------+------+
                              |          |      |      |
                              Filter_C   R_Fe   L_par  Z_inv
                              |          |      |      |
        ----------------------+----------+------+------+
     All values are RMS-values
     Calculation in single phase equivalent circuit
    """
    out = {}
    import math
    import cmath
    import numpy as np
    ## Calculation
    P_LN = Mains_P / 3 
    U_mains_LN = U_mains_LL/math.sqrt(3) 
        
    # Note: the negative sign helps to calculate from delta_phi to
    # current's phi
    phi_mains_rad = Mains_phi_degree * 2 * math.pi / 360 
    
    # Input filter
    Z_Filter_C = 1/complex(0,2*math.pi*f*Filter_C) 
    Z_Filter_L = complex(0,2*math.pi*f*Filter_L)
 
    # Calculate complex mains current
    I_mains_P_RMS = P_LN/U_mains_LN 
    I_mains_Q_RMS = I_mains_P_RMS * math.tan(phi_mains_rad) 
    I_mains = complex(I_mains_P_RMS, I_mains_Q_RMS)
    
    U_Filter_L = Z_Filter_L * I_mains 
    U_R_S_Transformer = R_S_Transformer * I_mains 
    
    U_inv = U_mains_LN - U_Filter_L - U_R_S_Transformer 
    U_RMS_Inv = abs(U_inv)
    I_Filter_C = U_inv / Z_Filter_C 
    I_R_Fe_Transformer = U_inv / R_Fe_Transformer 
    I_L_par = U_inv / complex(0,2*math.pi*f*L_par) 
    
    I_inv = I_mains - I_Filter_C - I_R_Fe_Transformer - I_L_par 
    
    Z_inv = U_inv / I_inv 
    
    #[R_ser L_ser C_ser R_par L_par C_par] = Parallel_Serial_Impedance(Z_inv, f, 0) 

    # output parameters, depending on kind of Z_inv
    out["R_inv_par"] = R_par 
    if imag(Z_inv) > 0 :
         L_inv_par = L_par 
         C_inv_par = NaN 
    elif imag(Z_inv) < 0:
         L_inv_par = NaN 
         C_inv_par = C_par       
    else :
         L_inv_par = NaN 
         C_inv_par = NaN             
    
    
    delta_phi_rad_inv = cmath.phase(U_inv) - cmath.phase(I_inv) 
    delta_phi_degree_inv = math.degrees(delta_phi_rad_inv)
    

    # Calculating the AFE's modulation degree for simulink simulation
    m = math.sqrt(2) * abs(U_inv) * 2 / U_DC_inv 
    I_RMS_Inv = abs(I_inv)
    # output peak current for inverter for simulink simulation
    I_Peak_inv = math.sqrt(2) * abs(I_inv) 
    
    # For simulink simulation
    out["V_DC"] = U_DC_inv 
    out["m"] = m
    out["phi_degree_inv"] = delta_phi_degree_inv
    out["cos_phi_inv"] = math.cos(delta_phi_degree_inv) 
    out["I_Peak_inv"] = I_Peak_inv
    # inverter power
    S_inv_compl = 3 * U_inv * I_inv.conjugate()
    S_inv = abs(S_inv_compl) 
    P_inv = S_inv_compl.real
    Q_inv = S_inv_compl.imag
    
    # Mains power
    S_Mains_compl = 3 * U_mains_LN * I_mains.conjugate()
    S_Mains = abs(S_Mains_compl) 
    P_Mains = S_Mains_compl.real
    Q_Mains = S_Mains_compl.imag
    
    # Transformer power
    P_S_Transformer = 3 * R_S_Transformer * I_mains * I_mains.conjugate() 
    P_mag_Transformer = 3 * R_Fe_Transformer * I_R_Fe_Transformer * I_R_Fe_Transformer.conjugate()
    P_Transformer =  P_S_Transformer.real +  P_mag_Transformer.real 

    out["S_inv"] = S_inv
    out["P_inv"] = P_inv
    out["Q_inv"] = Q_inv
    out["P_Transformer"] = P_Transformer
    out["S_Mains"] = S_Mains
    out["P_Mains"] = P_Mains
    out["Q_Mains"] = Q_Mains
    if plotbit == 1:
        print(f"P_Transformer = {round(P_Transformer)} W")
        print(f"P_Mains = {round(P_Mains)} W")
        print(f"Modulation degree m = {round(m, 2)}")
        print(f"I_RMS_Inv = {round(I_RMS_Inv,2)} A")
        print(f"U_RMS_inv = {round(U_RMS_Inv,2)} V")
        print(f"U_RMS_LL_inv = {round(U_RMS_Inv*math.sqrt(3), 2)} V")
        print(f"delta_phi_degree_inv = {round(delta_phi_degree_inv)}°")
        print(f"cos(phi)_inv = {round(math.cos(delta_phi_rad_inv),2)}")

    return out