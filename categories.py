from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from decorators import click_protection

# ('path/to/image.png', handler)
CATEGORIES = (
    ('img/categories/tv.png', 'show_tv'),
    ('img/categories/1tv.png', 'show_onetv'),
    ('img/categories/russia1.png', ''),
    ('img/categories/youtube.png', 'show_youtube')
)


class CategoriesList(QListWidget):
    def __init__(self, *args, **kwsrgs):
        super().__init__(*args, **kwsrgs)
        self.setFixedWidth(180)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def connect(self, item):
        if hasattr(item, 'handler') and item.handler:
            item.handler()

    @click_protection
    def keyPressEvent(self, event):
        super().keyPressEvent(event)


class Categories(QDockWidget):
    def __init__(self, *args, **kwsrgs):
        super().__init__(*args, **kwsrgs)
        self.setFloating(False)
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(Categories.NoDockWidgetFeatures)
        self.categories_list = CategoriesList()
        self.setWidget(self.categories_list)
        self.setStyleSheet("""
            Categories {
                margin: 0 0 20px 20px;
            }
            CategoriesList {
                background-color: rgb(50,50,50);
                color: #fff;
                border: none;
                margin-left: 65px;
                margin-top: 5px;
            }
            CategoriesList:item:selected {
                background-color: rgb(100,100,100);
            }
            CategoriesList:item {
                text-align: center;
            }
        """)

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

    @click_protection
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
