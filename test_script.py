import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget

app = QApplication(sys.argv)
api = QAxWidget('ITGExpertCtl.ITGExpertCtlCtrl.1')