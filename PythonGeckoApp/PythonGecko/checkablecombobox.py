# importing libraries 
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys 
  
  
# new check-able combo box 
class CheckableComboBox(QComboBox): 
  
    # constructor 
    def __init__(self, parent = None): 
        super(CheckableComboBox, self).__init__(parent) 
        self.view().pressed.connect(self.handleItemPressed) 
        self.setModel(QStandardItemModel(self)) 
  
    
    # when any item get pressed 
    def handleItemPressed(self, index): 
        # getting the item 
        item = self.model().itemFromIndex(index) 
        # checking if item is checked 
        if item.checkState() == Qt.Checked: 
            # making it unchecked 
            item.setCheckState(Qt.Unchecked) 
        # if not checked 
        else: 
            # making the item checked 
            item.setCheckState(Qt.Checked) 
    
    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(item.text())
        return checkedItems

