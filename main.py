import sys

from PyQt5.QtWidgets import QApplication

from pyefriend import DomesticAPI

if __name__ == "__main__":

    # create app
    app = QApplication(sys.argv)

    # api
    api = DomesticAPI()
    print('api.is_connected', api.is_connected)
    print('encrypted_password', api.encrypted_password)
    print('all_accounts', api.all_accounts)

    print('Session', api.session.GetAccountCount())

    api.show()

    sys.exit(app.exec_())
