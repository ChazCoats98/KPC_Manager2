
import math
import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRect, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPaintEvent
from textwrap import wrap

class RadioButtonTableWidget(QWidget):
    def __init__(self, parent=None):
        super(RadioButtonTableWidget, self).__init__(parent)
        
        self.layout = QHBoxLayout()
        
        self.yesRadio = QRadioButton('Yes')
        self.noRadio = QRadioButton('No')
        
        self.layout.addWidget(self.yesRadio)
        self.layout.addWidget(self.noRadio)
        
        self.setLayout(self.layout)
        
    stateChanged: typing.ClassVar[pyqtSignal]
        
    def isChecked(self):
        if self.yesRadio.isChecked():
            return True
        elif self.noRadio.isChecked():
            return False
        
    def setChecked(self, val: bool):
        if val:
            self.yesRadio.setChecked(True)
        else:
            self.noRadio.setChecked(True)
        
class SpinnerWidget(QWidget):
    def __init__(
        self, 
        parent=None, 
        center=True, 
        disable_parent=True,
        lines=20, 
        radius=10, 
        line_length=10, 
        speed=math.pi / 2, 
        fade=80, 
        color=None, 
        line_width=2,
        roundness=100,
        spinner_text = None
        ):
        super(SpinnerWidget, self).__init__(parent)
        self._current_counter = 0
        self._number_of_lines = lines
        self._inner_radius = radius
        self._line_length = line_length
        self._revolutions_per_second = speed
        self._center_on_parent = center
        self._disable_parent_when_spinning = disable_parent
        self._minimum_trail_opacity = math.pi
        self._trail_fade_percentage = fade
        self._color = color
        self._line_width = line_width
        self._roundness = roundness
        self.label = spinner_text
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._update_size()
        self._update_timer()
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        if spinner_text is not None:
            self.status_label = QLabel(self)
            self.status_label.setText(self.label)
            self.status_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
            
        self.setLayout(main_layout)
        self.hide()
        
    def _rotate(self):
        self._current_counter += 1
        if self._current_counter >= self._number_of_lines:
            self._current_counter = 0
        self.update()
        
    def _update_size(self):
        size = (self._inner_radius + self._line_length) * 2
        self.setFixedSize(size, size)
        
        if self.label:
            print(len(self.label))
            self.setFixedSize(size + (len(self.label) + 50), size + (self._inner_radius * 5))
        
    def _update_timer(self):
        self._timer.setInterval(
            int(1000 / (self._number_of_lines * self._revolutions_per_second))
        )
        
    def paintEvent(self,_):
        self._update_position()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        if self._current_counter >= self._number_of_lines:
            self._current_counter = 0
        
        painter.setPen(Qt.NoPen)
        for i in range(self._number_of_lines):
            painter.save()
            painter.translate(
                self.width() // 2,
                self._inner_radius + self._line_length
            )
            rotate_angle = 360 * i / self._number_of_lines
            painter.rotate(rotate_angle)
            painter.translate(self._inner_radius, 0)
            distance = self._line_count_distance_from_primary(
                i, self._current_counter, self._number_of_lines
            )
            color = self._current_line_color(
                distance, 
                self._number_of_lines,
                self._trail_fade_percentage,
                self._minimum_trail_opacity,
                self._color
            )
            painter.setBrush(color)
            painter.drawRoundedRect(
                QRect(
                    0, 
                    -self._line_width // 2,
                    self._line_length,
                    self._line_width,
                    
                ),
                self._roundness,
                self._roundness,
                Qt.RelativeSize
            )
            painter.restore()
            
    def start(self):
        self._update_position()
        self._is_spinning = True
        self.show()
        self.raise_()
        self.activateWindow()
        
        if self.parentWidget() and self._disable_parent_when_spinning:
            self.parentWidget().setEnabled(False)
        
        if not self._timer.isActive():
            self._timer.start()
            self._current_counter = 0
            
    def stop(self):
        self._is_spinning = False
        self.hide()
        
        if self.parentWidget() and self._disable_parent_when_spinning:
            self.parentWidget().setEnabled(True)
            
        if self._timer.isActive():
            self._timer.stop()
            self._current_counter = 0
    
    def _update_position(self):
        if self.parentWidget() and self._center_on_parent:
            self.move(
                (self.parentWidget().width() - self.width()) // 2,
                (self.parentWidget().height() - self.height()) // 2,
            )
            
    def _line_count_distance_from_primary(self, current, primary, total_nr_of_lines):
        distance = primary - current
        if distance < 0:
            distance += total_nr_of_lines 
        return distance
    
    def _current_line_color(self, count_distance, total_nr_of_lines, trail_fade_perc, min_opacity, color_input):
        color = QColor(color_input)
        if count_distance == 0:
            return color
        min_alpha_f = min_opacity / 100
        distance_threshold = int(
            math.ceil((total_nr_of_lines - 1) * trail_fade_perc / 100)
        )
        if count_distance > distance_threshold:
            color.setAlphaF(min_alpha_f)
        else:
            alpha_diff = color.alphaF() - min_alpha_f
            gradient = alpha_diff / float(distance_threshold + 1)
            result_alpha = color.alphaF() - gradient * count_distance
            result_alpha = min(1, max(0, result_alpha))
            color.setAlphaF(result_alpha)
        return color
    