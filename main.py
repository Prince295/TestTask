import os
import sys
import logging
import datetime


from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from PyQt5.QtWidgets import QMainWindow, QFrame, QMessageBox, QWidget, \
    QVBoxLayout, QAction, QSplitter, QPushButton, QTableWidget, QAbstractItemView, QTableWidgetItem, \
    QDialog, QGridLayout, QApplication, QLabel, QLineEdit, QTabWidget, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *

from model import Base
from settings import DATABASE_URL, BASE_PATH

# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

rus = {
    'part_number' : 'Партия',
    'problem' : 'Описание проблемы',
    'how_to_fix' : 'Что надо сделать',
    'logfiles' : 'Журнал',
    'id': 'id',
    'name': 'Название',
    'description': 'Описание',
    'model': 'Модель',
    'author': 'Автор',
    'turn': 'Смена',
    'area': 'Участок',
    'part_name' : 'Назв. партии',
    'iln': 'ILN',
    'cut_off_vin': 'CUT-OFF VIN',
    'date' : 'Дата',
    'vin' : 'VIN',
    'ran' : 'RAN',
    'creator' : 'Поставщик',
    'part_number_id' : 'Номер партии',
    'done_actions' : 'Какие действия сделаны',
    'reason' : 'Описание причины'
}
models = ['P32R MC','P32S','P32R','P42M']
authors = ['Хованский Е.','Рудаков А.','Галкин И.','Вершинин С.','Гарейс А.',
           'Мирошниченко А.','Дюбенок И.','Каширский А.']
turns = ['C','A']
areas = ['1insp','QRR','IZ','Trigo','BS VES','SCRAP','T2','T1','BS L1SA','SHORT VES','BS L2SA']

lists = {'model' : models,
           'author' : authors,
           'turn' : turns,
           'area' : areas}

part_num = ['part_name','iln','cut_off_vin', 'creator']

parties = {
    '803201KK2A' : ['HLDR ASSY-DOOR GLASS,RH', 'NMUK', 'NIFCO UK LIMITED'],
    '960334CE0A' : ['AIR SPOILER ASSY-RR,LH', 'NCIC SHANGHAI', 'JIAXING MINSHENG AUTOMOTIVE PARTS.LTD.'],
    '82901HZ30A' : ['FIN ASSY-RR DOOR LH', 'LOCAL', 'GRUPO ANTOLIN SAN-PETERBURGO'],
    '908904EM1A' : ['EMBLEM-BACK DOOR','NCIC', 'GUANGZHOU	SWELL MARUI(GUANGZHOU) AUTOMOBILE PARTS'],
    '72700BM90B' : ['GLASS ASSY-WS','LOCAL', 'AGC BOR GLASSWORKS'],
    '833134EA0A' : ['GLASS-SIDE WDW,LH','NMUK','PILKINGTON AUTOMOTIVE-UK LTD'],
    '80200BM90A' : ['SASH COMPL-FR DOOR,RH','LOCAL','SNOP RUS LLC'],
    '260604EH1A' : ['LAMP ASSY-HEAD,RH','NMUK','Koito Europe NV'],
    '72700HZ40A' : ['GLASS ASSY-WS','LOCAL','AGC BOR GLASSWORKS'],
    '75111HX80A' : ['MBR ASSY-FR SIDE,LH','LOCAL','PETERFORM LLC'],
    '24012HZ30D' : ['HARN-ENG ROOM','LOCAL','LLC LEONI WIRING SYSTEMS ZAVOLZHIE'],
    '963026FL5A' : ['MIRROR ASSY-DOOR,LH','NML KYUSHU','SMR POONG JEONG AUTOMOTIVE MIRRORS KOREA'],
    '833124EA0A' : ['GLASS-SIDE WDW,RH','NMUK','PILKINGTON AUTOMOTIVE-UK LTD'],
    '75111HX80A' : ['MBR ASSY-FR SIDE,LH','LOCAL','PETERFORM LLC'],
    '808705BF0A' : ['MLDG ASSY-FR DOORRH','NNA','EAKAS CORPORATION'],
    '75110BN10A' : ['MBR ASSY-FR SIDE,RH','LOCAL','PETERFORM LLC']

}




class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)

        self.db_metadata = Base.metadata

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.menu_buttons = []
        self.tab_tables = TabTablesWidget()
        self.toolbar = self.addToolBar('Работа с БД')

        self.build_toolbar()
        self.build_widgets()

    def build_toolbar(self):
        """
        Создает меню с интрументами
        """
        add_action = QAction(
            QIcon('icons/baseline_add_black_48dp.png'), 'Добавить запись', self
        )
        add_action.triggered.connect(self.add_new_row)

        rm_action = QAction(
            QIcon('icons/baseline_remove_black_48dp.png'), 'Удалить запись', self
        )
        rm_action.triggered.connect(self.remove_row)


        update_action = QAction(
            QIcon('icons/baseline_cached_black_48dp.png'), 'Обновить', self
        )
        update_action.triggered.connect(self.update_table_view)

        self.toolbar.addAction(add_action)
        self.toolbar.addAction(rm_action)
        self.toolbar.addAction(update_action)

    def build_widgets(self):
        """
        Создает основные виджеты окна
        """
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.create_menu())
        splitter.addWidget(self.create_tabs_area())

        self.main_layout.addWidget(splitter)

    def create_menu(self):
        """
        Создает меню, где отображаются все таблицы БД и из которого можно
        перейти к нужной таблице для редактирования
        """
        menu = QFrame(self)
        menu.setLayout(QVBoxLayout())
        menu.setFrameShape(QFrame.StyledPanel)

        for table_name in self.db_metadata.sorted_tables:
            table_name = table_name.name
            button = QPushButton(rus[table_name].capitalize())
            button.clicked.connect(
                lambda event, name=table_name: self.tab_tables.create_tab(name)
            )
            menu.layout().addWidget(button)
        menu.layout().addStretch(len(self.menu_buttons))
        menu.setFixedWidth(menu.sizeHint().width())

        return menu

    def create_tabs_area(self):
        """
        Создает виджет, отображающий открытые для редактирования таблицы
        """
        tabs_area = QFrame(self)
        tabs_area.setLayout(QVBoxLayout())
        tabs_area.layout().addWidget(self.tab_tables)
        tabs_area.setFrameShape(QFrame.StyledPanel)

        return tabs_area

    def add_new_row(self):
        """
        Запускает диалог добавления новой записи в БД
        """
        current_widget = self.tab_tables.current_widget()
        if current_widget:
            self.dialog = DialogAddingNewRecord(current_widget.table)
            self.dialog.button_ok.clicked.connect(
                lambda: current_widget.add_new_row(self.dialog.get_values())
            )
            self.dialog.button_ok.clicked.connect(self.dialog.close)
            self.dialog.exec_()

    def remove_row(self):
        """
        Удаляет выделеную строку из таблицы
        """
        current_widget = self.tab_tables.current_widget()

        if not current_widget:
            return
        elif not current_widget.selected_cell:
            QMessageBox.warning(
                self, 'Ошибка', 'Выберите строку, которую хотите удалить',
                QMessageBox.Yes
            )
            return

        current_widget.remove_row()



    def update_table_view(self):
        """
        Обновляет данные в таблице (синхронизует таблицу с таблицей БД)
        """
        current_widget = self.tab_tables.current_widget()

        if current_widget:
            current_widget.load_data()


class DatabaseTableView(QTableWidget):
    """
    Виджет отображает данные из базы данных и работает непосредственно с БД
    """
    def __init__(self, table_name):
        super(DatabaseTableView, self).__init__()

        self.table_name = table_name
        self.db_metadata = Base.metadata
        key = str(table_name.capitalize())

        self.table = sys.modules['model'].__dict__[key]
        self.selected_cell = ()
        self.clicked.connect(self.view_clicked)

        self.setColumnCount(len(self.db_metadata.tables[table_name].columns))
        self.setHorizontalHeaderLabels(
            [rus[i.name] for i in self.db_metadata.tables[table_name].columns]
        )
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(True)

        self.load_data()

    def load_data(self):
        """
        Загружает в таблицу данные из базы данных
        """
        result = session.query(self.table)
        self.setRowCount(result.count())

        for column, data in enumerate(result.all()):
            for row, attr in enumerate(data.__table__.columns.keys()):
                self.setItem(column, row,
                             QTableWidgetItem(str(getattr(data, attr)))
                             )

        # self.setRowHeight(0, 10)

    def view_clicked(self, index_clicked):
        self.selected_cell = (index_clicked.row(), index_clicked.column())

    def add_new_row(self, values):
        """
        Добавляет в базу новую запись
        """
        if not values['id']:
            values.pop('id')

        new_record = self.table(**values)
        session.add(new_record)

        try:
            session.commit()
        except Exception:
            session.rollback()
            QMessageBox.warning(
                self, 'Ошибка', 'Ошибка добавления данных в БД',
                QMessageBox.Yes
            )
        else:
            self.load_data()

    def remove_row(self):
        """
        Удаляет из базы данных выделенную в таблице строку и удаляет
        ее из таблицы
        """
        try:
            id_row = self.item(self.selected_cell[0], 0).text()
        except AttributeError:
            message = 'Выберите строку, котору хотите удалить.'
            QMessageBox.warning(
                self, 'Ошибка', message, QMessageBox.Yes
            )
            return

        session.query(self.table).filter(self.table.id == id_row).delete()
        try:
            session.commit()
        except Exception:
            session.rollback()
            QMessageBox.warning(
                self, 'Ошибка', 'Ошибка удаления данных из БД',
                QMessageBox.Yes
            )
        else:
            self.removeRow(self.selected_cell[0])





class TabTablesWidget(QTabWidget):
    """
    Виджет для отображения таблиц из базы данных в виде вкладок
    """
    def __init__(self):
        super(TabTablesWidget, self).__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        self.all_tabs = {}

    def create_tab(self, table_name):
        """
        Добавляет в окно вкладку
        """
        if table_name in self.all_tabs:
            widget = self.all_tabs[table_name]
        else:
            widget = DatabaseTableView(table_name)
            self.all_tabs[table_name] = widget

        # Добавляем новую вкладку, если она ещё не добавлена
        for widget_index in range(self.count()):
            if self.widget(widget_index).table_name == table_name:
                self.setCurrentIndex(widget_index)
                break
        else:
            self.addTab(widget, rus[table_name].capitalize())
            self.setCurrentIndex(self.count() - 1)

    def close_tab(self, current_index):
        """
        Запускается для удаления вкладки из виджета
        """
        current_widget = self.widget(current_index)
        current_widget.hide()
        self.removeTab(current_index)

    def current_widget(self) -> DatabaseTableView:
        """
        Возвращает текущую таблицу
        """
        current_widget = self.currentWidget()

        if current_widget:
            return current_widget
        else:
            message = 'Не выбрана таблица. Откройте таблицу с которой ' \
                      'хотите работать.'
            QMessageBox.warning(
                self, 'Ошибка', message, QMessageBox.Yes
            )
            return


class DialogAddingNewRecord(QDialog):
    """
    Диалог открывающийся для добавления новой записи в БД
    """
    def __init__(self, table):
        super(DialogAddingNewRecord, self).__init__()

        self.setWindowTitle('Добавление новой записи')
        self.main_layout = QGridLayout(self)
        self.button_ok = QPushButton('Ok')
        self.button_cancel = QPushButton('Отмена')
        self.button_cancel.clicked.connect(self.close)
        self.fields = {}

        self.table = table

        self.build_widgets()

    def build_widgets(self):
        """
        Создает все виджеты отображаемые в диалоге
        """
        columns = self.table.__table__.columns.keys()

        for row, column_name in enumerate(columns):
            label = QLabel(rus[column_name] + ':')
            line_edit = QLineEdit()
            combo = QComboBox()
            self.main_layout.addWidget(label, row, 0)
            if column_name in lists.keys():
                combo.addItems(lists[column_name])
                self.main_layout.addWidget(combo, row, 1)
                self.fields[column_name] = [label, combo]
            else:
                if column_name == 'date':
                    line_edit = QLineEdit(text =str(datetime.date.today()))
                    self.main_layout.addWidget(line_edit, row, 1)
                    self.fields[column_name] = [label, line_edit]
                else:
                    if column_name in part_num:
                        line_edit = QLineEdit(text='---------', readOnly=True)
                        self.main_layout.addWidget(line_edit, row, 1)
                        self.fields[column_name] = [label, line_edit]
                    else:
                        if column_name == 'id':
                            line_edit = QLineEdit(readOnly=True)
                            self.main_layout.addWidget(line_edit, row, 1)
                            self.fields[column_name] = [label, line_edit]
                        else:
                            self.main_layout.addWidget(line_edit, row, 1)
                            self.fields[column_name] = [label, line_edit]
        self.main_layout.addWidget(self.button_ok, len(columns), 0)
        self.main_layout.addWidget(self.button_cancel, len(columns), 1)

    def get_values(self):
        """
        Возвращает данные введеные пользователем в поля
        """
        n = {}
        for i in self.fields.items():
            try:
                if i[0] == 'part_number_id':
                    if str(i[1][1].text()) in parties.keys():
                        n['part_number_id'] = i[1][1].text()
                        n['part_name'] = parties[i[1][1].text()][0]
                        n['iln'] = parties[i[1][1].text()][1]
                        n['creator'] = parties[i[1][1].text()][2]
                        break
                else:
                    n[i[0]] =  i[1][1].text()
            except AttributeError:
                n[i[0]] = i[1][1].currentText()

        return n


def create_db_session() -> Session:
    """
    Создает сессию работы с БД
    """
    engine = create_engine(DATABASE_URL)
    new_session = sessionmaker(bind=engine)
    return new_session()


def create_sql_logger():
    """
    Создает логгер записывающий все выполняющиеся sql запросы
    """
    logging.basicConfig()
    sql = logging.getLogger('sqlalchemy.engine')
    sql.setLevel(logging.INFO)

    handler = logging.FileHandler(os.path.join(BASE_PATH, 'sql-query-log.log'))
    handler.setLevel(logging.INFO)
    sql.addHandler(handler)


session = create_db_session()
create_sql_logger()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.setWindowTitle('База Данных Nissan')
main_window.setGeometry(0, 0, 700, 400)
main_window.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
