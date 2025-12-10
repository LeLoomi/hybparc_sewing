from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QLineEdit, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class CleanupWidget(QWidget):
    continue_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # Setup ui
        headerLabel = QLabel("<b>Vor der Auswertung</b>")
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

        textLabel = QLabel('<h3>Achtung!</h3>Entsorge zunächst alle benutzten Nahtmaterialien und Nadeln im Spitzabwurf und entferne die Nähte am Nahtpad.')
        textLabel.setTextFormat(Qt.TextFormat.RichText)
        textLabel.setWordWrap(True)
        textLabel.setFixedWidth(1200)
        textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        startButton = QPushButton("Erledigt")
        startButton.clicked.connect(self.emit_continue_pressed)
        startButton.setShortcut(Qt.Key.Key_Return)
        startButton.setFont(mediumFont)
        startButton.setMaximumWidth(150)

        verticalLayout = QVBoxLayout()
        verticalLayout.addStretch()
        verticalLayout.addWidget(textLabel)
        verticalLayout.addSpacing(15)
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