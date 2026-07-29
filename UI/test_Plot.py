import sys
from PyQt6 import QtWidgets, uic
import pyqtgraph as pg

class CoordinatePlaneApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'C:\Users\nitro\WhoCaresAboutHUDandPitchComms\UI\PrimaryScreen.ui', self)
        self.plot_widget = self.findChild(pg.PlotWidget, 'graphicsView')

        # Set up coordinate plane axes
        self.plot_widget.setLabel('bottom', 'X Axis')
        self.plot_widget.setLabel('left', 'Y Axis')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setXRange(-1, 1)
        self.plot_widget.setYRange(-1, 1)

        # Prepare the scatter plot item for selected points
        self.scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush('r'), symbol='o')
        self.plot_widget.addItem(self.scatter)

        # Connect click event to the plot
        self.plot_widget.scene().sigMouseClicked.connect(self.on_plot_clicked)

    def on_plot_clicked(self, event):
        # Convert scene click position to plot coordinates
        pos = event.scenePos()
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
        x, y = mouse_point.x(), mouse_point.y()

        # Add the clicked point to the scatter plot
        self.scatter.addPoints([{'pos': (x, y)}])
        print(f"Point selected at: X = {x:.2f}, Y = {y:.2f}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CoordinatePlaneApp()
    window.show()
    sys.exit(app.exec())