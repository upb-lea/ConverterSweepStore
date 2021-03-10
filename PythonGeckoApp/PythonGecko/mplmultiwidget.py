# ------------------------------------------------- ----- 
# -------------------- mplmultiwidget.py -------------------- 
# -------------------------------------------------- ---- 
from  PyQt5.QtWidgets  import *
from  matplotlib.backends.backend_qt5agg  import  FigureCanvas
from  matplotlib.backends.backend_qt5agg  import  ( NavigationToolbar2QT  as  NavigationToolbar )
from  matplotlib.figure  import  Figure

    
class  MplMultiWidget(QWidget):
    
    def __init__(self, parent  =  None ):

        QWidget.__init__(self, parent)
        self.canvas  =  FigureCanvas(Figure())
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid_Layout = QGridLayout()
        grid_Layout.addWidget (self.canvas)
        grid_Layout.addWidget (self.toolbar)
        self.setLayout(grid_Layout)
    
    def plotOne(self, dfContainer, opPointRow):
        self.canvas.figure.clf()
        self.canvas.figure.suptitle('Operating Losses')
        dfList = list(dfContainer.values())
        opPointList = list(opPointRow.values())
        topologyList = list(dfContainer.keys())
        df = dfList[0]
        self.canvas.axes  =  self.canvas.figure.add_subplot(111) 
        self.canvas.axes.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axes,rot=0)
        self.createPatches(ax, opPointList[0], topologyList[0])
        self.canvas.figure.set_visible(True)
        self.canvas.draw_idle()

    def plotTwo(self, dfContainer,opPointRow):
        self.canvas.figure.clf()
        self.canvas.figure.suptitle('Operating Losses')
        dfList = list(dfContainer.values())
        opPointList = list(opPointRow.values())
        topologyList = list(dfContainer.keys())
        df = dfList[0]
        self.canvas.axesOne  =  self.canvas.figure.add_subplot(121) 
        self.canvas.axesOne.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesOne,rot=0)
        self.createPatches(ax, opPointList[0], topologyList[0])

        df = dfList[1]
        self.canvas.axesTwo  =  self.canvas.figure.add_subplot(122, sharey = self.canvas.axesOne) 
        self.canvas.axesTwo.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesTwo,rot=0)
        self.createPatches(ax, opPointList[1],topologyList[1])

        self.canvas.figure.set_visible(True)
        self.canvas.draw_idle()

    def plotThree(self, df, opPointRow):
        self.canvas.figure.clf()
        self.canvas.axes  =  self.canvas.figure.add_subplot(221) 
    def plotFour(self, df, opPointRow):
        self.canvas.figure.clf()
        self.canvas.axes  =  self.canvas.figure.add_subplot(221) 
       
    def createPatches(self, ax, opPointRow, topology):
        rects = ax.patches
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, round(height,2),
                    ha='center', va='bottom')
        ax.set_title(topology)
        ax.set_xlabel('Switches')
        ax.set_ylabel('Loss In Watts')
        textstr = "V_DC :{},\nTLoss:{},\nPdel :{},\nFsw   :{}".format("".join(str(opPointRow['V_DC'])),"".join(str(round(opPointRow['InvTotalLoss'],2))),
                                        "".join(str(opPointRow['PWatts'])),"".join(str(opPointRow['f_s'])))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=6,
                verticalalignment='top',horizontalalignment='left', bbox=props)
        #self.OptimalChartArea.canvas.draw()
        #self.OptimalChartArea.toolbar.hide()
            



