from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from tips_dialog import TipsDialog

class ResultsWidget(QWidget):
    new_try_requested_signal = pyqtSignal()
    
    currentLevel = 0
    levelTexts = [
        'Die Aufzeichnung wurde innerhalb weniger Sekunden abgebrochen und daher nicht ausgewertet.',
        'Du verfügst über Grundkenntnisse und Grundfertigkeiten. Übe weiter, um noch mehr Sicherheit zu bekommen.',
        'Du kennst die wichtigen Aspekte der Einzelknopfnaht und kannst diese fortgeschritten anwenden.',
        'Du bist mit allen Aspekten der Einzelknopfnaht vertraut und kannst diese geschickt anwenden.'
    ]
    
    def __init__(self, result_level_to_display: int = 0):
        super().__init__()

        self.currentLevel = result_level_to_display

        # We use icon here, since SVG -> Icon -> Pixmap has higher base resolution than SVG -> Pixmap pipeline
        starsQIcon = QIcon(f"./graphics/progress_feedback_{self.currentLevel}.svg")
        starsPixmap = starsQIcon.pixmap(QSize(485, 155), QIcon.Mode.Normal, QIcon.State.On)
        starLabel = QLabel()
        starLabel.setPixmap(starsPixmap.scaledToHeight(120, Qt.TransformationMode.SmoothTransformation))
        starLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        textLabel = QLabel(f'{self.levelTexts[self.currentLevel]}')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)

        self.helpButton = QPushButton('Tips')
        self.helpButton.clicked.connect(self.help_button_clicked)
        self.helpButton.setFont(font)

        self.newTryButton = QPushButton('Neuer Durchlauf')
        self.newTryButton.clicked.connect(self.start_new_try)
        self.newTryButton.setFont(font)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.helpButton)
        buttonLayout.addSpacing(15)
        buttonLayout.addWidget(self.newTryButton)
        buttonLayout.addStretch()
        
        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addWidget(starLabel)
        contentLayout.addSpacing(20)
        contentLayout.addWidget(textLabel)
        contentLayout.addSpacing(25)
        contentLayout.addLayout(buttonLayout)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def start_new_try(self):
        self.new_try_requested_signal.emit()
    
    def help_button_clicked(self):
        dialog = TipsDialog(self.currentLevel)
        dialog.exec()