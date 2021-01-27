from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow
from PyQt5 import QtCore,uic
from PyQt5.QtGui import QIcon
from pandasModel import pandasModel
import pandas as pd

class dataBaseClass(QWidget):
    filepath = r'calc\\results.pk'
    def __init__(self): 
        super().__init__()
        uic.loadUi('dataBaseWindow.ui',self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QIcon('dataIcon.png'))
        self.setWindowTitle(_translate("Form", "Simulated Data"))
        self.refreshBtn.clicked.connect(self.loadData)
        self.exitBtn.clicked.connect(self.close)
        self.loadData()
        
    def loadData(self) :
        df = pd.read_pickle(self.filepath)
        self.model = pandasModel(df)
        self.dataBaseTableView.setModel(self.model)

    
    
    



