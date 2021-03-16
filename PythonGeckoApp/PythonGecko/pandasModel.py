import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt


class pandasModel(QAbstractTableModel):
    """description of class"""
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data
    
    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]
    
    def returnLastSweep(self, parent=None):
        return self._data.iloc[-1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
    def clear(self):
        self.beginResetModel()
        self._data = pd.DataFrame(None)
        self.endResetModel()
      


