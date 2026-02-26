import sys, os
from db import DatabaseManager
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout,
 QPushButton)
from PyQt6.QtGui import  QIcon
from tasks_view import TasksView
from pomodoro_view import PomodoroView
#from analytics_view import AnalyticsView
from resource_path import resource_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Tivitapp")
        self.setWindowIcon(QIcon(resource_path("assets/logo.ico")))
        #Main widget and layout
        
        self._main_layout : QVBoxLayout = QVBoxLayout()
        self._main_layout.setContentsMargins(0,0,0,0)
        self._main_layout.setSpacing(0)

        self._main_widget : QWidget = QWidget()
        self._main_widget.setLayout(self._main_layout)
        self.setCentralWidget(self._main_widget)

        #Set size of window
        self._set_properties()
        #Set the nav bar
        self._set_menu_bar()

        #Database
        self._database = DatabaseManager()

        #Set the tabs and windows
        
        self._tasks_view = TasksView(self._database)
        self._pomodoro_view = PomodoroView(self._database)
        #self._analytics_view = AnalyticsView(self._database)

        self._pomodoro_view.setHidden(True)
        

        self._main_layout.addWidget(self._tasks_view)
        self._main_layout.addWidget(self._pomodoro_view)

        self._current_tab : QWidget = self._tasks_view
        self._current_tab_button : QPushButton 
        #Apply QSS
        self._apply_styles()


    def _set_properties(self):
        #Max dimensions
        self.setMaximumWidth(1280)
        self.setMaximumHeight(720)

        # Min dimensions
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
    
    def _set_menu_bar(self):
        self._menu_bar : QWidget = QWidget()
        self._menu_bar.setObjectName("nav_bar")
        self._menu_bar.setFixedHeight(60)


        self._menu_bar_layout : QHBoxLayout = QHBoxLayout()
        self._menu_bar.setLayout(self._menu_bar_layout)

        self._tasks_view_button : QPushButton = QPushButton("Tasks")
        self._tasks_view_button.setObjectName("active_tab") # Tasks is the default, active tab.
        self._tasks_view_button.pressed.connect(lambda: self.show_tab(self._tasks_view, self._tasks_view_button))
        self._current_tab_button = self._tasks_view_button # Default

        self._pomodoro_view_button : QPushButton = QPushButton("Pomodoro")
        self._pomodoro_view_button.setObjectName("inactive_tab")
        self._pomodoro_view_button.pressed.connect(lambda: self.show_tab(self._pomodoro_view, self._pomodoro_view_button))

        self._analytics_view_button : QPushButton = QPushButton("Analytics")
        self._analytics_view_button.setObjectName("inactive_tab")
        #self._analytics_view_button.pressed.connect(lambda: self.show_tab(self._analytics_view, self._analytics_view_button))

        self._files_view_button : QPushButton = QPushButton("Files")
        self._files_view_button.setObjectName("inactive_tab")
        #self._files_view_button.pressed.connect(lambda: self.show_tab(self))

        self._chatbot_view_button : QPushButton = QPushButton("Chatbot")
        self._chatbot_view_button.setObjectName("inactive_tab")
        #self._chatbot_view_button.pressed.connect(lambda: self.show_tab(self))

        self._config_open_button : QPushButton = QPushButton("")

        self._menu_bar_layout.addWidget(self._tasks_view_button)
        self._menu_bar_layout.addWidget(self._pomodoro_view_button)
        self._menu_bar_layout.addWidget(self._analytics_view_button)
        self._menu_bar_layout.addWidget(self._chatbot_view_button)
        self._menu_bar_layout.addWidget(self._files_view_button)
       

        self._main_layout.addWidget(self._menu_bar)
        
    def show_tab(self, tab, button: QWidget):
        self._current_tab_button.setObjectName("inactive_tab")
        self._current_tab.setHidden(True)
        #Re-style the old button
        self.style().unpolish(self._current_tab_button)
        self.style().polish(self._current_tab_button)

        button.setObjectName("active_tab")
        tab.setHidden(False)

        self._current_tab = tab
        self._current_tab_button = button

        #Re-style the new button
        self.style().unpolish(self._current_tab_button)
        self.style().polish(self._current_tab_button)

    def closeEvent(self, a0):
        self._pomodoro_view.save_activity_to_db()
        super().closeEvent(a0)

    def _apply_styles(self):
        self.setStyleSheet("""
            /* NAVIGATION BAR CONTAINER */
            QWidget#nav_bar {
                background-color: #94B0D0; 
                border-bottom: 1px solid #7F9bb9;
            }

            /* SCOPED BUTTONS: Only affect buttons INSIDE the navbar */
            QWidget#nav_bar QPushButton {
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                border: none;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                padding: 10px 30px;
                min-width: 80px;
            }

            /* INACTIVE TABS */
            QWidget#nav_bar QPushButton#inactive_tab {
                background-color: transparent;
                color: #E0E8F0;
                font-weight: normal;
                margin-top: 6px; 
            }
            QWidget#nav_bar QPushButton#inactive_tab:hover {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
            }

            /* ACTIVE TAB */
            QWidget#nav_bar QPushButton#active_tab {
                background-color: #F4F7FA; 
                color: #333333;
                font-weight: bold;
                margin-top: 0px; 
            }
        """)




if __name__ == "__main__":
    app =  QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()


   

    app.exec()
    
