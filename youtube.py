from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class YouTubeView(object):
    rendered = False

    def __init__(self, parent=None):
        self.parent = parent
        self.search = QLineEdit()
        self.result = QListWidget()
        self.layout = QFormLayout()
        label = QLabel("Search")
        self.layout.addRow(QLabel("Search"), self.search)
        self.layout.addRow(self.result)

        style = """
            QWidget {
                background-color: rgba(50,50,50, 0.8);
                color: #fff;
            }
        """
        label.setStyleSheet(style)
        self.result.setStyleSheet(style)
        self.search.setStyleSheet(style)

    def render(self):
        print('RENDER')
        self.parent.setLayout(self.layout)
        self.rendered = True

    def show(self):
        self.parent.setLayout(self.layout)

    def setFocus(self):
        self.search.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.parent.window().categories.show()
            self.parent.window().categories.categories_list.setFocus()
