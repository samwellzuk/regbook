# -*-coding: utf-8 -*-
# Created by samwell

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from view.mainwnd import MainWindow

from svc import SvcEntity


def main():
    app = QApplication(sys.argv)

    try:
        svc = SvcEntity.GetSvcEntity()
    except Exception as e:
        QMessageBox.critical(
            None,
            'Error',
            f'Initialization failed!\nPlease check files,directories and run as administrator.\nInformation:\n {e}')
        return -1

    wnd = MainWindow(svc)
    wnd.show()
    return app.exec()


if __name__ == "__main__":
    rt = -1
    try:
        rt = main()
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))
    sys.exit(rt)
