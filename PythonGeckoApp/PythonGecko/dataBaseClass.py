from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow
from PyQt5 import QtCore,uic
from PyQt5.QtGui import QIcon
from pandasModel import pandasModel
import pandas as pd
import os

class dataBaseClass(QWidget):
    invfilepath = r'calc\results.pk'
    afefilepath = r'calc_AFE\results.pk'
    
    def __init__(self, parent=None): 
        super(dataBaseClass,self).__init__(parent)
        uic.loadUi('dataBaseWindow.ui',self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QIcon('dataIcon.png'))
        self.setWindowTitle(_translate("Form", "Simulated Data"))
        self.refreshBtn.clicked.connect(self.refreshTableView)
        self.exitBtn.clicked.connect(self.close)
        self.refreshTableView()
        #self.applyTheme()

    def applyTheme(self):
        self.setStyle('Fusion')
        self.setPalette(palette)

    def refreshTableView(self):
        simCount = 0
        filepath = None
        topology = self.buttonGroupDbType.checkedButton().text()
        mode = self.buttonGroupDbMode.checkedButton().text()
        if mode == 'Inverter':
           filepath =self.invfilepath
        elif mode == 'AFE' :
           filepath = self.afefilepath
        if os.path.exists(filepath) :
            df = pd.read_pickle(filepath)
            if topology == 'Explore All':
                self.model = pandasModel(df)
            else:
                self.model = pandasModel(df[df['Topology']==topology])
            simCount= self.model.rowCount()  
            self.rowCountLabel.setStyleSheet("QLabel { background-color : green; color : black; }")
            self.rowCountLabel.setText(str(simCount)+ ' simulations exists!')
            self.dataBaseTableView.setModel(self.model)
        else :
            self.model.clear()
            self.rowCountLabel.setStyleSheet("QLabel { background-color :yellow ; color : red; }")
            self.rowCountLabel.setText('No database found!')
        
        
        
            

    
    
    



