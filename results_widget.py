from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ResultsWidget(QWidget):
    new_try_requested_signal = pyqtSignal()
        
    def __init__(self, starcount_to_display: int = 0):
        super().__init__()

        textLabel = QLabel(f'Die Auswertung ist abgeschlossen!')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)

        # We use icon here, since SVG -> Icon -> Pixmap has higher base resolution than SVG -> Pixmap pipeline
        progressIcon = QIcon(f"./graphics/progress_feedback_{starcount_to_display}.svg")
        progressPixmap = progressIcon.pixmap(QSize(1095, 155), QIcon.Mode.Normal, QIcon.State.On)
        progressBarLabel = QLabel()
        progressBarLabel.setPixmap(progressPixmap.scaledToHeight(210))
        progressBarLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        iconTextLayout = QHBoxLayout()
        iconTextLayout.addStretch()
        iconTextLayout.addWidget(textLabel)
        iconTextLayout.addStretch()

        self.controlButton = QPushButton('Neuer Durchlauf')
        self.controlButton.clicked.connect(self.start_new_try)
        self.controlButton.setFont(font)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.controlButton)
        buttonLayout.addStretch()
        
        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addLayout(iconTextLayout)
        contentLayout.addWidget(progressBarLabel)
        contentLayout.addLayout(buttonLayout)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def start_new_try(self):
        self.new_try_requested_signal.emit()