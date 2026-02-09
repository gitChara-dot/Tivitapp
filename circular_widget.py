from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import  Qt,QRectF

class CircularWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200,200)
        self.maximum_size = 5760
        self.minimum_size = 0
        self.current_size = 5760
    def get_max_size(self):
        return self.maximum_size
        
    def set_current_size(self,size:int):
        self.current_size = size
        self.update()
    def decrease_size(self, degrees:int):
        self.current_size -= degrees*16
        self.update()
    def restore_size(self):
        self.current_size = 5760
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)


        pen = QPen(QColor(83,104,120, 70)) # gray blue, below the main circle
        
        pen_width = 5
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        

        painter.setPen(pen)

        #Create a square with the dimensions to contain the widget
        width = self.width()
        height = self.height()

        side = min(width, height)

        #Adjust pos
        x_offset = (width-side)/2  +5
        y_offset = (height-side)/2 +5
        #Avoid the circle cutting off
        margin = pen_width/2

        side = side-margin

        rect_painter = QRectF(x_offset, y_offset, side-2*margin,side-2*margin)
        
        painter.drawArc(rect_painter, 0, self.maximum_size) #Draw a gray blue arc below

        pen.setColor(QColor(74, 144, 226)) # Blue for main circle
        
        painter.setPen(pen) #update the pen
        
        painter.drawArc(rect_painter, 0, self.current_size ) # Draw the main circle

        painter.end()
    def calc_degree_per_second(self, max_time):
        return int(self.maximum_size/max_time/16)
