import sys
import pandas as pd
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg


class StrikeZonePlot(QtWidgets.QMainWindow):
    def __init__(self, csv_path, batter_name):
        super().__init__()

        # Load CSV
        csv_path = r"C:\Users\nitro\WhoCaresAboutHUDandPitchComms\csv\NewHeightMetrics(ZoneDim).csv"
        df = pd.read_csv(csv_path)

        # Lookup batter zone values
        try:
            row = df.loc[df['name'] == batter_name].iloc[0]
        except IndexError:
            raise ValueError(f"Batter '{batter_name}' not found in CSV")

        zone_top = float(row['zone_top'])
        zone_bottom = float(row['zone_bottom'])

        # Strike zone height in inches
        zone_height = zone_top - zone_bottom

        # Strike zone width is always 17 inches
        zone_width = 17.0

        # Normalize height to coordinate plane [-1, 1]
        height_scale = 1.0
        width_scale = zone_width / zone_height

        # Main widget + layout
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        self.setCentralWidget(central)

        # Plot widget
        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)

        # Confirm button
        self.confirm_button = QtWidgets.QPushButton("Confirm Point")
        layout.addWidget(self.confirm_button)

        # Set domain & range
        self.plot.setXRange(-1, 1)
        self.plot.setYRange(-1, 1)
        self.plot.showGrid(x=True, y=True)

        # Title
        self.plot.setTitle(
            f"{batter_name} Strike Zone\n"
            f"Top={zone_top}, Bottom={zone_bottom}, Height={zone_height:.2f} in"
        )

        # Draw strike zone rectangle
        rect_height = height_scale
        rect_width = width_scale

        x_left = -rect_width / 2
        y_bottom = -rect_height / 2

        strike_zone = pg.QtGui.QGraphicsRectItem(
            x_left, y_bottom, rect_width, rect_height
        )
        strike_zone.setPen(pg.mkPen('r', width=3))
        self.plot.addItem(strike_zone)

        # Scatter plot for clicked points
        self.scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush('y'))
        self.plot.addItem(self.scatter)

        # Store last clicked point
        self.last_point = None

        # Connect click event
        self.plot.scene().sigMouseClicked.connect(self.on_plot_clicked)

        # Connect confirm button
        self.confirm_button.clicked.connect(self.on_confirm)

    def on_plot_clicked(self, event):
        pos = event.scenePos()
        mouse_point = self.plot.plotItem.vb.mapSceneToView(pos)
        x, y = mouse_point.x(), mouse_point.y()

        # Store last clicked point
        self.last_point = (x, y)

        # Show point visually
        self.scatter.addPoints([{'pos': (x, y)}])

        print(f"Clicked point: X={x:.3f}, Y={y:.3f}")

    def on_confirm(self):
        if self.last_point is None:
            print("No point selected yet.")
            return

        x, y = self.last_point
        print(f"Confirmed point: X={x:.3f}, Y={y:.3f}")

        # Call your Unity function
        self.send_to_unity(x, y)

    def send_to_unity(self, x, y):
        """
        Replace this with your actual Unity communication logic.
        For now, it just prints the values.
        """
        print(f"Sending to Unity: X={x:.3f}, Y={y:.3f}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = StrikeZonePlot(
        csv_path=r"C:\Users\nitro\WhoCaresAboutHUDandPitchComms\data\batter_data.csv",
        batter_name="Aaron Judge"
    )

    window.resize(600, 600)
    window.show()

    sys.exit(app.exec())
