function [out] = GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out_inv, Filter_L, Filter_C, Load_S, Load_phi_degree, plotbit)
% * Initial author: Nikolas Foerster       
% * Date of creation: xx.xx.2020     
% * Last modified by: Nikolas Foerster       
% * Date of modification: 17.11.2020      
% * Version: 1.1.0      
% * Compatibility: Matlab / GNU Octave       
% * Other files required: No      
% * Link to function:        
% Syntax:         
% [out] = GISMSParameters_phi(U_DC_inv, U_Load_LL, f_out_inv, Filter_L, Filter_C, Load_S, Load_phi_degree, plotbit)        
%       
% Description:      
% Calculates inverter output current, phi and modulation degree, depending on the input parameters       
%        
% Input parameters:      
%  * V_DC_inv       
%  * V_LL_inv
%  * f_out_inv
%  * Filter_L (single phase element)
%  * Filter_C (single phase element)
%  * Load_S
%  * Load_phi_degree (pos. = ind. Load, neg. = cap. load)
%  * plotbit =1: output display enabled, =0: output display disabled
%
% Output parameters:     
%  * out.m 
%  * out.phi_degree_inv 
%  * out.cos_phi_inv 
%  * out.I_Peak_inv 
%  * out.Q_Filter_C 
%  * out.Q_Filter_L 
%  * out.S_inv 
%  * out.P_inv 
%  * out.Q_inv 
%  * out.S_Load
%  * out.P_Load 
%  * out.Q_Load
%         
% Example:         
%        
%       
% Known Bugs:      
%      
%      
% Changelog:      
% VERSION / DATE / NAME: Comment     
% 1.0.0 / xx.xx.2020 / N. Foerster: Initial Version
% 1.0.x / xx.xx.2020 / N. Foerster: various changes
% 1.1.0 / 17.11.2020 / N. Foerster: fix problem with capacitive laods
% 1.1.1 / 19.11.2020 / N. Foerster: Add Plotbit as input parameter


    % All values are RMS-values
    % disp('+-------------------------------------------------+')
    % disp('+                Start of Simulation              +')
    % disp('+         Voltage/Current values in RMS           +')
    % disp(['+              ' datestr(now) '               +'])
    % disp('+-------------------------------------------------+')

    % disp('+-----------------------------+')
    % disp('+      Input parameters       +')
    % disp('+-----------------------------+')

    U_Load = U_Load_LL/sqrt(3);
    Load_phi_rad = Load_phi_degree*2*pi/360;
    
    %% Calculation
    % disp('+-----------------------------+')
    % disp('+    calculation values       +')
    % disp('+    Complex AC calculation   +')
    % disp('+  Note: single phase model   +')
    % disp('+-----------------------------+')
    % % Filter Impedances
    Z_Filter_C = 1/(i*2*pi*f_out_inv*Filter_C);
    Z_Filter_L = 2*pi*f_out_inv*Filter_L*i;
    
    S_Load = (Load_S*cos(Load_phi_rad) - i * Load_S*sin(Load_phi_rad))/3; % divided by 3 due to 3 phase system
    Z_Load = U_Load*U_Load / S_Load;
    I_Load = U_Load/Z_Load;

    % Current in Filter Capacitor
    I_Filter_C = U_Load/Z_Filter_C;

    % RL-Load including Filter Capacitor
    Y_RLC = 1/Z_Load + 1/Z_Filter_C;
    Z_RLC = 1/Y_RLC;

    % RL-Load + LC-Filter
    Z_Inverter = Z_RLC + Z_Filter_L;

    % Voltage Filter L
    I_RLC = U_Load / Z_RLC;
    U_Filter_L = Z_Filter_L * I_RLC;

    % Input Voltage, given by inverter
    U_Inverter = U_Load + U_Filter_L;

    %% Display paramters
    % disp('+-----------------------------+')
    % disp('+       output values         +')
    % disp('+-----------------------------+')
    I_RMS_Load = abs(I_Load);
    I_RMS_RLC = abs(I_RLC);
    I_Peak_RLC = sqrt(2) * abs(I_RLC);


    U_RMS_U_Load = abs(U_Load);
    U_RMS_U_Filter_L = abs(U_Filter_L);
    U_RMS_Inverter = abs(U_Inverter);


    % disp('+--------- Voltage ----------+')
    U_Peak_Inverter = sqrt(2) * abs(U_Inverter);
    % disp('+-------- Current RLC --------+')
    I_RMS_RLC = abs(I_RLC);
    I_Peak_RLC = sqrt(2) * abs(I_RLC);
    % disp('+-------- Current C ----------+')
    I_RMS_Filter_C = abs(I_Filter_C);

    % disp('+----------- Misc ------------+')
    phi_rad_Inverter = angle(U_Inverter) - angle(I_RLC);
    out.phi_degree_inv = phi_rad_Inverter * 360 / 2 / pi;
    out.cos_phi_inv = cos(phi_rad_Inverter);
    out.m = sqrt(2) * U_RMS_Inverter / (U_DC_inv / 2);

    % disp('+-----------------------------+')
    % disp('+  output for double check    +')
    % disp('+-----------------------------+')
    % disp('+----- Power (3 Phase) -------+')
    out.S_inv = 3* abs(I_RMS_RLC * U_RMS_Inverter);
    out.P_inv = 3* abs(I_RMS_RLC * U_RMS_Inverter) * cos(phi_rad_Inverter);
    out.Q_inv = 3* abs(I_RMS_RLC * U_RMS_Inverter) * sin(phi_rad_Inverter);

    out.S_Load = 3* abs(U_Load*U_Load/Z_Load);
    out.P_Load = 3* abs(U_Load*U_Load/Z_Load) * cos(Load_phi_rad);
    out.Q_Load = 3* abs(U_Load*U_Load/Z_Load) * sin(Load_phi_rad);

    out.Q_Filter_C = 3 * abs(U_Load * U_Load/Z_Filter_C);
    out.Q_Filter_L = 3 * abs(U_Filter_L * I_RLC);
    % disp('+-----------------------------+')
    % disp('+  output for Simulink        +')
    % disp('+-----------------------------+')
    U_DC_inv;
    out.m;
    out.phi_degree_inv;
    out.cos_phi_inv;
    out.I_Peak_inv = I_Peak_RLC;
    U_RMS_Inverter;
    
    if plotbit == 1
      U_RMS_U_Load
      U_RMS_U_Filter_L 
      U_RMS_Inverter 
      U_Peak_Inverter
      
      I_RMS_RLC 
      I_Peak_RLC
      I_RMS_Filter_C 
      
      out
      U_DC_inv
      
      Z_Load

    end
end