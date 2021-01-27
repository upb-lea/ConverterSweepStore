function [modBox] = read_script_gecko(boxData,plotData,plotBox,t)
repCount = containers.Map;
modBox = containers.Map;
for k = keys(boxData)
    len = length(boxData(k{1}));
    pieceData = boxData(k{1});
    count = 0;
    for i = 1:len
        if(isnan(pieceData(i)))
            pieceData(i) = 0;
            count= count+1;
        end
    end
    modBox(k{1}) = pieceData;
    repCount(k{1}) = count;
end
if plotData
    for i = 1: (length(plotBox)/4)
        figure('Name',['loss plots_',num2str(i)])
        for k = 1 : 2
            subplot(2,1,k);
            count = 0;
            for x = plotBox
                if count < 2
                    count = count +1;
                    gphs(count) = plot(t,modBox(x{1}));
                    legend_text{count} = x{1};
                    plotBox(strcmp(plotBox,x{1})) = [];
                    hold on
                end
            end
            legend(gphs,legend_text);
            xlabel('Time in secs');
            ylabel('Power in Watts');
            grid on;
            hold off
        end
    end
end
end