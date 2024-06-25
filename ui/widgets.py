from PyQt5.QtWidgets import *

class RadioButtonTableWidget(QWidget):
    def __init__(self, parent=None):
        super(RadioButtonTableWidget, self).__init__(parent)
        
        self.layout = QHBoxLayout()
        
        self.yesRadio = QRadioButton('Yes')
        self.noRadio = QRadioButton('No')
        
        self.layout.addWidget(self.yesRadio)
        self.layout.addWidget(self.noRadio)
        
        self.setLayout(self.layout)