from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ResultsWidget(QWidget):
    new_try_requested_signal = pyqtSignal()
    
    levelTexts = [
        'Die Aufzeichnung wurde innerhalb weniger Sekunden abgebrochen und daher nicht ausgewertet.',
        'Du verfügst über Grundkenntnisse und Grundfertigkeiten. Übe weiter, um noch mehr Sicherheit zu bekommen.',
        'Du kennst die wichtigen Aspekte der Einzelknopfnaht und kannst diese fortgeschritten anwenden.',
        'Du bist mit allen Aspekten der Einzelknopfnaht vertraut und kannst diese geschickt anwenden.'
    ]
    
    def __init__(self, result_level_to_display: int = 0):
        super().__init__()

        # We use icon here, since SVG -> Icon -> Pixmap has higher base resolution than SVG -> Pixmap pipeline
        starsQIcon = QIcon(f"./graphics/progress_feedback_{result_level_to_display}.svg")
        starsPixmap = starsQIcon.pixmap(QSize(1095, 155), QIcon.Mode.Normal, QIcon.State.On)
        starLabel = QLabel()
        starLabel.setPixmap(starsPixmap.scaledToHeight(210))
        starLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textLabel = QLabel(f'{self.levelTexts[result_level_to_display]}')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)

        self.controlButton = QPushButton('Neuer Durchlauf')
        self.controlButton.clicked.connect(self.start_new_try)
        self.controlButton.setFont(font)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.controlButton)
        buttonLayout.addStretch()
        
        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addWidget(starLabel)
        contentLayout.addWidget(textLabel)
        contentLayout.addLayout(buttonLayout)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def start_new_try(self):
        self.new_try_requested_signal.emit()