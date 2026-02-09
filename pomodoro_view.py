
from db import DatabaseManager
from PyQt6.QtWidgets import (QWidget, QVBoxLayout,QHBoxLayout, QGridLayout,
QLabel,QLineEdit, QPushButton,  QScrollArea,QComboBox,QStackedWidget)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt, QTimer
import uuid
from circular_widget import CircularWidget
class PomodoroView(QWidget):  
    def __init__(self, _database):
        super().__init__()

        self._main_layout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self._main_layout)

        self._database : DatabaseManager = _database

        self._timer = QTimer()
        self._remaining_seconds = 0
        self._current_session_seconds = 0
        self._current_timer_type = ""
        self._current_session_id = str(uuid.uuid4())

        self._queue_data : list[dict] = [] # Save time and type of the timers
        self._is_queue_running : bool = False
        self._queue_position_id = 0

        self._setup_ui()
        self._apply_styles() # Apply styles at the end
        self._config_timer()
        self.load_timers_from_db()
       
    
    def _setup_ui(self):
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_widget.setLayout(content_layout)
        
        left_column_widget = QWidget()
        left_layout = QVBoxLayout()
        left_column_widget.setLayout(left_layout)

        timer_container = QWidget()
        timer_container_layout = QGridLayout()
        timer_container.setLayout(timer_container_layout)

        self._circular_timer = CircularWidget() 
        self._label_timer = QLabel("00:00:00")
        self._label_timer.setObjectName("big_timer_label") 

        timer_container_layout.addWidget(self._circular_timer, 0, 0)
        timer_container_layout.addWidget(self._label_timer, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        
        timer_buttons_layout = QHBoxLayout()
        
        self.play_and_pause_button = QPushButton("▶") 
        self.play_and_pause_button.setEnabled(False)
        self.play_and_pause_button.clicked.connect(self.pause_internal_timer)
        
        self.stop_button = QPushButton("■") 
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_internal_timer)

        self.play_and_pause_button.setObjectName("control_button") 
        
        self.stop_button.setObjectName("control_button")

        self.play_and_pause_button.setFixedSize(50, 50) 
        
        self.stop_button.setFixedSize(50, 50)

        timer_buttons_layout.addStretch()
        timer_buttons_layout.addWidget(self.play_and_pause_button)
        timer_buttons_layout.addSpacing(10)
        
        timer_buttons_layout.addSpacing(10)
        timer_buttons_layout.addWidget(self.stop_button)
        timer_buttons_layout.addStretch()

        left_layout.addStretch()
        left_layout.addWidget(timer_container, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addSpacing(30)
        left_layout.addLayout(timer_buttons_layout)
        left_layout.addStretch()

        right_column_widget = QWidget()
        right_column_widget.setObjectName("right_panel") 
        right_layout = QVBoxLayout()
        right_column_widget.setLayout(right_layout)
        
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)
        button_layout.setContentsMargins(0,0,0,0)

        # Updated: Promoted to self to allow style toggling
        self.timers_select = QPushButton("Timers")
        self.timers_select.setObjectName("active_tab") # Default Active
        self.timers_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.timers_select.clicked.connect(lambda: self._switch_page(0))

        self.queue_select = QPushButton("Queue")
        self.queue_select.setObjectName("inactive_tab") # Default Inactive
        self.queue_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.queue_select.clicked.connect(lambda: self._switch_page(1))

        button_layout.addWidget(self.timers_select)
        button_layout.addWidget(self.queue_select)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidgetResizable(True) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.stacked_widget = QStackedWidget()
        stacked_container = QWidget() 
        stacked_container.setObjectName("stack_container") 
        stacked_layout = QVBoxLayout()
        stacked_container.setLayout(stacked_layout)

        self.timers_page_widget = QWidget()
        self.timers_page_widget.setObjectName("transparent_bg")
        self.timers_page_layout = QVBoxLayout()
        self.timers_page_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 
        self.timers_page_layout.setSpacing(10) 
        self.timers_page_widget.setLayout(self.timers_page_layout)

        self.queue_page_widget = QWidget()
        self.queue_page_widget.setObjectName("transparent_bg")
        self.queue_page_layout = QVBoxLayout()
        self.queue_page_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 
        self.queue_page_widget.setLayout(self.queue_page_layout)

        start_queue_button = QPushButton("Play Queue")
        start_queue_button.clicked.connect(self._play_next_in_queue)
        start_queue_button.setObjectName("queue_add_btn")
        self.queue_page_layout.addWidget(start_queue_button)

        self.current_layout = self.timers_page_layout
        
        self.stacked_widget.addWidget(self.timers_page_widget)
        self.stacked_widget.addWidget(self.queue_page_widget)
        stacked_layout.addWidget(self.stacked_widget)
        self.scroll_area.setWidget(stacked_container)

        self.controls_container = QWidget()
        self.controls_container.setObjectName("controls_container")
        controls_layout = QHBoxLayout()
        self.controls_container.setLayout(controls_layout)
        
        self.timer_type_chooser = QComboBox()
        self.timer_type_chooser.setObjectName("timer_combo")
        self.timer_type_chooser.addItems(["Focus Time","Break"])

        self.timer_time_input = QLineEdit()
        self.timer_time_input.setObjectName("timer_input")
        minutes_validator = QIntValidator(1,1440) 
        self.timer_time_input.setValidator(minutes_validator)
        self.timer_time_input.setPlaceholderText("Min")
        self.timer_time_input.setFixedWidth(60)

        timer_add = QPushButton("Add")
        timer_add.setObjectName("action_button") 
        timer_add.clicked.connect(self._add_timer_user)

        controls_layout.addWidget(self.timer_type_chooser)
        controls_layout.addWidget(self.timer_time_input)
        controls_layout.addWidget(timer_add)

        right_layout.addWidget(button_container)
        right_layout.addWidget(self.scroll_area, stretch =1) 
        right_layout.addWidget(self.controls_container)
        
        content_layout.addWidget(left_column_widget) 
        content_layout.addWidget(right_column_widget)
        self._main_layout.addWidget(content_widget)

    def _switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        
        # Logic to toggle styles
        if index == 0:
            self.current_layout = self.timers_page_layout
            self.timers_select.setObjectName("active_tab")
            self.queue_select.setObjectName("inactive_tab")
        else:
            self.current_layout = self.queue_page_layout
            self.timers_select.setObjectName("inactive_tab")
            self.queue_select.setObjectName("active_tab")

        # Refresh styles to apply changes
        self.timers_select.style().unpolish(self.timers_select)
        self.timers_select.style().polish(self.timers_select)
        self.queue_select.style().unpolish(self.queue_select)
        self.queue_select.style().polish(self.queue_select)
    def _apply_styles(self):
        self.setStyleSheet("""
            PomodoroView {
                background-color: #F4F7FA;
            }

            /* RIGHT PANEL BACKGROUND */
            QWidget#right_panel {
                background-color: #EAF2F8; 
                border-radius: 15px;
                margin-left: 10px; 
            }

            QLabel#big_timer_label {
                font-size: 44px;
                font-weight: bold;
                color: #333;
                background-color: transparent;
            }

            QPushButton#control_button {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 25px; 
                font-size: 18px;
                color: #555;
            }
            QPushButton#control_button:hover {
                background-color: #4a90e2;
                border-color: #4a90e2;
                color: white;
            }
            QPushButton#control_button:pressed {
                background-color: #357ABD;
            }

            /* TAB BUTTONS (ACTIVE VS INACTIVE) */
            QPushButton#active_tab, QPushButton#inactive_tab {
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                padding: 8px;
                min-width: 80px;
                border: none;
            }

            QPushButton#active_tab {
                background-color: #4a90e2;
                color: white;
            }

            QPushButton#inactive_tab {
                background-color: #F4F7FA; 
                border-bottom: 2px solid #D1D9E0;
                color: #888;
            }
            QPushButton#inactive_tab:hover {
                background-color: white;
                color: #4a90e2;
            }
            QPushButton#control_tab:disabled {
                background-color: gray;
                color: darkgray;
            }
            QScrollArea#scroll_area, QWidget#stack_container, QWidget#timers_page, QWidget#queue_page, QWidget#transparent_bg {
                border: none;
                background-color: transparent;
            }

            QWidget#custom_timer {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
            
            QLabel#time_label {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                padding-left: 5px;
            }

            QPushButton#list_action_btn {
                background-color: #EEF2F6;
                color: #555;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                min-width: 50px; 
            }
            QPushButton#list_action_btn:hover {
                background-color: #DDE4EB;
                color: #333;
            }
            
            QPushButton#queue_add_btn {
                background-color: #E8F0FE;
                color: #4a90e2;
                border: 1px solid #D2E3FC;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton#queue_add_btn:hover {
                background-color: #D2E3FC;
            }

            QWidget#controls_container {
                background-color: #DDEBF7;
                border-radius: 10px;
                padding: 5px;
            }
            
            QComboBox#timer_combo, QLineEdit#timer_input {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }

            QPushButton#action_button {
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 6px 15px;
                border: none;
            }
            QPushButton#action_button:hover {
                background-color: #357ABD;
            }
        """)

    def _add_timer_user(self):
        time = self.timer_time_input.text()
        if(time ):
            text = self.timer_type_chooser.currentText()
            self.timer_time_input.clear()
            widget = self._add_timer_to_gui(time, text)
            if (widget != None and self.current_layout == self.timers_page_layout) :
                #Add to _database
                id = self._database.add_timer(text, time)
                widget.setProperty("id", id)

    def _add_timer_to_gui(self, time: str, text:str, layout = None):
        if(int(time) > 0):
            if(layout == None):
                layout = self.current_layout
            
            # Container
            container_widget : QWidget = QWidget()
            container_widget.setObjectName("custom_timer")
            container_widget.setFixedHeight(70) # Fixed height for neat rows
            

            container_layout : QHBoxLayout = QHBoxLayout() # Use HBox for simpler row alignment
            container_layout.setContentsMargins(5,5,5,5)
            container_layout.setSpacing(5)
            
            container_widget.setLayout(container_layout)
            
            # Logic
            time_val = int(time)
            hours = time_val // 60
            minutes = time_val - hours * 60
            
            # Label
            display_text = f"{minutes}m" if hours == 0 else f"{hours}h {minutes}m"
            label = QLabel(f"{display_text} {text}")
            label.setObjectName("time_label")

            # Buttons              
            start_timer_button= QPushButton("Start")
            start_timer_button.clicked.connect(lambda: self._start_timer(time_val, text ))
            start_timer_button.setObjectName("list_action_btn") # CSS ID
                
            delete_button = QPushButton("Del")
            delete_button.clicked.connect(lambda: self._delete_item(container_widget))
            delete_button.setObjectName("list_action_btn") # CSS ID

            if(not layout == self.queue_page_layout):
                add_to_queue_button = QPushButton("+ Queue")
                add_to_queue_button.clicked.connect(lambda: self._add_to_queue(time, text))
                add_to_queue_button.setObjectName("queue_add_btn") # CSS ID

            # Add to Layout
            container_layout.addWidget(label) 

            #If its not the queue page, or if its the queue page and the first item, set the start button
            if(not layout == self.queue_page_layout):
                container_layout.addWidget(start_timer_button)
                container_layout.addWidget(add_to_queue_button)

            container_layout.addWidget(delete_button)
            container_layout.addStretch()

            layout.addWidget(container_widget)
            
            if(layout == self.queue_page_layout):
                timer_data = {'time':time_val, 'type':text}
                self._queue_data.append(timer_data)

            return container_widget
        else:
            return None
    def _add_to_queue(self, time : int, text: str):
        self._add_timer_to_gui(time, text, layout=self.queue_page_layout)
    def _play_next_in_queue(self):
        if(self._queue_data):
            self._is_queue_running = True
            self._start_timer(self._queue_data[0]['time'], self._queue_data[0]['type'])
           
    def _delete_item(self, item: QWidget):
        if(self.current_layout == self.queue_page_layout):
            if(self._queue_data):
                self._queue_data.pop(self.current_layout.indexOf(item)-1) # Substract 1 to account for the extra button widget
            
                
            if(self._is_queue_running and self._queue_data): # If there's more timers, play the next
                self._play_next_in_queue()
            else:
                self.stop_internal_timer()
        else:
            id = item.property("id")
            print(id)
            self._database.delete_timer(id)
            print("borrado")

        self.current_layout.removeWidget(item)
        item.deleteLater()
    def _delete_first_in_queue(self):
        
        if(len(self._queue_data)>0):
            widget = self.queue_page_layout.itemAt(1).widget()
            if(widget.objectName() == "custom_timer"): #safety mesure
                self._delete_item(widget)
    def _start_timer(self, time_minutes:int, type : str):
        if(self._current_session_seconds > 0): #If there are seconds to save, save them to the db
            self.save_activity_to_db()

        if(self._timer.isActive()):
            self._timer.stop()

        self._current_timer_type = type
        
        

        #Change buttons to adjust 
        self.stop_button.setEnabled(True)
        self.play_and_pause_button.setEnabled(True)
        self.play_and_pause_button.setText("II")


        self._remaining_seconds = time_minutes*60
        self.max_seconds = self._remaining_seconds
        
        #Set the circular _timer back to max and get the degree per second rate
        self.degree_per_second = self._circular_timer.calc_degree_per_second(self.max_seconds)
        self._circular_timer.set_current_size(self._circular_timer.get_max_size())
        

        self._set_timer()

        if(self.current_layout == self.timers_page_layout):
            self._is_queue_running = False
            
    def _config_timer(self): #NEVER CALL MORE THAN ONCE
        self._timer.setInterval(1000)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._update_timer_label)
    def _set_timer(self):
        if(not self._timer.isActive()):
            self._timer.start()
        
    def _update_timer_label(self):
        if(self._remaining_seconds == 0):
            self._timer.stop()
            self._circular_timer.set_current_size(self._circular_timer.get_max_size())
            self._label_timer.setText("00:00:00")
            self.stop_button.setEnabled(False)
            self.play_and_pause_button.setEnabled(False)

            if(self._is_queue_running):
                self._delete_first_in_queue()
            
            self.save_activity_to_db()
                
            return 
        else:
            self._remaining_seconds -= 1

        hours = self._remaining_seconds // 3600 
        minutes = (self._remaining_seconds % 3600 )//60
        seconds = self._remaining_seconds % 60
    

        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self._label_timer.setText(time_text)

        #Update the circle of the _timer
        self._circular_timer.decrease_size(self.degree_per_second)

        #Update the current session time
        self._current_session_seconds += 1

    def pause_internal_timer(self):
        if(self._timer.isActive()):
            self._timer.stop()
            self.play_and_pause_button.setText("▶")
        else:
            if(self._remaining_seconds>0):
                self.play_and_pause_button.setText("II")
                self._set_timer()
                
    
    def stop_internal_timer(self):
        if(self._remaining_seconds>0):

            if(self._is_queue_running):
                self._is_queue_running = False
                
            #Stop the qtimer
            self._timer.stop()
            #Set the seconds to 0 and update the label
            self._remaining_seconds = 0
            self._update_timer_label()

            #Change the visuals of the play button
            self.play_and_pause_button.setText("▶")
            self.play_and_pause_button.setEnabled(False)

            

            
    
    def save_activity_to_db(self):
        if(self._current_timer_type and self._current_session_seconds > 0):
            self._database.log_activity(self._current_timer_type, self._current_session_seconds, self._current_session_id)
            self._current_session_seconds = 0
        



    def remove_timer_from_db(self, id):
        self._database.delete_timer(id)
    
    def add_timer_to_db(self, type: str, length :int):
        self._database.add_timer(type, length)
    def load_timers_from_db(self):
        timers = self._database.get_timers()

        if(timers):
            for _timer in timers:
                id, type, length = _timer
                widget = self._add_timer_to_gui(length, type, layout=self.timers_page_layout)

                if(widget != None):
                    widget.setProperty("id",id)