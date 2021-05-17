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
        ax= df.plot(kind='bar',ax=self.canvas.axes,rot=0, legend=False)
        self.createPatches(ax, opPointList[0], topologyList[0])
        lines, labels = self.canvas.figure.axes[-1].get_legend_handles_labels()
        self.canvas.figure.tight_layout()
        self.canvas.figure.legend(lines, labels, loc = 'upper left')
        self.canvas.figure.text(0.5, 0, 'Switches', ha='center')
        self.canvas.figure.text(0, 0.5, 'Loss In Watts', va='center', rotation='vertical')   
        self.canvas.figure.set_visible(True)
        self.canvas.toolbar.show()
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
        ax= df.plot(kind='bar',ax=self.canvas.axesOne,rot=0,legend=False)
        self.createPatches(ax, opPointList[0], topologyList[0])

        df = dfList[1]
        self.canvas.axesTwo  =  self.canvas.figure.add_subplot(122, sharey = self.canvas.axesOne) 
        self.canvas.axesTwo.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesTwo,rot=0, legend=False)
        self.createPatches(ax, opPointList[1],topologyList[1])
        lines, labels = self.canvas.figure.axes[-1].get_legend_handles_labels()
        self.canvas.figure.tight_layout()
        self.canvas.figure.legend(lines, labels, loc = 'upper left')
        self.canvas.figure.text(0.5, 0, 'Switches', ha='center')
        self.canvas.figure.text(0, 0.5, 'Loss In Watts', va='center', rotation='vertical')   
        self.canvas.toolbar.show()
        self.canvas.figure.set_visible(True)
        self.canvas.draw_idle()

    def plotThree(self, dfContainer, opPointRow):
        self.canvas.figure.clf()
        self.canvas.figure.suptitle('Operating Losses')
        dfList = list(dfContainer.values())
        opPointList = list(opPointRow.values())
        topologyList = list(dfContainer.keys())

        df = dfList[0]
        self.canvas.axesOne  =  self.canvas.figure.add_subplot(221) 
        self.canvas.axesOne.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesOne,rot=0, legend=False)
        self.createPatches(ax, opPointList[0], topologyList[0])

        df = dfList[1]
        self.canvas.axesTwo  =  self.canvas.figure.add_subplot(222, sharey = self.canvas.axesOne) 
        self.canvas.axesTwo.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesTwo,rot=0, legend=False)
        self.createPatches(ax, opPointList[1],topologyList[1])

        df = dfList[2]
        self.canvas.axesThree  =  self.canvas.figure.add_subplot(223, sharey = self.canvas.axesOne) 
        self.canvas.axesThree.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesThree,rot=0, legend=False)
        self.createPatches(ax, opPointList[2],topologyList[2])

        lines, labels = self.canvas.figure.axes[-1].get_legend_handles_labels()
        self.canvas.figure.tight_layout()
        self.canvas.figure.legend(lines, labels, loc = 'upper left')
        self.canvas.figure.text(0.5, 0, 'Switches', ha='center')
        self.canvas.figure.text(0, 0.5, 'Loss In Watts', va='center', rotation='vertical')   
        self.canvas.figure.set_visible(True)
        self.canvas.toolbar.show()
        self.canvas.draw_idle()
    def plotFour(self, dfContainer, opPointRow):
        self.canvas.figure.clf()
        self.canvas.figure.suptitle('Operating Losses')
        dfList = list(dfContainer.values())
        opPointList = list(opPointRow.values())
        topologyList = list(dfContainer.keys())

        df = dfList[0]
        self.canvas.axesOne  =  self.canvas.figure.add_subplot(221) 
        self.canvas.axesOne.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesOne,rot=0, legend=False)
        self.createPatches(ax, opPointList[0], topologyList[0])

        df = dfList[1]
        self.canvas.axesTwo  =  self.canvas.figure.add_subplot(222, sharey = self.canvas.axesOne) 
        self.canvas.axesTwo.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesTwo,rot=0, legend=False)
        self.createPatches(ax, opPointList[1],topologyList[1])

        df = dfList[2]
        self.canvas.axesThree  =  self.canvas.figure.add_subplot(223, sharey = self.canvas.axesOne) 
        self.canvas.axesThree.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesThree,rot=0, legend=False)
        self.createPatches(ax, opPointList[2],topologyList[2])

        df = dfList[3]
        self.canvas.axesFour =  self.canvas.figure.add_subplot(224, sharey = self.canvas.axesOne) 
        self.canvas.axesFour.clear()
        ax= df.plot(kind='bar',ax=self.canvas.axesFour,rot=0, legend=False)
        self.createPatches(ax, opPointList[3],topologyList[3])

        lines, labels = self.canvas.figure.axes[-1].get_legend_handles_labels()
        self.canvas.figure.tight_layout()
        self.canvas.figure.legend(lines, labels, loc = 'upper left')
        self.canvas.figure.text(0.5, 0, 'Switches', ha='center')
        self.canvas.figure.text(0, 0.5, 'Loss In Watts', va='center', rotation='vertical')   
        self.canvas.toolbar.show()
        self.canvas.figure.set_visible(True)
        self.canvas.draw_idle()
       




    def createPatches(self, ax, opPointRow, topology):
        rects = ax.patches
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, round(height,1),
                    ha='center', va='bottom')
        ax.set_title(topology)
        textstr = "DS: {},\nV_DC :{},\nTLoss:{},\nPdel :{},\nFsw   :{}".format("".join(str(opPointRow['Datasheet'])),"".join(str(opPointRow['V_DC'])),"".join(str(round(opPointRow['ConvTotalLoss'],2))),
                                        "".join(str(opPointRow['PWatts'])),"".join(str(opPointRow['f_s'])))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=6,
                va='top',ha='right', bbox=props)
        #self.OptimalChartArea.canvas.draw()
        #self.OptimalChartArea.toolbar.hide()
            



