# -*-coding: utf-8 -*-
# Created by samwell

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from view.mainwnd import MainWindow

from svc import SvcEntity

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        svc = SvcEntity.GetSvcEntity()
    except Exception as e:
        QMessageBox.critical(None, 'Error',
                             f'Initialization failed!\nPlease check files,directories and run as administrator.\nInformation:\n {e}')
        sys.exit(-1)

    wnd = MainWindow(svc)
    wnd.show()
    sys.exit(app.exec_())
