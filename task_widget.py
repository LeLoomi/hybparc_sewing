from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QLineEdit, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class TaskWidget(QWidget):
    continue_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # Setup ui
        headerLabel = QLabel("<b>Aufgabenstellung</b>")
        largeFont = headerLabel.font()
        largeFont.setPointSize(32)
        largeFont.setBold(True)
        headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headerLabel.setFont(largeFont)

        mediumFont = QFont()
        mediumFont.setPointSize(28)

        self.m_lineEditName = QLineEdit()
        self.m_lineEditName.setMinimumWidth(300)
        self.m_lineEditName.setFont(mediumFont)

        textLabel = QLabel('Nähe an dem Nahtpad so viele Einzelknopfnähte, wie du schaffst. Achte dabei auch auf gute Qualität!<br>Du hast hierfür fünf Minuten Zeit, danach erfolgt die Auswertung.')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        startButton = QPushButton("Weiter")
        startButton.clicked.connect(self.emit_continue_pressed)
        startButton.setShortcut(Qt.Key.Key_Return)
        startButton.setFont(mediumFont)
        startButton.setMaximumWidth(150)

        verticalLayout = QVBoxLayout()
        verticalLayout.addStretch()
        verticalLayout.addWidget(headerLabel)
        verticalLayout.addWidget(textLabel)
        verticalLayout.addWidget(startButton)
        verticalLayout.setAlignment(startButton, Qt.AlignmentFlag.AlignHCenter)
        verticalLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(verticalLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)

    def emit_continue_pressed(self):
        self.continue_pressed.emit()