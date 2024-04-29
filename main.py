import sys
from PyQt5.QtWidgets import QApplication
from ui import DashboardView

def main():
    app = QApplication(sys.argv)
    
    dashboard = DashboardView()
    dashboard.show()
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()