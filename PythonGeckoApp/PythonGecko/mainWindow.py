# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'initializeWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


import sys
import threading
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QMessageBox,QAbstractButton
from  matplotlib.backends.backend_qt5agg  import  ( NavigationToolbar2QT  as  NavigationToolbar )
import matplotlib.pyplot as plt
import matplotlib as mpl
import  random
import math
from PyQt5 import QtCore,uic
from PyQt5.QtGui import QIcon
from pandasModel import pandasModel
from thermalParamClass import thermalParamClass
import pyqtgraph as pg
import functools
import re
import os
import numpy as np
import time as t
import csv
import pandas as pd
from retrying import retry
from GISMSParameters_phi import GISMSParameters_phi
import glob
import psweep as ps
import subprocess
#from pandasgui import show
from startConnection import startConnection 
from dataBaseClass import dataBaseClass
opLabelAppend = ''
class MainWindow(QMainWindow):
    invfilepath = r'calc\results.pk'
    afefilepath = r'calc_AFE\results.pk'
    Tfilepath = r'calc\Thermal\params.csv'
    ## Make all plots clickable
    clickedPen = pg.mkPen('b', width=2)
    lastClicked = []
    data2plot ={}
    filter = {}
    def __init__(self): 
        super().__init__()
        uic.loadUi('initializeWindow.ui',self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QIcon('clienticon.png'))
        self.setWindowTitle(_translate("MainWindow", "Inverter Sweep Store"))
        self.dateTimeLabel.setText(_translate("MainWindow", "12:02:59 Jan 12 2021"))
        self.simulateBtn.clicked.connect(self.simulate)
        self.showGSIMS.stateChanged.connect(self.showGSIMSData)
        self.tabWidget.currentChanged.connect(self.onChange)
        self.progressBar.hide()
        self.progressBar.reset()
        self.databaseBtn.clicked.connect(self.openDataBase) 
        self.pandasGUIBtn.clicked.connect(self.openPandasGUI)
        self.toolButtonIGBT.clicked.connect(self.loadThermalBox)
        self.toolButtonIGBT.setAutoRaise(True)
        self.toolButtonRev.clicked.connect(self.loadThermalBox)
        self.toolButtonRev.setAutoRaise(True)
        self.toolButtonFW.clicked.connect(self.loadThermalBox)
        self.toolButtonFW.setAutoRaise(True)
        self.loadPrevParams(self.invfilepath)
        self.plotControls.hide()
        if not os.path.exists(self.invfilepath) :
            self.thermalBtn.setEnabled(False)
        self.cid = self.MplWidget.canvas.mpl_connect('motion_notify_event', self.hover) 
        self.buttonGroupScatterData.setId(self.invTotalRadio,1)
        self.buttonGroupScatterData.setId(self.invIgbtRadio,2)
        self.buttonGroupScatterData.setId(self.invDiodeRadio,3)
        self.buttonGroupRangeType.setId(self.optPinToolBtn,1)
        self.buttonGroupRangeType.setId(self.optVdcToolBtn,2)
        self.buttonGroupRangeType.setId(self.optSwToolBtn,3)
        self.buttonGroupRangeType.buttonClicked[int].connect(self.toggleSlider)
        self.scDiodeCombo.textActivated.connect(self.scComboboxChanged)
        self.scIgbtCombo.textActivated.connect(self.scComboboxChanged)
        self.opComboType.textActivated.connect(self.updateOpBtnLabel)
        self.buttonGroupPlotType.buttonClicked.connect(self.selectPlotType)
        self.buttonGroupScatterData.buttonClicked.connect(self.updateScatterRadios)
        self.buttonGroupMode.buttonClicked.connect(self.updateAfeLabels)
        self.opAddBtn.clicked.connect(self.addFilterCriteria)
        self.plotBtn.clicked.connect(self.validateFilter)
        self.opClearBtn.clicked.connect(self.clear)
        self.InverterModeBtn.setChecked(True)
        self.searchOptBtn.clicked.connect(self.findOptimum)
        self.sc = {}
        self.df = pd.read_pickle(self.invfilepath)
        self.PinRangeSelector.hide()
        self.VdcRangeSelector.hide()
        self.SwRangeSelector.hide()
        self.VdcRangeSelector.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        self.VdcRangeSelector.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        self.VdcRangeSelector.setStyleSheet("""
        QRangeSlider > QSplitter::handle {
            background: #777;
            border: 1px solid #555;
        }
        QRangeSlider > QSplitter::handle:vertical {
            height: 2px;
        }
        QRangeSlider > QSplitter::handle:pressed {
            background: #ca5;
        }
        """)
        self.PinRangeSelector.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        self.PinRangeSelector.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        self.PinRangeSelector.setStyleSheet("""
        QRangeSlider > QSplitter::handle {
            background: #777;
            border: 1px solid #555;
        }
        QRangeSlider > QSplitter::handle:vertical {
            height: 2px;
        }
        QRangeSlider > QSplitter::handle:pressed {
            background: #ca5;
        }
        """)
        self.SwRangeSelector.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        self.SwRangeSelector.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        self.SwRangeSelector.setStyleSheet("""
        QRangeSlider > QSplitter::handle {
            background: #777;
            border: 1px solid #555;
        }
        QRangeSlider > QSplitter::handle:vertical {
            height: 2px;
        }
        QRangeSlider > QSplitter::handle:pressed {
            background: #ca5;
        }
        """)


    def openPandasGUI(self) :
        df = pd.read_pickle(self.invfilepath)
        #show(df)

    def conjunction(*conditions):
        return functools.reduce(np.logical_and, conditions)

    def clear(self):
        self.filter = {}
        self.opSelectDisplayLabel.clear()
        self.opAddBtn.setText('Add')
        self.opErrorLabel.setStyleSheet("")
        self.opErrorLabel.clear()

    def updateAfeLabels(self,button):
        if button.text()=='AFE':
            self.loadWLabel.setText("Mains in VA       :")
            self.loadVltg.setText("Mains Voltage       :")
            self.loadPrevParams(self.afefilepath)
            self.loadZ.setText("Load Inv(Z_inv) :")
        else :
            self.loadWLabel.setText("Load in VA        :")
            self.loadVltg.setText("Load Voltage       :")
            self.loadPrevParams(self.invfilepath)
            self.loadZ.setText("Load Imp(Z_L)  :")

    def updateOpBtnLabel(self):
        key = self.opComboType.currentText()
        if key in self.filter:
            self.opAddBtn.setText('Update')
        else:
            self.opAddBtn.setText('Add')

    def toggleSlider(self,id):
        vdcMinReq =  185
        vdcMaxReq = 260
        vdcNominal = 216
        fsMaxReq = 14400
        fsMinReq = 7200
        fsNominal = 10800
        pWNomial = 32000
        def findRange(Min,Max,MinReq,MaxReq):
            if(MinReq > Min):
                Min = MinReq
            if(MaxReq < Max):
                Max = MaxReq
            return Max,Min
        vDcMax = self.df['V_DC'].max()
        vDcMin = self.df['V_DC'].min()
        fsMax = self.df['f_s'].max()    
        fsMin = self.df['f_s'].min()
        if not 'PWatts' in self.df.columns:
            self.df['PWatts'] = round(self.df['Load_S']* self.df['Load_phi'].apply(math.cos))
        pWMax = self.df['PWatts'].max()
        pWMin = self.df['PWatts'].min()
        setVDcMax,setVDcMin = findRange(vDcMin,vDcMax,vdcMinReq,vdcMaxReq)
        setFsMax,setFsMin = findRange(fsMin,fsMax,fsMinReq,fsMaxReq)
        setPWMax,setPWMin = findRange(pWMin,pWMax,10000,pWNomial)
        btnOptions = { 1:{'rangeBtn':self.PinRangeSelector,'inputBtn':self.optPinInput,'Max':pWMax,'Min':pWMin,'rangeMin':setPWMin,'rangeMax':setPWMax,'normValue':1000,'decimalValue':1},
                       2:{'rangeBtn':self.VdcRangeSelector,'inputBtn':self.optVdcInput,'Max':vDcMax,'Min':vDcMin,'rangeMin':setVDcMin,'rangeMax':setVDcMax},
                       3:{'rangeBtn':self.SwRangeSelector,'inputBtn':self.optSwInput,'Max':fsMax,'Min':fsMin,'rangeMin':setFsMin,'rangeMax':setFsMax,'normValue':1000,'decimalValue':1}
                      }
        self.toggleInput(**btnOptions[id])
   
    def findOptimum(self):
        searchSeries = {}
        searchValue = []
        if not 'PWatts' in self.df.columns:
            self.df['PWatts'] = round(self.df['Load_S']* self.df['Load_phi'].apply(math.cos))
        try:
            def searchOptBtn(rangeBtn,column,inputBtn,normalizeValue =1):
                if rangeBtn.isVisible(): 
                    range = rangeBtn.getRange()
                    actual_range = tuple([normalizeValue*x for x in range])
                    searchValue = list(actual_range)
                    filterSeries = self.df[column].between(*actual_range)
                else:
                    searchValue = float(inputBtn.text())
                    filterSeries = self.df[column]==float(inputBtn.text())
                isAValidSeries = filterSeries.sum()                                
                if not isAValidSeries:
                    raise Exception("{} = {} not found".format(''.join(column),''.join(str(searchValue))))
                else : 
                    return filterSeries
            
            searchSeries['pSearchSeries'] = searchOptBtn(self.PinRangeSelector,'PWatts',self.optPinInput,1000)
            searchSeries['vDcSearchSeries'] = searchOptBtn(self.VdcRangeSelector,'V_DC',self.optVdcInput)
            searchSeries['sWSearchSeries'] = searchOptBtn(self.SwRangeSelector,'f_s',self.optSwInput,1000)
            conditionsBoolReturns = list(searchSeries.values())
            resultDataFrame = self.df[self.conjunction(*conditionsBoolReturns)]
            if resultDataFrame.empty :
                raise Exception("Not in DBase")
            else :
                self.processAndMaptoFigure(resultDataFrame)
        except Exception as e:
            #self.opErrorLabel.setStyleSheet("QLabel { background-color : yellow; color : red; }")
            print(str(e.args[0]))
    
    def processAndMaptoFigure(self,df):
        finalRow = df[df['InvTotalLoss']==df['InvTotalLoss'].min()].to_dict('records')[0]
        conductionLoss = [finalRow['IG1_con'],finalRow['D1_con'],finalRow['IG2_con'],finalRow['D2_con'],finalRow['D13_con']]
        switchLoss = [finalRow['IG1_sw'],finalRow['D1_sw'],finalRow['IG2_sw'],finalRow['D2_sw'],finalRow['D13_sw']]
        index  = ['T1/T4','D1/D4','T2/T3','D2/D3','D5/D6']
        df = pd.DataFrame({'Cond Loss': conductionLoss,'SW Loss': switchLoss}, index=index)
        self.OptimalChartArea.canvas.axes.clear()
        ax= df.plot(kind='bar',ax=self.OptimalChartArea.canvas.axes,rot=0)
        rects = ax.patches
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, round(height,2),
                    ha='center', va='bottom')
        ax.set_title('Operating Losses')
        ax.set_xlabel('Switches')
        ax.set_ylabel('Loss In Watts')
        textstr = "V_DC :{},\nTLoss:{},\nPdel :{},\nFsw   :{}".format("".join(str(finalRow['V_DC'])),"".join(str(round(finalRow['InvTotalLoss'],2))),
                                       "".join(str(finalRow['PWatts'])),"".join(str(finalRow['f_s'])))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=6,
                verticalalignment='top',horizontalalignment='left', bbox=props)
        self.OptimalChartArea.canvas.draw()
        self.OptimalChartArea.canvas.figure.set_visible(True)
        self.OptimalChartArea.toolbar.hide()
        self.OptimalChartArea.canvas.draw_idle()


    def toggleInput(self,rangeBtn,inputBtn,Max,Min,rangeMin,rangeMax,normValue= 1,decimalValue = 0):
            if rangeBtn.isVisible():
                rangeBtn.hide()
                inputBtn.show()
            else :
                rangeBtn.show()
                rangeBtn.setMin(round(Min/normValue,decimalValue))
                rangeBtn.setMax(round(Max/normValue,decimalValue))
                rangeBtn.setRange(round(rangeMin/normValue,decimalValue),round(rangeMax/normValue,decimalValue))
                inputBtn.hide()    

    def validateFilter(self) :
        filtString = {}
        try :
            button = self.buttonGroupScatterData.checkedButton()
            if button and button.text() =='Total Inverter Loss' :
                self.scIgbtCombo.setCurrentIndex(-1) 
                self.scDiodeCombo.setCurrentIndex(-1) 
                selected = 'InvTotalLoss'
            elif button and button.text() == 'IGBT ':
                selected =  self.scIgbtCombo.currentText()
                self.scDiodeCombo.setCurrentIndex(-1)
            elif button and button.text() == 'Diode':
                selected =  self.scDiodeCombo.currentText()
                self.scIgbtCombo.setCurrentIndex(-1) 
            if not selected:
                raise Exception("select the loss type")

            if len(self.filter) < 2 :
                raise Exception("min 2 filters required")
            elif len(self.filter) == 2 or len(self.filter) == 3:
                for key in self.filter :
                   filtString[key] =  (self.df[key] == self.filter[key])
                   if not filtString[key].values.sum():
                        raise Exception("{} = {} not found".format(''.join(key),''.join(str(self.filter[key]))))
            conditionsBoolReturns = list(filtString.values())
            resultDF = self.df[self.conjunction(*conditionsBoolReturns)]
            if resultDF.empty :
                raise Exception("Not in DBase")
            index = set(self.filterList)-self.filter.keys()
            key = 'Load_phi' if index == set() else index.pop()
            self.makeLinearPlot(resultDF,selected, key)
        except Exception as e:
            self.opErrorLabel.setStyleSheet("QLabel { background-color : yellow; color : red; }")
            self.opErrorLabel.setText(str(e.args[0]))


    def selectPlotType(self,button) :
        self.scatterDataBox.setEnabled(True)
        buttonBox = self.buttonGroupScatterData.checkedButton()
        if buttonBox :
            self.buttonGroupScatterData.setExclusive(False)
            buttonBox.setChecked(False)
            self.buttonGroupScatterData.setExclusive(True)
        if button.text() == 'Linear':
            self.opPointBox.setEnabled(True)
            self.buttonGroupScatterData.buttonClicked.disconnect()
            self.scDiodeCombo.textActivated.disconnect()
            self.scIgbtCombo.textActivated.disconnect()
        else :
            self.opPointBox.setEnabled(False)
            self.clear()
            self.buttonGroupScatterData.buttonClicked.connect(self.updateScatterRadios)
            self.scDiodeCombo.textActivated.connect(self.scComboboxChanged)
            self.scIgbtCombo.textActivated.connect(self.scComboboxChanged)
        
    
    
    def makeLinearPlot(self,df,ykey,key) :
        self.MplWidget.canvas.axes.clear()
        for key, grp in df.groupby([key]):
            l= grp.plot(ax=self.MplWidget.canvas.axes, kind='line', x='V_DC', y=ykey, marker='o',grid =True, label=key)
        self.sc['linear'] = l.lines
        self.sc.pop('scatter',None)
        self.annot = self.MplWidget.canvas.axes.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.cid = self.MplWidget.canvas.mpl_connect('motion_notify_event', self.hover)
        self.MplWidget.canvas.draw()
        self.MplWidget.canvas.figure.set_visible(True)
        self.MplWidget.toolbar.show()
        print(df)


    def updateScatterRadios(self,button,selected=None) :         
        yLabel = ''
        xLabel = ''
        xData = []
        yData = []
        if button.text() =='Total Inverter Loss' : 
            self.scIgbtCombo.setCurrentIndex(-1) 
            self.scDiodeCombo.setCurrentIndex(-1) 
            selected = 'InvTotalLoss'
        elif button.text() == 'IGBT ':
            self.scDiodeCombo.setCurrentIndex(-1)
        elif button.text() == 'Diode':
            self.scIgbtCombo.setCurrentIndex(-1) 
           
        if selected :
            self.data2plot['xData']= {'V_DC': list(self.df['V_DC'])}                
            self.data2plot['yData']= {selected: list(self.df[selected].fillna(0))}
            length = len(self.data2plot['yData'][selected])
            xLabel = 'Dc Link Voltage'
            yLabel =  button.text() if 'Loss' in button.text() else button.text()+' Loss'
            self.data2plot['Dataset'] = self.df
            self.plotScatter(self.data2plot['xData'],self.data2plot['yData'],xLabel,yLabel,length)


    def scComboboxChanged(self):
        sender = self.sender()
        selection = str(sender.currentText())
        if sender.objectName() == 'scDiodeCombo':
            self.invDiodeRadio.setChecked(True)
            self.updateScatterRadios(self.invDiodeRadio,selection)
        elif sender.objectName() == 'scIgbtCombo':
            self.invIgbtRadio.setChecked(True)
            self.updateScatterRadios(self.invIgbtRadio,selection)
        print(selection)
        
    
    def addFilterCriteria(self):
        try :
            item = str(self.opComboType.currentText())
            input = float(self.opComboInput.text())
            global opLabelAppend
            self.filter[item] = input
            if item in self.filter:
                for key in self.filter :
                    opLabelAppend = opLabelAppend + "{} = {}\n".format("".join(key),"".join(str(self.filter[key])))
            self.opSelectDisplayLabel.setText(opLabelAppend)
            opLabelAppend = ''
            self.opComboInput.clear()
            self.opAddBtn.setText('Update')
        except :
            self.opErrorLabel.setStyleSheet("QLabel { background-color : yellow; color : red; }")
            self.opErrorLabel.setText("Invalid {} input".format("".join(str(self.opComboType.currentText()))))

        
    def initializeControls(self):
        self.df = pd.read_pickle(self.invfilepath)
        self.MplWidget.canvas.mpl_disconnect(self.cid)
        self.scIgbtCombo.clear()
        self.scDiodeCombo.clear()
        igbtList = ['IG1','IG2','IG3','IG4']
        diodeList = ['D1','D2','D3','D4','D13','D14']
        self.filterList = ['Load_S','f_s','Load_phi']
        self.scIgbtCombo.addItems(igbtList)
        self.scDiodeCombo.addItems(diodeList)
        self.opComboType.addItems(self.filterList)
        self.scIgbtCombo.setCurrentIndex(-1) 
        self.scDiodeCombo.setCurrentIndex(-1) 
        button = self.buttonGroupPlotType.checkedButton()
        if button :
            self.buttonGroupPlotType.setExclusive(False)
            button.setChecked(False)
            self.buttonGroupPlotType.setExclusive(True)
        button = self.buttonGroupScatterData.checkedButton()
        if button :
            self.buttonGroupScatterData.setExclusive(False)
            button.setChecked(False)
            self.buttonGroupScatterData.setExclusive(True)
        self.plotScRadio.setChecked(False)  
        self.plotLinRadio.setChecked(False)
        self.invTotalRadio.setChecked(False)
        self.invDiodeRadio.setChecked(False) 
        self.invIgbtRadio.setChecked(False) 
        self.opPointBox.setEnabled(False)  
        self.scatterDataBox.setEnabled(False)
        self.clear()
        self.MplWidget.canvas.figure.set_visible(False)
        self.MplWidget.toolbar.hide()
        
    def plotScatter(self,xData,yData,xLabel,yLabel,length):
        self.MplWidget.canvas.axes.clear()
        self.c = np.random.randint(1,5,size=length)
        self.norm = plt.Normalize(1,4)
        self.cmap = plt.cm.RdYlGn
        self.sc['scatter'] = self.MplWidget.canvas.axes.scatter(list(xData.values()), list(yData.values()),c=self.c, s=10, cmap=self.cmap, norm=self.norm)
        self.sc.pop('linear', None)
        self.MplWidget.canvas.axes.set_xlabel(xLabel)
        self.MplWidget.canvas.axes.set_ylabel(yLabel)
        self.annot = self.MplWidget.canvas.axes.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.cid = self.MplWidget.canvas.mpl_connect('motion_notify_event', self.hover) 
        self.MplWidget.canvas.figure.set_visible(True)
        self.MplWidget.toolbar.show()
        self.MplWidget.canvas.draw()

        
    def update_scatter_annot(self,sc,ind):
        pos = sc.get_offsets()[ind]
        self.annot.xy = pos 
        OpPoint = self.data2plot['Dataset'][(self.data2plot['Dataset'][[*self.data2plot['xData']][0]] == pos[0]) & (self.data2plot['Dataset'][[*self.data2plot['yData']][0]] == pos[1])]

        text = "V_DC :{},\nTLoss:{},\nLoad :{},\nPhi    :{},\nFsw   :{}".format("".join(str(OpPoint.iloc[0]['V_DC'])),"".join(str(round(OpPoint.iloc[0]['InvTotalLoss'],2))),
                                       "".join(str(OpPoint.iloc[0]['Load_S'])),"".join(str(OpPoint.iloc[0]['Load_phi'])),
                                       "".join(str(OpPoint.iloc[0]['f_s'])))
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_facecolor(self.cmap(self.norm(self.c[ind])))
        self.annot.get_bbox_patch().set_alpha(0.4)

    def update_linear_annot(self, line,idx) : 
        posx, posy = [line.get_xdata()[idx], line.get_ydata()[idx]]
        self.annot.xy = (posx, posy)
        leg = line.axes.get_legend()
        ind = line.axes.get_lines().index(line)
        legPhi = leg.texts[ind].get_text()
        index = set(self.filterList)-self.filter.keys()
        key = 'Phi' if index == set() else index.pop()
        text = f'{key} :{legPhi},\nV_DC :{posx:.2f},\nTLoss :{posy:.2f}'
        self.annot.set_text(text)
        # annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self,event):
        vis = self.annot.get_visible()
        (key,lines),*rest = self.sc.items()
        lines = lines if isinstance(lines, list) else [lines]
        if event.inaxes == self.MplWidget.canvas.axes:
            for plotLine in lines :
                cont, ind = plotLine.contains(event)
                if cont:
                    if key == 'linear':
                        self.update_linear_annot(plotLine, ind['ind'][0])
                    if key == 'scatter':
                        self.update_scatter_annot(plotLine,ind['ind'][0])
                    self.annot.set_visible(True)
                    self.MplWidget.canvas.draw_idle()
                else:
                    if vis:
                        self.annot.set_visible(False)
                        self.MplWidget.canvas.draw_idle()
        

    def onChange(self, ord):
        if ord ==1:
            self.plotControls.show()
            self.initializeControls()
        else :
            self.plotControls.hide()
            self.MplWidget.canvas.toolbar_visible = False


    def checkThermalParams(self,df):
        def checkIfExists(sheetList):
            areAllinDB = True
            for sheet in sheetList:
                areAllinDB = areAllinDB and sheet in df.index
            return areAllinDB
        return checkIfExists


    def simulate(self):       
        try :
            dcVltgList = self.dcVltgIn.toPlainText()
            dcVltgList = re.split(',|\s+|;|\n',dcVltgList)
            dcVltgListNew = [int(i) for i in dcVltgList]
            loadWInList = self.loadWIn.toPlainText()
            loadWInList = re.split(',|\s+|;|\n',loadWInList)
            loadWInListNew = [int(i) for i in loadWInList]
            pfDegreeInList = self.pfDegreeIn.toPlainText()
            pfDegreeInList = re.split(',|\s+|;|\n',pfDegreeInList)
            pfDegreeInListNew = [float(i) for i in pfDegreeInList]
            switchFreqInList = self.switchFreqIn.toPlainText()
            switchFreqInList = re.split(',|\s+|;|\n',switchFreqInList)
            switchFreqInListNew = [int(i) for i in switchFreqInList]
            tempInList = self.tempIn.toPlainText()
            tempInList = re.split(',|\s+|;|\n',tempInList)
            tempInListNew = [int(i) for i in tempInList]
            fOutList = self.fOutIn.toPlainText()
            fOutList = re.split(',|\s+|;|\n',fOutList)
            fOutListNew = [int(i) for i in fOutList]
            igbtDataInList = self.igbtDataIn.toPlainText()
            igbtDataInList = re.split(',|\s+|;|\n',igbtDataInList)
            revDataInList = self.revDataIn.toPlainText()
            revDataInList = re.split(',|\s+|;|\n',revDataInList)
            fwDataInList = self.fwDataIn.toPlainText()
            fwDataInList = re.split(',|\s+|;|\n',fwDataInList)
            paramsContainer = {'V_DC':dcVltgListNew,'Load_S':loadWInListNew,'Load_phi':pfDegreeInListNew,'Mains_S':loadWInListNew,'Mains_phi':pfDegreeInListNew,'f_s':switchFreqInListNew,'f_out':fOutListNew,
                               'T_HS':tempInListNew,'Transistor':igbtDataInList,'Transistor_revD':revDataInList,'Transistor_fwD':fwDataInList }
            for x in paramsContainer:
                result = True
                if x=='Transistor' or x == 'Transistor_revD' or x== 'Transistor_fwD':
                    result = not(any([re.search("^\s*$", elem) for elem in paramsContainer[x]]))
                if paramsContainer[x] and result :
                    print(x + ':Accepted')
                else:
                    raise Exception('Please check the DataSheet inputs provided')
            self.statusWriteLabel.setStyleSheet("QLabel { background-color : green; color : black; }")
            self.statusWriteLabel.setText('Inputs are good')
            areAllinDb = False
            equalLenSheets = len(igbtDataInList)==len(revDataInList) and len(revDataInList)==len(fwDataInList)
            if os.path.exists(self.Tfilepath) and equalLenSheets:
                df = pd.read_csv(self.Tfilepath,index_col =['Datasheet'])
                tocheck = self.checkThermalParams(df)
                areAllinDb = tocheck(igbtDataInList) and tocheck(revDataInList) and tocheck(fwDataInList)
                if not areAllinDb:
                    raise Exception('Check the Thermal Params')
            else :
                msg = ('Input Sheets should be of same length', 'Thermal params file not found')[equalLenSheets]
                raise Exception(msg)
            self.statusWriteLabel.adjustSize()
            saveData = self.saveLossData.isChecked()
            isAFEselected = self.AFEModeBtn.isChecked()
            createobj = startConnection(paramsContainer,saveData,isAFEselected)
            createobj.gismsUpdate.connect(self.updateGSIMS)
            createobj.progressUpdate.connect(self.updateProgressBar)
            #createobj.eventemit()
            self.progressBar.show()
            self.progressBar.setValue(1)
            self.progressBar.setMaximum(100)
            test_thread = threading.Thread(target = createobj.initiateConnection)
            test_thread.start()
        
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText(str(e.args[0]))
            msgBox.exec()
        except :
            errorOutput = 'unexpected error : '+ str( sys.exc_info()[0])
            print(errorOutput)
            self.statusWriteLabel.setStyleSheet("QLabel { background-color : red; color : blue; }")
            self.statusWriteLabel.setText('Please check the inputs provided\n'+ str( sys.exc_info()[0]))
            self.statusWriteLabel.adjustSize()
   

    def showGSIMSData(self):
        if(self.showGSIMS.isChecked()):
            self.gridLayoutWidget.hide()
            self.GSIMSLabel.hide()
        else:
            self.gridLayoutWidget.show()
            self.GSIMSLabel.show()
    
            
    @QtCore.pyqtSlot(dict)
    def updateGSIMS(self,out):
        self.invCosPhiOut.setText(str(round(out['cos_phi_inv'],3)))
        self.modulationOut.setText(str(round(out['m'],3)))
        self.peakRlcCurrentOut.setText(str(round(out['I_Peak_inv'],2)))
        
        if self.AFEModeBtn.isChecked():
            self.loadVltgOut.setText(str(round(out['U_Mains_LL'],2)))
            self.loadZOut.setText(str(complex(round(out['Z_Inv'].real,2),round(out['Z_Inv'].imag,2))))
        else :
            self.loadVltgOut.setText(str(round(out['U_Load_LL'],2)))
            self.loadZOut.setText(str(complex(round(out['Z_Load'].real,2),round(out['Z_Load'].imag,2))))
        self.cCurrentOut.setText(str(round(out['I_Filter_C'],2)))
        self.lVltgOut.setText(str(round(out['U_Filter_L'],2)))
        self.invVtlgOut.setText(str(out['U_RMS_inv']))
    
        
    @QtCore.pyqtSlot(int,str)
    def updateProgressBar(self,value,text) :
        if value==-1:
            self.progressBar.setFormat(text)
        else :
            self.progressBar.setValue(value)
    

    def openDataBase(self):
        self.dataBaseWindow = dataBaseClass()
        self.dataBaseWindow.loadData()
        self.dataBaseWindow.show()
            

    def loadPrevParams(self,filepath):
        if os.path.exists(filepath):
            df = pd.read_pickle(filepath)
            self.model = pandasModel(df)
            lastSweepParams = self.model.returnLastSweep()
            self.dcVltgIn.setPlainText(str(lastSweepParams.V_DC))
            if self.AFEModeBtn.isChecked():
                self.loadWIn.setPlainText(str(lastSweepParams.Mains_S))
                self.pfDegreeIn.setPlainText(str(lastSweepParams.Mains_phi))
            else:
                self.loadWIn.setPlainText(str(lastSweepParams.Load_S))
                self.pfDegreeIn.setPlainText(str(lastSweepParams.Load_phi))
            self.switchFreqIn.setPlainText(str(lastSweepParams.f_s))
            self.tempIn.setPlainText(str(lastSweepParams.T_HS))
            self.fOutIn.setPlainText(str(lastSweepParams.f_out))
            self.igbtDataIn.setPlainText(str(lastSweepParams.Transistor))
            self.revDataIn.setPlainText(str(lastSweepParams.Transistor_revD))
            self.fwDataIn.setPlainText(str(lastSweepParams.Transistor_fwD))
        else : 
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText('Could not find data base!')
            msgBox.exec()
        

    def swit(self,x):
            return {
             'toolButtonIGBT': self.igbtDataIn.toPlainText(),
             'toolButtonFW': self.fwDataIn.toPlainText(),
             'toolButtonRev': self.revDataIn.toPlainText()
            }.get(x, [])


    def loadThermalBox(self):
        sender = self.sender()
        obj = sender.objectName()
        sheetList = self.swit(obj)
        sheetList = re.split(',|\s+|;|\n',sheetList)
        self.thermalWindow = thermalParamClass(sheetList)
        self.thermalWindow.show()


                 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window....')
