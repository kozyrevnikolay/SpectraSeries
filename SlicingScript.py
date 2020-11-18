import pyqtgraph as pg
import numpy as np
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QSpinBox, QLineEdit, QPushButton, QGroupBox, QGridLayout, QLabel,
                             QFileDialog, QListWidget, QListWidgetItem)


class MainWindow(QWidget):
    filenames = None
    data = None
    series_parameter = None
    slice_data = None
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        self.plot_box = PlotBox()
        self.data_box = DataBox()
        layout.addWidget(self.plot_box, 0, 0, 2, 1)
        layout.addWidget(self.data_box, 0, 1, 1, 1)
        layout.setColumnStretch(0, 1)

        self.data_box.add_data_btn.clicked.connect(self.add_data)
        self.data_box.reference.textChanged.connect(self.match_reference)
        self.data_box.get_slice.valueChanged.connect(self.update_graph)
        self.data_box.save_slice_btn.clicked.connect(self.save_slice)

    def add_data(self):
        self.filenames = QFileDialog.getOpenFileNames(caption='Open Files', filter='Data (*.dat, *.txt)')[0]
        num_of_files = len(self.filenames)

        self.data_box.reference.setText(self.filenames[0].split('/')[-1])
        self.data_box.file_list.clear()
        for filename, f in zip(self.filenames, range(num_of_files)):
            self.data_box.file_list.addItem(QListWidgetItem(self.filenames[f].split('/')[-1]))

        if num_of_files == 0:
            pass
        else:
            self.data = {filename: np.loadtxt(filename) for filename in self.filenames}
        self.data_box.get_slice.setMaximum(len(self.data[self.filenames[0]][:, 0]))

    def match_reference(self):
        float_re = re.compile('\+?-?[0-9]*.?[0-9]*')
        if self.filenames is None:
            pass
        else:
            regular_expr = self.data_box.reference.text()
            if 'float' in regular_expr:
                regular_expr = regular_expr.replace('float', float_re.pattern)
            self.series_parameter = {filename: float(float_re.search(filename.split('/')[-1])[0])
                                     for filename in self.filenames if re.search(regular_expr, filename)}
        self.update_graph()

    def update_graph(self):
        value_column = 3
        slice_row = self.data_box.get_slice.value()
        if self.series_parameter and self.data is not None:
            wavelength = self.data[self.filenames[0]][:, 0]
            self.data_box.slice_value.setText(str(wavelength[slice_row - 1]))
            self.slice_data = np.array([[1239.8/self.series_parameter[filename], self.data[filename][slice_row - 1, value_column]]
                             for filename in self.filenames])
            # self.plot_box.plot_data_item.clear()
            self.plot_box.plot_data_item.setData(self.slice_data)

    def save_slice(self):
        point = self.data_box.get_slice.value()
        wl = self.data[self.filenames[0]][point, 0]
        if self.series_parameter and self.data is not None:
            np.savetxt('slice at wavelength {:.2f}nm ({:d} point).txt'.format(wl, point), self.slice_data)


class PlotBox(QGroupBox):
    def __init__(self):
        super().__init__('Slice plot')
        layout = QGridLayout(self)
        self.plot_item = pg.PlotWidget()
        self.plot_data_item = pg.PlotDataItem()
        self.plot_item.addItem(self.plot_data_item)
        self.plot_item.getPlotItem().setLogMode(y=True)
        layout.addWidget(self.plot_item)


class DataBox(QGroupBox):
    def __init__(self):
        super().__init__('Data')
        layout = QGridLayout(self)

        self.add_data_btn = QPushButton('Add data')
        self.add_data_btn.setFixedWidth(100)

        self.save_slice_btn = QPushButton('Save slice')
        self.save_slice_btn.setFixedWidth(100)

        self.get_slice = QSpinBox()
        self.get_slice.setMinimum(1)

        self.slice_value = QLineEdit()
        self.slice_value.setFixedWidth(100)
        self.slice_value.setReadOnly(True)

        self.reference = QLineEdit()

        self.file_list = QListWidget()
        layout.addWidget(self.add_data_btn, 0, 0, 1, 1)
        layout.addWidget(self.save_slice_btn, 0, 1, 1, 1)
        layout.addWidget(QWidget(), 1, 0, 1, 1)
        layout.addWidget(QLabel('Slice row'), 2, 0, 1, 1)
        layout.addWidget(self.get_slice, 3, 0, 1, 1)
        layout.addWidget(QLabel('Slice value'), 2, 1, 1, 1)
        layout.addWidget(self.slice_value, 3, 1, 1, 1)
        layout.addWidget(QWidget(), 4, 0, 1, 1)
        layout.addWidget(QLabel('Reference'), 5, 0, 1, 2)
        layout.addWidget(self.reference, 6, 0, 1, 2)
        layout.addWidget(QWidget(), 7, 0, 1, 1)
        layout.addWidget(QLabel('File list'), 8, 0, 1, 2)
        layout.addWidget(self.file_list, 9, 0, 1, 2)
        layout.setSpacing(4)
        layout.setRowStretch(9, 1)
        layout.setColumnMinimumWidth(0, 100)
        layout.setColumnMinimumWidth(1, 100)


class Reference(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

if __name__ == '__main__':
    app = QApplication([])
    main = MainWindow()
    main.show()
    app.exec_()