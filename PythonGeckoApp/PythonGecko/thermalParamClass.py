from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QMessageBox
from PyQt5 import QtCore,uic
from PyQt5.QtGui import QIcon
from pandasModel import pandasModel
import pandas as pd
import re
import os
class thermalParamClass(QWidget):
    filepath = r'calc\Thermal\params.csv'
    #thermalInputSignal = pyqtSignal(int,str)
    def __init__(self,datasheets): 
        super().__init__()
        uic.loadUi('thermalParametersDialogModular.ui',self)
        self.datasheets = datasheets
        self.available = False
        self.missingSheets = datasheets
        self.thermDoneBtn.clicked.connect(self.storeThermalInputs)
        self.thermCnclBtn.clicked.connect(self.close)
        self.readAnyExisting()
        

    def storeThermalInputs(self) :
        thermalParaInputs = {}
        itemLength = []
        thermalParaInputs['Rcs'] = re.split(',|\s+|;|\n',self.rcs.toPlainText())
        thermalParaInputs['Rjc'] = re.split(',|\s+|;|\n',self.rjc.toPlainText())
        thermalParaInputs['Cth'] = re.split(',|\s+|;|\n',self.cth.toPlainText())
        isValid = len(thermalParaInputs['Rcs']) == len(thermalParaInputs['Rjc']) and len(thermalParaInputs['Rjc']) == len(thermalParaInputs['Cth'])
        
        thermalParaInputs['Datasheet'] = self.missingSheets
        if isValid  and len(thermalParaInputs['Rcs']) == len(self.missingSheets) :
            thermalDF = pd.DataFrame(thermalParaInputs)
            thermalDF.set_index('Datasheet',inplace=True)
            print(thermalDF)
            with open(self.filepath, 'a') as path:
                thermalDF.to_csv(path,header=path.tell()==0)
            self.close()
        else : 
            msgBox = QMessageBox()
            msgBox.setText("Please check the inputs")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec()

    def readAnyExisting(self) :
        if os.path.exists(self.filepath):
            df = pd.read_csv(self.filepath,index_col =['Datasheet'])
            thermalSet = {}
            for sheet in self.datasheets:
                if sheet in df.index:
                    thermalSet.update(df.loc[df.index ==sheet].to_dict(orient = 'index'))
            if len(thermalSet) == len(self.datasheets):
                self.inputLabel.setText('Available :')
                self.displayEdit.setText(str(len(thermalSet)))
                for x in thermalSet:
                    self.rcs.append(str(thermalSet[x]['Rcs']))
                    self.rjc.append(str(thermalSet[x]['Rjc']))
                    self.cth.append(str(thermalSet[x]['Cth']))    
                    self.available = True
                    self.thermDoneBtn.setEnabled(False)     
            else:
                for index in thermalSet:
                    for ds in self.datasheets:
                        if(index == ds):
                            self.missingSheets.remove(index)
                self.inputLabel.setText('Missing :'+ str(len(self.missingSheets)))
                missingSheets_text = ',\n'.join(map(str, self.missingSheets)) 
                self.displayEdit.setText(missingSheets_text)
           
        else :
            msgBox = QMessageBox();
            msgBox.setText("No Thermal parameters found, please enter new...");
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec();
            self.inputLabel.setText('Missing :'+ str(len(self.missingSheets)))
            missingSheets_text = ','.join(map(str, self.missingSheets)) 
            self.displayEdit.setText(missingSheets_text)
            
  