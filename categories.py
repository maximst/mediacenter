from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ('path/to/image.png', handler)
CATEGORIES = (
    ('img/categories/tv.png', ''),
    ('img/categories/1tv.png', ''),
    ('img/categories/russia1.png', ''),
    ('img/categories/youtube.png', 'show_youtube')
)


class CategoriesList(QListWidget):
    def __init__(self, *args, **kwsrgs):
        super().__init__(*args, **kwsrgs)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(50,50,50, 1);
                color: #fff;
                border: none;
            }
            QWidget:item:selected {
                background-color: rgba(100,100,100, 0.5);
            }
            QWidget:item {
                background-color: rgba(50,50,50,1);
                text-align: center;
            }
        """)
        self.setFixedWidth(125)

        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def connect(self, item):
        if hasattr(item, 'handler') and item.handler:
            item.handler()


class Categories(QDockWidget):
    def __init__(self, *args, **kwsrgs):
        super().__init__(*args, **kwsrgs)
        self.setFloating(False)
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(Categories.NoDockWidgetFeatures)
        self.categories_list = CategoriesList()
        self.setWidget(self.categories_list)

    def render(self):
        _handler = lambda: print('Switch category')
        for i, item in enumerate(CATEGORIES or []):
            list_item = QListWidgetItem(QIcon(item[0]), '')
            list_item.handler = getattr(self.window(), item[1], _handler)
            self.categories_list.addItem(list_item)

        self.categories_list.setIconSize(QSize(100, 100))
        self.categories_list.itemActivated.connect(self.categories_list.connect)

        self.categories_list.item(0).setSelected(True)
        self.categories_list.setFocus()
