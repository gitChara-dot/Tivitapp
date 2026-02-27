
# Tivitapp: Technical Documentation

## Module 1: Advanced Task Management System

The Task Management module in Tivitapp is engineered to handle complex user workflows by providing a high-performance, state-driven interface for daily organization. Unlike standard implementations, this module utilizes a custom synchronization logic between the graphical table and the underlying relational database.

### 1.1 Architecture & State Management

The system maintains data integrity through a triple-mapping dictionary architecture. This ensures O(1) access time for UI updates and data retrieval:

* **Task Registry (`_tasks`):** Maps unique database IDs to a tuple containing the task name and its parent QWidget.
* **Metadata Store (`_tasks_details`):** Stores a synchronized list of task attributes (Deadline, Priority, State) indexed by ID, facilitating rapid export and editing without redundant database queries.
* **Index Mapping (`_tasks_rows`):** A dynamic pointer system that tracks the physical row position of each task in the `QTableWidget`. This is crucial for maintaining functionality after batch deletions or sorting operations.

### 1.2 Inline Editing via QStackedWidget

To enhance User Experience (UX), Tivitapp implements a "non-disruptive editing" workflow. Instead of launching external dialogs, the module performs inline swaps:

* **View Mode:** Displays data using standard `QLabel` components with specific QSS styling for readability.
* **Edit Mode:** Utilizing `QStackedWidget`, the UI instantly replaces labels with interactive components (`QLineEdit`, `QDateEdit`, `QComboBox`).
* **Confirmation Logic:** Data is committed to the SQLite database only after the `editingFinished` or `activated` signals are triggered, ensuring that the persistent state always reflects the UI state.

### 1.3 The Export Engine (PDF Generation)

Tivitapp features a dedicated `TaskPDFGenerator` class, extending the `FPDF` library to produce professional productivity reports.

* **Branding & Visuals:** The engine dynamically renders headers with corporate branding and applies zebra-striping to table rows for improved legibility.
* **Iconography Integration:** The generator resolves asset paths at runtime using a specialized `resource_path` utility, embedding priority icons directly into the document.
* **Data Transformation:** It converts the internal dictionary-based task state into a structured PDF table, supporting conditional formatting (e.g., green-colored text for "Completed" status).

### 1.4 Visual Feedback and Styling

The interface uses dynamic QSS (Qt Style Sheets) to provide immediate feedback:

* **Task Completion:** Completed tasks are visually modified using HTML-based strike-through tags (`<s>`) and color-shifted to green, signaling achievement to the user.
* **Priority Hierarchy:** Uses custom assets (`Low.png` to `Urgent.png`) to provide an at-a-glance priority assessment, mimicking modern enterprise Kanban boards.

## Module 2: High-Precision Pomodoro & Focus Engine

The Pomodoro module is designed to provide a distraction-free environment while maintaining a granular log of productive time. It stands out due to its custom rendering engine and its ability to handle complex session sequences.

### 2.1 Custom Graphics with CircularWidget

Instead of using standard progress bars, Tivitapp features a custom-built circular timer. This component is a subclass of `QWidget` that utilizes the **Qt Paint Engine** for high-performance rendering.

* **Mathematical Precision:** The widget uses the `drawArc` method from `QPainter`. Since Qt measures spans in **1/16th of a degree**, the logic converts time remaining into a span of $5760$ units ($360^\circ \times 16$).
* **Dynamic UI Feedback:** The timer features a dual-layer arc system. A background "ghost" arc provides visual context of the total session length, while the foreground blue arc dynamically shrinks as time elapses, calculated by a specific `degree_per_second` rate.
* **Anti-Aliasing:** To ensure a modern and smooth aesthetic, the widget forces `RenderHint.Antialiasing`, preventing "jagged" edges on high-resolution displays.

### 2.2 Session Queue & State Machine

One of the most advanced features of the engine is the **Timer Queue**. This allows users to automate their workflow by chaining multiple intervals.

* **Sequential Logic:** The system stores a list of timer dictionaries (`_queue_data`). When a session ends, a "callback-like" logic triggers the removal of the finished task and automatically starts the next one in the sequence.
* **Internal State Tracking:** The view manages several states (Running, Paused, Stopped, and Queue-Running) to ensure that UI controls (Start/Pause/Stop buttons) respond correctly to the current context, preventing logic collisions.

### 2.3 Productivity Logging & UUIDs

To prepare for data analysis and visualization, the engine performs background logging.

* **Unique Session Identification:** Every time a timer starts, a **Version 4 UUID** is generated. This allows the system to group multiple focus intervals into a single "study session," even if the app is restarted.
* **Atomic Time Tracking:** Instead of just saving the total duration, the system tracks `_current_session_seconds`. This ensures that even if a user closes the app mid-timer, the actual time spent focusing is accurately recorded in the `activity` table of the database.
* **Database Synchronization:** Upon the `closeEvent` of the main window, the system performs a final flush of any unsaved focus time, ensuring zero data loss.


## Module 3: Data Architecture & Persistence Layer

Tivitapp implements a robust persistence layer designed to ensure data integrity and high availability across sessions. The architecture separates business logic from data access, utilizing an encapsulated Database Management system.

### 3.1 Advanced SQLite Wrapper with Context Managers

The database interaction is built upon the `sqlite3` library, but enhanced with Python's `contextmanager` pattern. This architectural choice addresses several critical engineering challenges:

* **Resource Management:** By using the `yield` keyword within a `@contextmanager` decorator, the system guarantees that database connections are always closed, preventing memory leaks and file locking issues.
* **Atomic Transactions:** The manager automatically performs a `conn.commit()` upon successful execution or a `conn.rollback()` if an exception occurs. This ensures that the database never enters an inconsistent state during complex write operations.
* **Encapsulation:** All SQL queries are abstracted within the `DatabaseManager` class, allowing the UI components to interact with data through high-level methods without needing to handle raw SQL syntax.

### 3.2 Relational Schema Design

The data model is structured into three normalized tables to support diverse productivity metrics:

* **`tasks` Table:** Stores the state of the user's workflow. It utilizes dynamic text fields for deadlines and priorities, allowing for flexible filtering and sorting.
* **`timers` Table:** Acts as a configuration store for user-defined focus presets. This decoupling allows the UI to populate the "Queue" and "Presets" views dynamically.
* **`activity` Table:** The core of the analytics engine. It records every interaction with a high-precision ISO 8601 timestamp and a session-based UUID. This design supports complex time-series analysis (e.g., "focus hours per day" or "average session length per priority").

### 3.3 Asset Management & Deployment Strategy

To ensure the application is portable and "production-ready," Tivitapp implements a sophisticated asset resolution strategy:

* **`resource_path` Utility:** This method detects whether the application is running in a standard Python interpreter or as a bundled executable (via PyInstaller). It dynamically resolves the path to the `_MEIPASS` temporary folder or the local directory.
* **Cross-Platform Pathing:** By using `os.path.join`, the system maintains compatibility across Windows, macOS, and Linux, preventing hardcoded string errors.
* **Binary Packaging:** The architecture is fully compatible with standalone `.exe` distribution, ensuring that all iconography, logos, and the SQLite database remain accessible regardless of the installation environment.

### 3.4 Data Retrieval & Temporal Queries

The system supports advanced data fetching logic, including:

* **Pattern Matching:** Utilizing SQL `LIKE` operators for date-based filtering.
* **Boundary Analysis:** Fetching activity records between specific ISO 8601 timestamps, which is the foundation for the upcoming Analytics module.

## Module 4: UI/UX Design & Component-Based Architecture

Tivitapp's interface is built on a modular, component-based architecture that prioritizes scalability and a modern user experience. By leveraging the full power of the PyQt6 framework, the application achieves a clean separation between functional logic and visual presentation.

### 4.1 Modular View Controller Pattern

The application architecture is divided into independent view modules (`TasksView`, `PomodoroView`, etc.). Each module is an encapsulated `QWidget` that manages its own internal state and UI components.

* **Encapsulation:** Views communicate with the `MainWindow` through the Signal/Slot mechanism, ensuring that changes in one module do not produce side effects in others.
* **Dynamic Navigation:** The navigation system uses a custom-styled `QWidget` acting as a controller to swap the active view within a `QVBoxLayout`. This prevents memory overhead by maintaining only the necessary components in the visual stack.
* **Memory Management:** Each view is responsible for its own resource cleanup, utilizing PyQt’s parent-child hierarchy to ensure proper garbage collection of UI elements.

### 4.2 Professional Styling with QSS (Qt Style Sheets)

To achieve a contemporary "flat" design, Tivitapp implements a comprehensive styling system using QSS, the Qt equivalent of CSS.

* **Separation of Concerns:** Styles are defined through localized and global style sheets, separating the aesthetic definition from the Python logic.
* **Dynamic Properties:** The UI utilizes custom properties (e.g., `active_tab` vs `inactive_tab`) to update component styles at runtime. The system uses `.unpolish()` and `.polish()` methods to force the Qt style engine to re-render components dynamically when their state changes.
* **Responsive Layouts:** Using a combination of `QGridLayout`, `QHBoxLayout`, and `QVBoxLayout` with specific stretch factors, the application remains functional and aesthetically pleasing across different window dimensions (from $800 \times 600$ to $1280 \times 720$).

### 4.3 User Experience (UX) Enhancements

* **Visual Consistency:** A unified color palette (Blue/Gray/White) is applied across all modules to reduce cognitive load.
* **Contextual Feedback:** Interactive elements, such as checkboxes and buttons, provide immediate visual feedback (e.g., color shifts and strike-through text for completed tasks).
* **Iconography:** Integration of custom high-fidelity assets for priorities and system status, ensuring an intuitive "at-a-glance" interpretation of productivity data.

---

## Technical Future Roadmap

The architecture is currently prepared for the implementation of advanced modules:

1. **Analytics Module:** Utilizing the `activity` table data to generate productivity heatmaps and focus-time trends using `matplotlib` or `PyQtGraph`.
2. **File Management System:** A dedicated view for handling task-related documents with direct database linking.
3. **AI Integration:** A local or API-based Chatbot designed to assist with task prioritization and schedule optimization.


