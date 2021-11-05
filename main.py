import sys

from PyQt5.QtWidgets import QApplication

# from PyQt5.QtGui import *
from pyefriend import StockAPI

if __name__ == "__main__":

    # create app
    app = QApplication(sys.argv)

    # api
    api = StockAPI()
    api.show()
    app.exec_()