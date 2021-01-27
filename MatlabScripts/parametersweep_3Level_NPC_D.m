% Parameters for Step Simulation
Ts_Control = 5e-5;
Ts_Power = 5e-6;

%% Run startup script to import git functions
% startup;

%% Parameter input

% type of load
% load = 'filter': simulation with a filter between inverter and load
% load = 'motor': simulation with a motor in an operating point as load
       % Parameter input, these parameters will be calculated by script to inverter parameters
Filter_C = 3.516e-3;
Filter_L = 117.33e-6;
U_Load_LL = 115;

% Parameter input variable
Parameter_Sweep.V_DC = [216];
Parameter_Sweep.Load_S = [40000];
Parameter_Sweep.Load_phi = [32]; % pos = inductive load, neg = capacitive load. +/-36.87 degree is equivalent to cos(phi) = +/-0.8
Parameter_Sweep.f_s = [7200];
Parameter_Sweep.T_HS = [95];
Parameter_Sweep.f_out = [50];

T14_Transistor_array = [Infineon_F3L300R07PE4_T_RD]
T23_Transistor_array = [Infineon_F3L300R07PE4_T_RD]
C_Transistor_array = [Infineon_F3L300R07PE4_T_RD]
%% Run simulation

for i_Transistor = 1:length(T14_Transistor_array)
    T14_Transistor = T14_Transistor_array(i_Transistor);
     T23_Transistor =  T23_Transistor_array(i_Transistor);
     Clamping =  C_Transistor_array(i_Transistor);
    % Calculation of the simulation time for each transistor
     
    t14auS = T14_Transistor.Switch.R_th_total*T14_Transistor.Switch.C_th_total;
    t23auS = T23_Transistor.Switch.R_th_total*T23_Transistor.Switch.C_th_total;
    if(t14auS>t23auS)
        tau_switch = t14auS;
    else
        tau_switch =t23auS;
    end
    t14_diode = T14_Transistor.Diode.R_th_total*T14_Transistor.Diode.C_th_total;
    tC_diode =  Clamping.Diode.R_th_total*Clamping.Diode.C_th_total;
     if(t14_diode>tC_diode)
        tau_diode = t14_diode;
    else
        tau_diode =tC_diode;
     end  
    if tau_switch > tau_diode
        t_sim = 20*tau_switch;
    else
        t_sim = 20*tau_diode;
    end
    
    for i_V_DC = 1:length(Parameter_Sweep.V_DC)
        U_DC_inv = Parameter_Sweep.V_DC(i_V_DC);

        for i_Load_S = 1:length(Parameter_Sweep.Load_S)
            Load_S = Parameter_Sweep.Load_S(i_Load_S);

            for i_Load_phi = 1:length(Parameter_Sweep.Load_phi)
                Load_phi_degree = Parameter_Sweep.Load_phi(i_Load_phi);

                for i_f_s = 1:length(Parameter_Sweep.f_s)
                    f_s = Parameter_Sweep.f_s(i_f_s);
                    
                    for i_T_HS = 1:length(Parameter_Sweep.T_HS)
                        T_HS = Parameter_Sweep.T_HS(i_T_HS);
                        
                        for i_f_out = 1:length(Parameter_Sweep.f_out)
                            f_out = Parameter_Sweep.f_out(i_f_out);
                            
                            % Calculate amount of simulations
                            amount_sum_sim = length(Parameter_Sweep.V_DC) * length(Parameter_Sweep.Load_S) * length(Parameter_Sweep.Load_phi) * length(Parameter_Sweep.f_s) * length(Parameter_Sweep.T_HS) * length(T14_Transistor_array);
                            amount_act_sim = i_V_DC * i_Load_S * i_Load_phi * i_f_s * i_T_HS * i_Transistor;
                            percent_sim_state = amount_act_sim / amount_sum_sim;

                            disp(['Simulation ',num2str(amount_act_sim),' / ',num2str(amount_sum_sim),' : ',num2str(percent_sim_state*100), ' %']);

                           
                                    % Parameter precalculation for simulink simulation
                                    precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS, i_f_out) = GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out, Filter_L, Filter_C, Load_S, Load_phi_degree, 1);
                                     % Input parameters
                                    siminput.f_out = f_out;
                                    siminput.f_s = f_s;
                                    siminput.V_DC = U_DC_inv;
                                    siminput.T_HS = T_HS;
                            
                                    % Input parameters for simulink simulation from parameter
                                    % precalculation
                                    siminput.m = precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s).m;
                                    siminput.I_inv_peak = precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s).I_Peak_inv;
                                    siminput.phi_inv_deg = precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s).phi_degree_inv;
                                    
                         
                            clear out;
                            out = sim('Loss_Evaluation_3Level_NPC_D');

    %% Power Loss calculation   
    %% Leg/phase W loss investigator
    Evaluation_Period = 1/Parameter_Sweep.f_out(i_f_out);
    P_Switch_SW_WT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_WT1, Evaluation_Period);
    P_Switch_SW_WT4(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_WT4, Evaluation_Period);
    P_Switch_SW_WT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_WT3, Evaluation_Period);
    P_Switch_SW_WT2(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_WT2, Evaluation_Period);
    
    P_Switch_ON_WT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_On_WT1, Evaluation_Period);
    P_Switch_OFF_WT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Off_WT1, Evaluation_Period);
    
    
    P_Switch_Cond_WT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_WT1, Evaluation_Period);
    P_Switch_Cond_WT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_WT3, Evaluation_Period);
     P_Switch_Cond_WT4(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_WT4, Evaluation_Period);
    P_Switch_Cond_WT2(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_WT2, Evaluation_Period);

    P_Diode_SW_WD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_WD1, Evaluation_Period);
    P_Diode_SW_WD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_WD3, Evaluation_Period);
    P_Diode_SW_WDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_WC, Evaluation_Period);
    P_Diode_SW_WD4(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_WD4, Evaluation_Period);
    P_Diode_SW_WD2(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_WD2, Evaluation_Period);
    P_Diode_SW_WDC6(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_WC6, Evaluation_Period);

    P_Diode_Cond_WD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_WD1, Evaluation_Period);
    P_Diode_Cond_WD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_WD3, Evaluation_Period);
    P_Diode_Cond_WDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_WC, Evaluation_Period);
    P_Diode_Cond_WD4(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_WD4, Evaluation_Period);
    P_Diode_Cond_WD2(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_WD2, Evaluation_Period);
    P_Diode_Cond_WDC6(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_WC6, Evaluation_Period);

    T_J_W_T1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Wm1, Evaluation_Period);
    T_J_W_T3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Wm3, Evaluation_Period);
    T_J_W_T4(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Wm4, Evaluation_Period);
    T_J_W_DC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_WC, Evaluation_Period);
    T_J_W_D1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Wm1, Evaluation_Period);
    T_J_W_D3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Wm3, Evaluation_Period);
    T_J_W_D4(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Wm4, Evaluation_Period);
    
     T_C_W_m1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Wm1, Evaluation_Period);
     T_C_W_m3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Wm3, Evaluation_Period);
     T_C_W_m2(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Wm2, Evaluation_Period); 
     T_C_W_m5(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Wm5, Evaluation_Period); 

    %% Leg/phase V loss investigator 
     P_Switch_SW_VT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_VT1, Evaluation_Period);
    P_Switch_SW_VT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_VT3, Evaluation_Period);
    P_Switch_Cond_VT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_VT1, Evaluation_Period);
    P_Switch_Cond_VT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_VT3, Evaluation_Period);

    P_Diode_SW_VD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_VD1, Evaluation_Period);
    P_Diode_SW_VD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_VD3, Evaluation_Period);
    P_Diode_SW_VDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_VC, Evaluation_Period);

    P_Diode_Cond_VD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_VD1, Evaluation_Period);
    P_Diode_Cond_VD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_VD3, Evaluation_Period);
    P_Diode_Cond_VDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_VC, Evaluation_Period);

    T_J_V_T1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Vm1, Evaluation_Period);
    T_J_V_T3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Vm3, Evaluation_Period);
    T_J_V_D5(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_VC, Evaluation_Period);
    T_J_V_D1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Vm1, Evaluation_Period);
    T_J_V_D3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Vm3, Evaluation_Period);
    
     T_C_V_m1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Vm1, Evaluation_Period);
     T_C_V_m3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Vm3, Evaluation_Period);
     T_C_V_m5(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Vm5, Evaluation_Period); 
     
     %% Leg/phase U loss investigator 
     P_Switch_SW_UT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_UT1, Evaluation_Period);
    P_Switch_SW_UT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_SW_UT3, Evaluation_Period);
    P_Switch_Cond_UT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_UT1, Evaluation_Period);
    P_Switch_Cond_UT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.IGBT_Cond_UT3, Evaluation_Period);

    P_Diode_SW_UD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_UD1, Evaluation_Period);
    P_Diode_SW_UD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_UD3, Evaluation_Period);
    P_Diode_SW_UDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_SW_UC, Evaluation_Period);

    P_Diode_Cond_UD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_UD1, Evaluation_Period);
    P_Diode_Cond_UD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_UD3, Evaluation_Period);
    P_Diode_Cond_UDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.Diode_Cond_UC, Evaluation_Period);

    T_J_U_T1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Um1, Evaluation_Period);
    T_J_U_T3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Switch_Um3, Evaluation_Period);
    T_J_U_D5(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_UC, Evaluation_Period);
    T_J_U_D1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Um1, Evaluation_Period);
    T_J_U_D3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_J_Diode_Um3, Evaluation_Period);
    
     T_C_U_m1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Um1, Evaluation_Period);
     T_C_U_m3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Um3, Evaluation_Period);
     T_C_U_m5(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = iMEAN(out.T_C_Um5, Evaluation_Period); 
    
    %% post production calculations
    P_Switch_WT14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2*(P_Switch_SW_WT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+ P_Switch_Cond_WT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)); 
    P_Switch_VT14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2*(P_Switch_SW_VT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+ P_Switch_Cond_VT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)); 
    P_Switch_UT14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2*(P_Switch_SW_UT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+ P_Switch_Cond_UT1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)); 

    P_Switch_WT32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2*(P_Switch_SW_WT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+ P_Switch_Cond_WT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)); 
    P_Switch_VT32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2*(P_Switch_SW_VT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+ P_Switch_Cond_VT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)); 
    P_Switch_UT32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2*(P_Switch_SW_UT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+ P_Switch_Cond_UT3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)); 


    P_Diode_WD14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_WD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_WD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );
    P_Diode_VD14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_VD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_VD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );
    P_Diode_UD14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_UD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_UD1(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );

    P_Diode_WD32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_WD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_WD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );
    P_Diode_VD32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_VD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_VD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );
    P_Diode_UD32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_UD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_UD3(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );

    P_Diode_WDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_WDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_WDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );
    P_Diode_VDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_VDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_VDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );
    P_Diode_UDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = 2 *(P_Diode_SW_UDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) +P_Diode_Cond_UDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) );

    P_Switch(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = P_Switch_WT14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) + P_Switch_VT14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Switch_UT14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Switch_WT32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) + P_Switch_VT32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Switch_UT32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS);
    P_Diode(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = P_Diode_WD14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_VD14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_UD14(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_WD32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_VD32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_UD32(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_WDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_VDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS)+P_Diode_UDC(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS);

    P_inv(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = P_Switch(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) + P_Diode(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS);

    P_out(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = Parameter_Sweep.Load_S(i_Load_S) * cos(Parameter_Sweep.Load_phi(i_Load_phi)*2*pi/360);
    eta(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) = P_out(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) /(P_inv(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS) + P_out(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS));
                        end
                    end
                end
            end
        end
    end
end
