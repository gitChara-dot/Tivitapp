import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QLayout, QWidget, QVBoxLayout,QHBoxLayout, QGridLayout
from PyQt6.QtWidgets import QLabel,QLineEdit, QPushButton, QDateEdit, QScrollArea, QCheckBox
from PyQt6.QtGui import QAction, QMouseEvent
from PyQt6.QtCore import QSize, QEvent, QDate
import sqlite3 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Tivitapp")
        #Main widget and layout
        
        self.main_layout : QVBoxLayout = QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.main_widget : QWidget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        #Set size of window
        self._set_properties()
        #Set the nav bar
        self._set_menu_bar()


        #Set the tabs and windows
        self._tasks_view = TasksView()
        self.main_layout.addWidget(self._tasks_view)
        
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
        self._menu_bar.setObjectName("barra_navegacion")
        self._menu_bar.setFixedHeight(60)


        self._menu_bar_layout : QHBoxLayout = QHBoxLayout()
        self._menu_bar.setLayout(self._menu_bar_layout)

        self.tasks_view_button : QPushButton = QPushButton("Tasks")
        self.tasks_view_button.setObjectName("active_tab") # Tasks is the default, active tab.
        self.pomodoro_view_button : QPushButton = QPushButton("Pomodoro")
        self.pomodoro_view_button.setObjectName("inactive_tab")
        self.files_view_button : QPushButton = QPushButton("Files")
        self.files_view_button.setObjectName("inactive_tab")
        self.chatbot_view_button : QPushButton = QPushButton("Chatbot")
        self.chatbot_view_button.setObjectName("inactive_tab")

        self._menu_bar_layout.addWidget(self.tasks_view_button)
        self._menu_bar_layout.addWidget(self.pomodoro_view_button)
        self._menu_bar_layout.addWidget(self.files_view_button)
        self._menu_bar_layout.addWidget(self.chatbot_view_button)

        self.main_layout.addWidget(self._menu_bar)
        

    
    def _apply_styles(self):
      self.setStyleSheet("""
            
            QWidget#barra_navegacion {
                background-color: #94B0D0; 
                border-bottom: 1px solid #7F9bb9;
            }

            
            QPushButton {
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                border: none;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                padding: 10px 30px;
                min-width: 80px;
            }

            
            QPushButton#inactive_tab {
                background-color: transparent;
                color: #E0E8F0;
                font-weight: normal;
                margin-top: 6px; 
            }
            QPushButton#inactive_tab:hover {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
            }

            
            QPushButton#active_tab {
                background-color: #F4F7FA; /* Mismo color que el fondo de TasksView */
                color: #333333;
                font-weight: bold;
                margin-top: 0px; 
            }
        """)

        
class TasksView(QWidget):
    def __init__(self):
        super().__init__()

        self._main_layout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self._main_layout)

        self._tasks : dict[int, tuple[str,QWidget]] = {} # Save id and (name and widget) of task
        self._tasks_number : int = 0 # Number of tasks

        self._checked_tasks : list = [] # Tasks with checked checkboxes
        self._setup_ui()
        self._setup_button_actions()
        self._apply_styles()


    

    def _setup_ui(self):
        #Scroll area instancing
        self._scroll_area : QScrollArea = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area_layout : QVBoxLayout = QVBoxLayout()

        self.task_ui : QVBoxLayout = QVBoxLayout()
        self._task_widget : QWidget = QWidget()
        self._task_widget.setLayout(self.task_ui)

        #Headers widget and layout configuration. This will be on top of each task
        self._task_ui_headers : QWidget = QWidget()
        self._task_ui_headers_layout : QGridLayout = QGridLayout()
        self._task_ui_headers.setLayout(self._task_ui_headers_layout)

        #Title and headers
        self._task_ui_task_select_header : QLabel = QLabel("Select")
        self._task_ui_task_name_header : QLabel = QLabel("Tasks Details")
        self._task_ui_task_deadline_header : QLabel = QLabel("Deadline")
        self._task_ui_task_id_header : QLabel = QLabel("Task ID")

        #Adding the labels to their parent
        self._task_ui_headers_layout.addWidget(self._task_ui_task_select_header, 0, 0)
        self._task_ui_headers_layout.addWidget(self._task_ui_task_id_header, 0, 1)
        self._task_ui_headers_layout.addWidget(self._task_ui_task_name_header, 0 , 2)
        self._task_ui_headers_layout.addWidget(self._task_ui_task_deadline_header, 0, 3)
        

        
        #sub-layout to let the add task button and the enter task box be in the same height
        self._add_task_layout : QHBoxLayout = QHBoxLayout()

        #Set up the widget and layout for the entry of the task
        self._add_task_field_widget : QWidget = QWidget()
        self._add_task_field_widget.setLayout(self._add_task_layout)

        #Set up the field to input and retrieve text
        self._add_task_text : QLineEdit = QLineEdit()
        self._add_task_text.setPlaceholderText("Enter task name")
        
        #Set up the date editor 
        self._deadline_checklist : QCheckBox = QCheckBox() # This allows for optional deadline
        self._deadline_checklist.toggled.connect(self._change_deadline_button)
        self._add_task_deadline : QDateEdit = QDateEdit()
        self._add_task_deadline.setMinimumDate(QDate.currentDate())
        self._add_task_deadline.setDisabled(True) # Starts disabled by default
        

        self._add_task_button : QPushButton = QPushButton("Enter")
        
        #Adding all the widgets of the add task interface to its layout
        self._add_task_layout.addWidget(self._add_task_text)
        self._add_task_layout.addWidget(self._deadline_checklist)
        self._add_task_layout.addWidget(self._add_task_deadline)
        self._add_task_layout.addWidget(self._add_task_button)
        
        #Adding the current tasks area to the scrollable area
        self._scroll_area.setWidget(self._task_widget)

        ### Select all task button. It's invisible until first task created
        self._select_all_tasks_button : QPushButton = QPushButton("Select All")
        self._select_all_tasks_button.setVisible(False)

        ### EDE Bottom controls: Edit, Delete and Export
        #Container widget and layout
        self._control_container_widget : QWidget = QWidget()
        self._control_container_layout : QHBoxLayout = QHBoxLayout()
        self._control_container_widget.setLayout(self._control_container_layout)

        #Creating and configurating the control buttons
        self._edit_task_button : QPushButton = QPushButton("Edit")
        self._edit_task_button.clicked.connect(self._edit_task)
        self._delete_task_button : QPushButton = QPushButton("Delete")
        self._delete_task_button.clicked.connect(self._delete_task)
        self._export_task_button : QPushButton = QPushButton("Export")
        self._export_task_button.clicked.connect(self._export_task)

        #Add the buttons to the widget
        self._control_container_layout.addWidget(self._edit_task_button)
        self._control_container_layout.addWidget(self._delete_task_button)
        self._control_container_layout.addWidget(self._export_task_button)


        #Adding the scroll area, the headers, the controls and creation menu to the main, parent layout
        self._main_layout.addWidget(self._add_task_field_widget)
        self._main_layout.addWidget(self._task_ui_headers)
        self._main_layout.addWidget(self._select_all_tasks_button)
        self._main_layout.addWidget(self._scroll_area)
        self._main_layout.addWidget(self._control_container_widget)
        
      

    
    def _setup_button_actions(self):
        self._add_task_button.clicked.connect(self._create_task)
        self._select_all_tasks_button.clicked.connect(self._check_all)
    def _change_deadline_button(self):
        if(self._deadline_checklist.isChecked()):
            self._add_task_deadline.setDisabled(False)
        else:
            self._add_task_deadline.setDisabled(True)
    def _create_task(self ):
        name : str = self._add_task_text.text()
        if(name):
            #Setting widget and layout for new task
            new_task_layout : QGridLayout  = QGridLayout()
            
            new_task_widget : QWidget = QWidget()
            new_task_widget.setLayout(new_task_layout)
            
            #Get the details of the task
            date : str 
            if(self._add_task_deadline.isEnabled()):
                date = self._add_task_deadline.date().toString()
            else:
                date = "No deadline"

            #Increment the number of tasks
            self._tasks_number += 1

            #Set the text to the original placeholder after entering
            self._add_task_text.setText("")
            self._add_task_text.setPlaceholderText("Enter task name")

            #Set the name of task along the id
            task_number : QLabel = QLabel(f'#{self._tasks_number}')
            task_number.setObjectName("id")
            task_name : QLabel = QLabel(name)
            task_name.setObjectName("task_name")
            task_date : QLabel = QLabel(date)
            task_date.setObjectName("task_date")
            
            #Check to select the task
            task_checklist : QCheckBox = QCheckBox()
            task_checklist.setObjectName(str(self._tasks_number))
            task_checklist.toggled.connect(lambda: self._add_checked(task_checklist))

            ## For edit task button:
            #Create the line edit and the deadline edit, invisible until edit button is pressed
            task_text_edit_field : QLineEdit  = QLineEdit()
            task_deadline_edit_field : QDateEdit = QDateEdit()
            task_confirm_edit_button : QPushButton = QPushButton("Confirm")


            task_text_edit_field.setObjectName("input_task_name")
            task_deadline_edit_field.setObjectName("date_selector")
            task_confirm_edit_button.setObjectName("enter_button")

            task_text_edit_field.setStyleSheet("""
                
                background-color: white;
                border: 2px solid #CFD9E6;
                border-radius: 10px;
                padding: 8px 10px;
                font-size: 14px;
                color: #333;
            
            
            """)
            task_deadline_edit_field.setStyleSheet("""                      
                border: 2px solid #4a90e2;
                
            """)
            task_confirm_edit_button.setStyleSheet("""
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #2c69c7);
                color: white;
                font-weight: bold;
                border-radius: 15px;
                padding: 8px 20px;
                border: none;
            """)

            task_text_edit_field.setPlaceholderText("Set your new text here")
            task_text_edit_field.setVisible(False)

            
            task_deadline_edit_field.setMinimumDate(QDate.currentDate())
            task_deadline_edit_field.setVisible(False)

            
            task_confirm_edit_button.setVisible(False)

            
            #add the widgets to the child layout then to the tasks_ui parent layout
            new_task_layout.addWidget(task_text_edit_field, 0, 0)
            new_task_layout.addWidget(task_deadline_edit_field,0,1)
            new_task_layout.addWidget(task_confirm_edit_button, 0, 2)
            new_task_layout.addWidget(task_checklist,0,0)
            new_task_layout.addWidget(task_number,0,1)
            new_task_layout.addWidget(task_name,0,2)
            new_task_layout.addWidget(task_date,0,3)
            
            

            new_task_widget.setStyleSheet("""
                 background-color: #F4F7FA;
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px;
            """)
            self.task_ui.addWidget(new_task_widget)

            #Update the dictionary
            name_id_tuple : tuple[str, QWidget] = (name, new_task_widget)
            self._tasks[self._tasks_number] = name_id_tuple

            #Set visible the button
            self._select_all_tasks_button.setVisible(True)
    def _add_checked(self, object: QCheckBox ):
        name = object.objectName()
        id = int(name)
        if(object.isChecked()):
            self._checked_tasks.append(id)
        else:
            if id in self._checked_tasks:
                self._checked_tasks.remove(id)
        print(self._checked_tasks)
    def _check_all(self):
        new_checked : int = 0
        for id in self._tasks:
            if(id not in self._checked_tasks):
                checkbox = self._tasks[id][1].findChild(QCheckBox)
                checkbox.toggle()
                new_checked += 1
        if(new_checked == 0): # If none were checked, all are checked, thus they must be unchecked.
            for id in self._tasks:
                checkbox = self._tasks[id][1].findChild(QCheckBox)
                checkbox.toggle()
                
    def _edit_task(self):
        if(self._checked_tasks):
            for id in self._checked_tasks:
                
                widget = self._tasks[id][1]
                self._is_editing(True, id)
                confirm_button = widget.findChild(QPushButton)
                confirm_button.clicked.connect(lambda _, task_id=id: self.confirm_edit(task_id))

    def confirm_edit(self, id: int):
        widget = self._tasks[id][1]

        self._is_editing(False, id)
        new_name = widget.findChild(QLineEdit, "input_task_name").text()
        new_date = widget.findChild(QDateEdit, "date_selector").text()

        label = widget.findChild(QLabel, "task_name")
        date = widget.findChild(QLabel, "task_date")
        label.setText(new_name)
        date.setText(new_date)

    def _is_editing(self, is_visible: bool, id):
        #If true, hide all labels and show the editing controls.
        widget = self._tasks[id][1]
        editing_obj_names = ["input_task_name", "date_selector","enter_button"]        
        children_widgets = widget.children()
                
        for children_widget in children_widgets:
            if(children_widget.isWidgetType()):
                obj_name = children_widget.objectName()

                if(obj_name in editing_obj_names):
                    children_widget.setVisible(is_visible)
                else:
                    children_widget.setVisible(not is_visible)
                
                






              

                



    def _delete_task(self):
        if(self._checked_tasks):
            for id in self._checked_tasks:
                #Decrease the total amount of widgets
                self._tasks_number -=1

                #Extract the name and the widget using the id
                name_and_widget = self._tasks[id]
                widget = name_and_widget[1]
                #Deletion
                widget.deleteLater()
                del self._tasks[id]

            #Update the checked tasks dict
            self._checked_tasks = []

            #Prepare for updating the indexes
            i : int = 1
            updated_dict : dict[int, tuple[str,str]] = {}
            for id in self._tasks:

                name_and_widget = self._tasks[id]
                updated_dict[i] = name_and_widget
                #Find the checkbox and update its object name to the new id
                checkbox = name_and_widget[1].findChild(QCheckBox)
                checkbox.setObjectName(str(i))

                #Find the label and set its text to the correct id
                old_label = name_and_widget[1].findChild(QLabel, "id")
                old_label.setText(f'#{i}')

                #Increase the number
                i+=1
            #Update the dict
            self._tasks = updated_dict
            
            

                
        
    def _export_task(self):
        pass
    def _apply_styles(self):

        # Ids for QSS
        self.setObjectName("main_window")
        self._add_task_text.setObjectName("input_task_name")
        
        self._add_task_deadline.setObjectName("date_selector")
        
        self._add_task_button.setObjectName("enter_button")
        
        # Containers
        self._task_ui_headers.setObjectName("header_container")
        self._scroll_area.setObjectName("scroll_area")
        self._task_widget.setObjectName("task_container") 
        
        # Headers 
        self._task_ui_task_select_header.setObjectName("header_text")
        self._task_ui_task_name_header.setObjectName("header_text")
        self._task_ui_task_deadline_header.setObjectName("header_text")
        self._task_ui_task_id_header.setObjectName("header_text")
        
        # Control buttons
        self._edit_task_button.setObjectName("edit_button")
        
        self._delete_task_button.setObjectName("delete_button")
        self._export_task_button.setObjectName("export_button")
        self._select_all_tasks_button.setObjectName("select_all_button")
       
        self.setStyleSheet( """ 
            
            QWidget#main_window {
                background-color: #F4F7FA;
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px;
            }

            
            QLineEdit#input_task_name, QDateEdit#date_selector {
                background-color: white;
                border: 2px solid #CFD9E6;
                border-radius: 10px;
                padding: 8px 10px;
                font-size: 14px;
                color: #333;
            }
            QLineEdit#input_task_name:focus, QDateEdit#date_selector:focus {
                border: 2px solid #4a90e2;
            }
            
            QDateEdit#date_selector:disabled{  
                color: gray
            }
            QDateEdit#date_selector::up-button,
            QDateEdit#date_selector::down-button {
                
                
                width: 15px; /* Adjust button width */
                padding: 2px; /* Spacing inside button */
            }

            
            QPushButton#enter_button, QPushButton#edit_button, 
            QPushButton#delete_button, QPushButton#export_button, QPushButton#select_all_button {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #2c69c7);
                color: white;
                font-weight: bold;
                border-radius: 15px;
                padding: 8px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #6aa9f0; 
            }
            QPushButton:pressed {
                background-color: #2a5db0;
                padding-top: 10px;
            }

            
            QWidget#header_container {
                background-color: #8FAAC9; 
                border-radius: 12px;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            QLabel#header_text {
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 5px;
                background-color: transparent; 
            }

           
            QScrollArea#scroll_area {
                
                    background-color: white;
                    border-radius: 5px;
                    border: 2px solid #4287f5;
                
            }
            QWidget#task_container {
                background-color: #F4F7FA; 
            }

            
            QCheckBox { spacing: 8px; }
            QCheckBox::indicator {
                width: 15px; height: 18px;
                border: 2px solid #97b0d1;
                border-radius: 5px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border-color: #4a90e2;
            }
        """)
        


if __name__ == "__main__":
    app =  QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()

    app.exec()
    
