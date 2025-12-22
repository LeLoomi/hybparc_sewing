from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QLineEdit, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

class WelcomeWidget(QWidget):
    start_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # Setup ui
        headerLabel = QLabel("<b>Hybparc-GUI: Start</b>")
        largeFont = headerLabel.font()
        largeFont.setPointSize(48)
        largeFont.setBold(True)
        headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headerLabel.setFont(largeFont)

        mediumFont = QFont()
        mediumFont.setPointSize(28)

        self.m_lineEditName = QLineEdit()
        self.m_lineEditName.setMinimumWidth(300)
        self.m_lineEditName.setFont(mediumFont)

        textLabel = QLabel('Willkommen zur Naht-Selbstlerneinheit!')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)

        self.startButton = QPushButton("Weiter")
        self.startButton.clicked.connect(self.handle_continue_pressed)
        self.startButton.setShortcut(Qt.Key.Key_Return)
        self.startButton.setFont(mediumFont)
        self.startButton.setMaximumWidth(150)

        verticalLayout = QVBoxLayout()
        verticalLayout.addStretch()
        verticalLayout.addWidget(textLabel)
        verticalLayout.addWidget(self.startButton)
        verticalLayout.setAlignment(self.startButton, Qt.AlignmentFlag.AlignHCenter)
        verticalLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(verticalLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)

    def handle_continue_pressed(self):
        self.startButton.setDisabled(True)
        self.repaint()
        QTimer.singleShot(0, self.emit_continue_pressed)    # needed for Qt painter thread stuff...
    
    def emit_continue_pressed(self):
        self.start_pressed.emit()