clc;clear all;close all;
%import package with functions for control of GeckoCIRCUITS
import('gecko.GeckoRemote.*');

%start the program
startGui();
connectToGecko();
openFile('D:\thesis-research\VS_code\GeckoCIRCUITS\3level_npc_therm.ipes');
lossfilepath = 'D:\thesis-research\VS_code\workspace';
%% Parameter input

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

%Load transistor loss curves
Transistor_array = {'F3L300R07PE4_T_new'};
RevDiode_array = {'F3L300R07PE4_RD_new'};
FWDiode_array = {'F3L300R07PE4_RD_new'};
IGBTlen = 12;
Dfwlen = 6;

%simulation time and step
dt = 100e-9;
tEnd = 400e-3;
R_jc = 0.16;
Rd_jc = 0.32;
Cth_ig = 0.2381;
Cth_d = 0.1233;
R_th = 0.063;
initSimulation(dt,tEnd);
%Types of losses recorded
IGBT_loss_keys = {'IG1_con','IG3_con','IG1_sw','IG3_sw','IG2_con','IG4_con','IG2_sw','IG4_sw'};
DREV_loss_keys = {'D1_con','D3_con','D1_sw','D3_sw','D2_con','D4_con','D2_sw','D4_sw'};
DFW_loss_keys = {'D13_con','D14_con','D13_sw','D14_sw'};

%% Run simulation
try
    for i_Transistor = 1:length(Transistor_array)
        for Ig_i = 1:IGBTlen
            doOperation(['IGBT.',num2str(Ig_i)],'setLossFile',[lossfilepath,'\',Transistor_array{(i_Transistor)},'.scl'])
            doOperation(['D.',num2str(Ig_i)],'setLossFile',[lossfilepath,'\',RevDiode_array{(i_Transistor)},'.scl'])
        end
        
        for Fd_i = 13:(12+Dfwlen)
            doOperation(['D.',num2str(Fd_i)],'setLossFile',[lossfilepath,'\',FWDiode_array{(i_Transistor)},'.scl'])
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
                                amount_sum_sim = length(Parameter_Sweep.V_DC) * length(Parameter_Sweep.Load_S) * length(Parameter_Sweep.Load_phi) * length(Parameter_Sweep.f_s) * length(Parameter_Sweep.T_HS) * length(Transistor_array);
                                amount_act_sim = i_V_DC * i_Load_S * i_Load_phi * i_f_s * i_T_HS * i_Transistor;
                                percent_sim_state = amount_act_sim / amount_sum_sim;
                                
                                disp(['Simulation ',num2str(amount_act_sim),' / ',num2str(amount_sum_sim),' : ',num2str(percent_sim_state*100), ' %']);
                                
                                
                                % Parameter precalculation for simulink simulation
                                precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s, i_T_HS, i_f_out) = GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out, Filter_L, Filter_C, Load_S, Load_phi_degree, 1);
                                m = precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s).m;
                                I_inv_peak = precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s).I_Peak_inv;
                                phi_inv_deg = precalcout(i_Transistor, i_V_DC, i_Load_S, i_Load_phi, i_f_s).phi_degree_inv;
                                %thermal network
                                setGlobalParameterValue('$R_JC',R_jc);
                                setGlobalParameterValue('$Rd_JC',Rd_jc);
                                setGlobalParameterValue('$R_CS',R_th);
                                setGlobalParameterValue('$Cth_ig',Cth_ig);
                                setGlobalParameterValue('$Cth_d',Cth_d);
                                
                                % Input parameters
                                setGlobalParameterValue('$fout',f_out);
                                setGlobalParameterValue('$fsw',f_s);
                                setGlobalParameterValue('$Udc',U_DC_inv/2);
                                setGlobalParameterValue('$m',m);
                                setGlobalParameterValue('$Ipeak_inv',I_inv_peak);
                                
                                setGlobalParameterValue('$uDC_t',T_HS);
                                setGlobalParameterValue('$uDC_rd',T_HS);
                                setGlobalParameterValue('$uDC_fd',T_HS);
                                for i = 1:3
                                    setParameter(['Iout.',num2str(i)],'phase',phi_inv_deg+(i-1)*120);
                                end
                                runSimulation();
                            end
                        end
                    end
                end
            end
        end
    end
    IGBT_losses = containers.Map;
    Drev_losses = containers.Map;
    FD_losses = containers.Map;
    end_time = get_Tend();
    start_time = end_time-20e-3;
    for ig=IGBT_loss_keys
        IGBT_losses(ig{1})=getSignalData(ig{1},start_time,end_time,0);
    end
    for rd=DREV_loss_keys
        Drev_losses(rd{1})=getSignalData(rd{1},start_time,end_time,0);
    end
    for fd=DFW_loss_keys
        FD_losses(fd{1})=getSignalData(fd{1},start_time,end_time,0);
    end
    time = getTimeArray('D13_con',0,tEnd,0);
    disconnectFromGecko();
    data2Box = [IGBT_losses;Drev_losses;FD_losses];
    wholeKeys = [IGBT_loss_keys DREV_loss_keys DFW_loss_keys];
    [modData] = read_script_gecko(data2Box,0,wholeKeys,time);
    
    for key=wholeKeys
        disp([key{1},' :', num2str(mean(modData(key{1})))]);
    end
catch Err
    % endSimulation();
    disconnectFromGecko();
    shutdown();
    rethrow(Err);
end

disconnectFromGecko()