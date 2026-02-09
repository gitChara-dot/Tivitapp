
from db import DatabaseManager
from PyQt6.QtWidgets import (QWidget, QVBoxLayout,QHBoxLayout, QGridLayout,
QLabel,QLineEdit, QPushButton, QDateEdit, QScrollArea, QCheckBox, QComboBox, QFileDialog, QMessageBox,
 QSizePolicy, QStackedWidget, QTableWidget, QHeaderView)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QDate, Qt
from task_pdf_generator import TaskPDFGenerator


class TasksView(QWidget):
    def __init__(self, _database: DatabaseManager):
        super().__init__()

        self._main_layout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self._main_layout)

        self._tasks : dict[int, tuple[str,QWidget]] = {} # Save id and a tuple with name and widget of the task
        self._tasks_details : dict[int, list] = {} # Access tasks details list using ID. List order is: Task name, deadline, priority, state.
        self._tasks_rows: dict[int, int] = {} # Get the row position with the id. 
 

        self._completed_tasks : list[int] = []
        self._checked_tasks : list = [] # Tasks with checked checkboxes
        self._editing_tasks : list = [] # Tasks currently being edited

        self._setup_ui()
        self._setup_button_actions()
        self._apply_styles()

        self._database =  _database
        self.load_tasks_from_db()

    def load_tasks_from_db(self):
        tasks_list = self._database.get_tasks()
        
        if(tasks_list):
            for task in tasks_list:
                id, name, deadline, priority, state = task # Unpacking

                if(name):
                    
                    self._add_task_to_ui(id, name, deadline, priority, state)
                    if(state == "Completed"):
                        self._completed_tasks.append(id)
                        self._mark_task_as_completed(id, True)
                    else:
                        self._mark_task_as_completed(id, False)
                else:
                    self._database.delete_task(id) #If name is blank, delete it
   
    
    def _setup_ui(self):
        #Scroll area instancing
        self._scroll_area : QScrollArea = QScrollArea()
        self._scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area_layout : QVBoxLayout = QVBoxLayout()

        self.task_ui : QVBoxLayout = QVBoxLayout()
        self._task_widget : QWidget = QWidget()
        self._task_widget.setLayout(self.task_ui)
        
        self._main_table = QTableWidget(0, 5)
        self._main_table_layout = QHBoxLayout()

        labels = ["Select", "Task Details", "Deadline", "Priority", "State"]
        
        #Set them on the table
        self._main_table.setHorizontalHeaderLabels(labels)

        #Hide numeration and config
        self._main_table.verticalHeader().setHidden(True) 
        self._main_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._main_table.setAlternatingRowColors(True) # Alternating colors
        self._main_table.verticalHeader().setDefaultSectionSize(50) # Row height
        
        
        header = self._main_table.horizontalHeader()
        
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._main_table.setColumnWidth(0,75)
        self._main_table.setColumnWidth(3,75)
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
        self._add_task_deadline.setCalendarPopup(True)
        self._add_task_deadline.setDisabled(True) # Starts disabled by default
        
        #Priority selector
        self._priority_label : QLabel = QLabel("Priority: ")
        self._priority_selector : QComboBox = QComboBox()
        priority_choices : list = ["Low", "Medium", "High", "Urgent"]
        self._priority_selector.addItems(priority_choices)

        self._add_task_button : QPushButton = QPushButton("Enter")
        
        #Adding all the widgets of the add task interface to its layout
        self._add_task_layout.addWidget(self._add_task_text)
        self._add_task_layout.addWidget(self._deadline_checklist)
        self._add_task_layout.addWidget(self._add_task_deadline)
        self._add_task_layout.addWidget(self._priority_label)
        self._add_task_layout.addWidget(self._priority_selector)
        self._add_task_layout.addWidget(self._add_task_button)
        
        
        #Adding the current tasks area to the scrollable area
        self._scroll_area.setWidget(self._task_widget)

        ### Select all task button. It's invisible until first task created
        self._select_all_tasks_button : QPushButton = QPushButton("Select All")
        self._select_all_tasks_button.setVisible(False)

        ### EDECS Bottom controls: Edit, Delete, Export, Change State
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
        self._main_layout.addWidget(self._select_all_tasks_button)
        self._main_layout.addWidget(self._main_table)
        self._main_layout.addWidget(self._control_container_widget)
    def _add_task_to_ui(self, task_id, name, date, chosen_priority, state):
        

        #Setting widget and layout for new task
        new_task_layout : QGridLayout  = QGridLayout()
        
        new_task_widget : QWidget = QWidget()
        new_task_widget.setLayout(new_task_layout)
        ###Set the task parameters
        #Name/Detail of the task label
        task_name : QLabel = QLabel(name)
        task_name.setObjectName("task_name")
        
        #Deadline
        task_date : QLabel = QLabel(date)
        task_date.setObjectName("task_date")

        #Priority label
        task_priority : QLabel = QLabel()
        task_priority.setObjectName("task_priority")
        task_priority.setScaledContents(True) 
        task_priority.setFixedSize(45,45)
      
        #State label, txt only
        task_state : QLabel = QLabel(state)
        task_state.setObjectName("task_state")

        #We can set the alignment of the text-only labels without container
        labels_to_center = [task_date, task_state]
        for label in labels_to_center:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        #Check to select the task
        task_checklist : QCheckBox = QCheckBox()
        task_checklist.setObjectName(str(task_id))
        task_checklist.toggled.connect(lambda: self._add_checked(task_checklist))

        ## For edit task button:
        #Create the edit controls that will go below the corresponding labels.
        #Each field is hidden using a QStackedWidget, and it's only shown when the user presses edit on a task.
        task_text_edit_field : QLineEdit  = QLineEdit()
        task_text_edit_field.editingFinished.connect(lambda: self._confirm_edit(task_id, 1)) # Give the column position
        task_text_edit_field.setPlaceholderText("Set your new task here")

        task_deadline_edit_field : QDateEdit = QDateEdit()
        task_deadline_edit_field.setSpecialValueText("No deadline")
        task_deadline_edit_field.setCalendarPopup(True)
        task_deadline_edit_field.setMinimumDate(QDate.currentDate())
        task_deadline_edit_field.editingFinished.connect(lambda: self._confirm_edit(task_id, 2))
        
        task_priority_edit_field : QComboBox = QComboBox()
        priority_choices : list = ["Low", "Medium", "High", "Urgent"]
        task_priority_edit_field.addItems(priority_choices)
        task_priority_edit_field.activated.connect(lambda: self._confirm_edit(task_id, 3))

        task_state_edit_field : QComboBox = QComboBox()
        state_choices : list = ["Not Started", "Started", "Completed"]
        task_state_edit_field.addItems(state_choices)
        task_state_edit_field.activated.connect(lambda: self._confirm_edit(task_id, 4))

        task_text_edit_field.setObjectName("input_task_name")
        task_deadline_edit_field.setObjectName("date_selector")
        task_priority_edit_field.setObjectName("priority_selector")
        task_state_edit_field.setObjectName("state_selector")

        self._main_table.insertRow(self._main_table.rowCount())
        current_row = self._main_table.rowCount()-1

        #Create stacked widgets to allow swapping between widgets and edit lines
        stacked_name_widget = QStackedWidget()
        stacked_name_widget.addWidget(task_name)
        stacked_name_widget.addWidget(task_text_edit_field)

        

        stacked_date_widget = QStackedWidget()
        stacked_date_widget.addWidget(task_date)
        stacked_date_widget.addWidget(task_deadline_edit_field)

        stacked_priority_widget = QStackedWidget()
        stacked_priority_widget.addWidget(task_priority)
        stacked_priority_widget.addWidget(task_priority_edit_field)

        stacked_state_widget = QStackedWidget()
        stacked_state_widget.addWidget(task_state)
        stacked_state_widget.addWidget(task_state_edit_field)
    

        self._main_table.setCellWidget(current_row,0, task_checklist)
        self._main_table.setColumnWidth(0, 30)
        self._main_table.setCellWidget(current_row,1, stacked_name_widget)
        self._main_table.setCellWidget(current_row,2, stacked_date_widget)
        self._main_table.setCellWidget(current_row,3, stacked_priority_widget)
        self._main_table.setCellWidget(current_row,4, stacked_state_widget)
        
  

        ###Update the dictionaries
        #Save the name and the widget of the widget
        name_widget_tuple : tuple[str, QWidget] = (name, new_task_widget)
        self._tasks[task_id] = name_widget_tuple

        #Save the details of the widget as text
        details : list = [task_name.text(), task_date.text(), chosen_priority,task_state.text()]
        self._tasks_details[task_id] = details

        #Save the row with the id
        self._tasks_rows[task_id] = current_row

        #Set visible the button
        self._select_all_tasks_button.setVisible(True)
    def _setup_button_actions(self):
        self._add_task_button.clicked.connect(self._create_task)
        self._select_all_tasks_button.clicked.connect(self._check_all)
    def _change_deadline_button(self):
        if(self._deadline_checklist.isChecked()):
            self._add_task_deadline.setDisabled(False)
        else:
            self._add_task_deadline.setDisabled(True)

        
    def _create_task(self):
        name : str = self._add_task_text.text()
        if(name):

            
            #Get the details of the task
            date : str 
            if(self._add_task_deadline.isEnabled()):
                date = self._add_task_deadline.text()
            else:
                date = "No deadline"

            #Get the priority
            chosen_priority = self._priority_selector.currentText()
           
            
            #Set the text to the original placeholder after entering
            self._add_task_text.setText("")
            self._add_task_text.setPlaceholderText("Enter task name")

            

            #Add to _database and get unique ID (UID)
            unique_id = self._database.add_task(name, date, chosen_priority, "Not Started")
            
            self._add_task_to_ui(unique_id, name, date, chosen_priority, "Not Started")

            
    def _add_checked(self, object: QCheckBox ):
        name = object.objectName()
        id = int(name)
        if(object.isChecked()):
            self._checked_tasks.append(id)
        else:
            if id in self._checked_tasks:
                self._checked_tasks.remove(id)
        
    def _check_all(self):
        new_checked : int = 0
        for id in self._tasks:
            if(id not in self._checked_tasks):
                row = self._tasks_rows[id]
                checkbox = self._main_table.cellWidget(row, 0)
                checkbox.toggle()
                new_checked += 1
        if(new_checked == 0): # If none were checked, that means all are checked. Then, every task is unchecked.
            for id in self._tasks:
                row = self._tasks_rows[id]
                checkbox = self._main_table.cellWidget(row, 0)
                checkbox.toggle()

    def update_tasks_database(self,id):
        task_data = self._tasks_details[id]
        self._database.update(task_data[0], task_data[1], task_data[2], task_data[3], id)




    def _edit_task(self):
        if(self._checked_tasks):
            #Handle checked tasks
            for id in self._checked_tasks:
                #Find tasks not being edited already and that aren't completed
                if(id not in self._editing_tasks):
                   
                    self._editing_tasks.append(id) #Set as currently being edited
                    self._is_editing(True, id) # Hide corresponding labels
                else:
                    self._is_editing(False, id) #if pressed edit and already editing, hide edit controls on that task


    def _confirm_edit(self, id, position):
        row = self._tasks_rows[id]
        stacked_widget = self._main_table.cellWidget(row, position)
        if(isinstance(stacked_widget, QStackedWidget)): #Safety measures
            edit_widget = stacked_widget.currentWidget()
            if(isinstance(edit_widget, QComboBox)):
                new_text = edit_widget.currentText()
            else:
                new_text = edit_widget.text()
            
            self._tasks_details[id][position-1] = new_text 
            if(position == 4 and new_text == "Completed"):
                self._completed_tasks.append(id)

           
            ### Clarification:
            #Since tasks_details and the edit widgets are in the same order: Task name, date, priority and state, we can update
            #the task details freely.

            stacked_widget.setCurrentIndex(0)
            widget_to_edit = stacked_widget.currentWidget()
            #In case of the priority label, we change it's pixmap instead. If its the date, we get the plain text
            if(position == 3):
                widget_to_edit.setPixmap(QPixmap(f"assets/{new_text}.png"))
            else:
                if(new_text):
                    widget_to_edit.setText(new_text)

           

            self.update_tasks_database(id)    
        else: #In case of a fatal error of encountering a non-stacked widget, cancel edits.
            self._is_editing(False, id)
            pass
        
        if(id in self._completed_tasks):
            still_editing = False
            for i in range(1,5):
                stacked_widget = self._main_table.cellWidget(row, i)
                if(isinstance(stacked_widget,QStackedWidget)):
                    if(stacked_widget.currentIndex() == 1):
                        still_editing = True
                        break
                    
            if(not still_editing):
                if(self._tasks_details[id][3] == "Completed"):
                    self._mark_task_as_completed(id, True)
                else:
                    self._mark_task_as_completed(id, False)
                    if(id in self._completed_tasks):
                        self._completed_tasks.remove(id)
                       
                self._editing_tasks.remove(id)
            
    def _is_editing(self, is_editing: bool, id: int):
        #Get the row to switch the pages of the stacked widgets, allowing the user to edit the details of the task
        row = self._tasks_rows[id]
        for i in range(1,5):
            widget = self._main_table.cellWidget(row, i)
            if isinstance(widget, QStackedWidget):
                if(is_editing): # If its editing, show edit controls, if not, go back to normal.
                    widget.setCurrentIndex(1)
                else:
                    widget.setCurrentIndex(0)
                    if(self._tasks_details[id][3]  == "Completed"):
                         self._mark_task_as_completed(id, True)
                    else:
                        self._mark_task_as_completed(id, False)
                        if id in self._completed_tasks:
                            self._completed_tasks.remove(id)
                    if(id in self._editing_tasks):
                        self._editing_tasks.remove(id)
                
            

    def _delete_task(self):
        if(self._checked_tasks):
            
            ids_to_delete = sorted(self._checked_tasks, key=lambda x: self._tasks_rows[x], reverse=True)

            for id in ids_to_delete:
                
                row_deleted = self._tasks_rows[id]

                self._database.delete_task(id)

                self._main_table.removeRow(row_deleted)

                del self._tasks[id]
                del self._tasks_details[id]
                del self._tasks_rows[id]

                for tid, trow in self._tasks_rows.items():
                    if trow > row_deleted:
                        self._tasks_rows[tid] -= 1

            self._checked_tasks = []
    def _mark_task_as_completed(self, taskid: int, is_completed: bool):
        row = self._tasks_rows[taskid]
        
        # Search columns: (name, deadline, priority, state)
        for col in range(1, 5):
            stack = self._main_table.cellWidget(row, col)
            
            if isinstance(stack, QStackedWidget):
                label_widget = stack.widget(0) # Label widget is always the lowest on stack
                
                if isinstance(label_widget, QLabel):
                    # Get the original text
                    clean_text = self._tasks_details[taskid][col-1]

                    if is_completed:
                        
                        if col == 3: # Change the priority image 
                            label_widget.setPixmap(QPixmap("assets/Completed.png"))
                        else: # Texts only
   
                            label_widget.setText(f"<s>{clean_text}</s>")
                            label_widget.setStyleSheet("color: #2e7d32; font-weight: bold;") 
                    else:
                        
                        if col == 3: # Restore the priority image
                            priority_val = self._tasks_details[taskid][2]
                            label_widget.setPixmap(QPixmap(f"assets/{priority_val}.png"))
                        else: #Set the text to black 
                            label_widget.setText(clean_text)
                            label_widget.setStyleSheet("color: black; font-weight: normal;")
                        
                   
                    
    def _get_task_details(self, taskid : int):
        return self._tasks_details[taskid]
    def _export_task(self):
        if(self._checked_tasks):
            generator  =  TaskPDFGenerator()
            taskslist : dict[int, list] = {}
            for id in self._checked_tasks:
                taskslist[id] = self._get_task_details(id)

            file_filter = "Select a directory and a file name (.pdf)"
            initial_directory = QDate.currentDate().toString()+".pdf"
            directory, _ = QFileDialog.getSaveFileName(self, "Select a directory to export", filter=file_filter, directory=initial_directory)
            
            if(directory):
                generator.create_table(taskslist)
                if(directory[-4:] != ".pdf"):
                    directory+=".pdf"
                generator.output(directory)
                

                message = QMessageBox()
                message.setWindowIcon(QIcon("assets/sign_green.png"))
                message.setWindowTitle("Success!")
                message.setText("File saved succesfully at "+directory)
                message.exec()
            

            

    def _apply_styles(self):
        self.setObjectName("main_window")
        
        self._add_task_text.setObjectName("input_task_name")
        self._add_task_deadline.setObjectName("date_selector")
        self._priority_selector.setObjectName("priority_combo") 
        self._priority_label.setObjectName("priority_label")    
        self._add_task_button.setObjectName("enter_button")
        
        self._main_table.setObjectName("tasks_table")

        self._edit_task_button.setObjectName("edit_button")
        self._delete_task_button.setObjectName("delete_button")
        self._export_task_button.setObjectName("export_button")
        self._select_all_tasks_button.setObjectName("select_all_button")
        
        self.setStyleSheet(""" 
            QWidget#main_window {
                background-color: #F4F7FA;
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px;
            }

            QLineEdit#input_task_name, QDateEdit#date_selector {
                background-color: white;
                border: 1px solid #CFD9E6;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #333;
            }
            QLineEdit#input_task_name:focus, QDateEdit#date_selector:focus {
                border: 2px solid #4a90e2;
            }
            
            QComboBox#priority_combo, QComboBox#priority_selector, QComboBox#state_selector {
                background-color: white;
                border: 1px solid #CFD9E6;
                border-radius: 8px;
                padding: 5px 12px;
                color: #333;
            }
            QComboBox#priority_combo::drop-down, QComboBox#priority_selector::drop-down, QComboBox#state_selector::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none; 
                border-left: 1px solid #CFD9E6; 
            }

            QLabel#priority_label {
                font-weight: bold;
                color: #555;
                margin-right: 5px;
                margin-left: 10px;
            }

            QDateEdit#date_selector:disabled{  
                color: #999;
                background-color: #F0F2F5;
                border-color: #E0E0E0;
            }
            QDateEdit#date_selector::up-button,
            QDateEdit#date_selector::down-button {
                width: 0px; 
                padding: 0px; 
            }

            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #2c69c7);
                color: white;
                font-weight: bold;
                border-radius: 12px;
                padding: 8px 24px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6aa9f0; 
            }
            QPushButton:pressed {
                background-color: #2a5db0;
                padding-top: 10px;
            }

            QTableWidget#tasks_table {
                background-color: white;
                border: 1px solid #CFD9E6;
                border-radius: 10px;
                gridline-color: #F0F2F5;
                selection-background-color: #E8F0FE;
                selection-color: #333;
                outline: none;
            }
            
            QHeaderView::section {
                background-color: #8FAAC9;
                color: white;
                font-weight: bold;
                border: none;
                border-right: 1px solid #94B0D0;
                padding: 10px;
                font-size: 14px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }

            QCheckBox { 
                spacing: 5px; 
                margin-left: 10px;
            }
            QCheckBox::indicator {
                width: 18px; 
                height: 18px;
                border: 2px solid #CFD9E6;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border-color: #4a90e2;
            }
            QCheckBox::indicator:hover {
                border-color: #4a90e2;
            }

            QInputDialog {
                background-color: #F4F7FA;
                border: 1px solid #8FAAC9;
                border-radius: 12px;
            }
            QInputDialog QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            QInputDialog QComboBox, QInputDialog QLineEdit {
                background-color: white;
                border: 1px solid #CFD9E6;
                border-radius: 6px;
                padding: 5px;
            }

            QInputDialog QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #2c69c7);
                color: white;
                border: none;
                padding: 6px 20px;
                font-weight: bold;
                min-width: 60px;
                height: 20px;
                margin-top: 0px; 
            }
            QInputDialog QPushButton:hover {
                background-color: #6aa9f0;
            }
            QInputDialog QPushButton:pressed {
                background-color: #2a5db0;
                padding-top: 2px;
            }

            QCalendarWidget QWidget {
                alternate-background-color: #E8F0FE; 
            }
            
            QCalendarWidget QToolButton {
                color: black;
                font-weight: bold;
                icon-size: 20px;
                background-color: transparent;
            }
            
            QCalendarWidget QToolButton:hover {
                background-color: #E8F0FE;
                border-radius: 5px;
            }
            
            QCalendarWidget QMenu {
                background-color: white;
                color: black;
            }
            
            QCalendarWidget QSpinBox {
                color: black;
                background-color: white;
                selection-background-color: #4a90e2;
            }
            
            QCalendarWidget QAbstractItemView:enabled {
                color: #333;  
                background-color: white;  
                selection-background-color: #4a90e2; 
                selection-color: white; 
            }
            
            QCalendarWidget QAbstractItemView:disabled {
                color: #999;
            }
        """)
