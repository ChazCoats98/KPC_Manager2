from PyQt5.QtWidgets import QApplication

        
        
def renderDashboard():
    global d
    d = dashboard()
    d.show()
    window.close()
    
app = QApplication(sys.argv)
window = loginWindow()
window.show()
app.exec_()