from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QLineEdit, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
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

        startButton = QPushButton("Weiter")
        startButton.clicked.connect(self.emit_start_pressed)
        startButton.setShortcut(Qt.Key.Key_Return)
        startButton.setFont(mediumFont)
        startButton.setMaximumWidth(150)

        verticalLayout = QVBoxLayout()
        verticalLayout.addStretch()
        verticalLayout.addWidget(textLabel)
        verticalLayout.addWidget(startButton)
        verticalLayout.setAlignment(startButton, Qt.AlignmentFlag.AlignHCenter)
        verticalLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(verticalLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)

    def emit_start_pressed(self):
        self.start_pressed.emit()