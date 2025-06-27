from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class RecordingWidget(QWidget):
    start_recording_signal = pyqtSignal()
    stop_recording_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        textLabel = QLabel('Drücke auf Start um zu beginnen.<br>Danach wird aufgezeichnet bis du stop drückst.')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(32)
        textLabel.setFont(font)

        iconTextLayout = QHBoxLayout()
        iconTextLayout.addStretch()
        iconTextLayout.addWidget(textLabel)
        iconTextLayout.addStretch()

        self.controlButton = QPushButton('Aufzeichnung starten')
        self.controlButton.clicked.connect(self.start_recording)
        self.controlButton.setFont(font)
        
        self.iconLabel = QLabel()
        self.iconLabel.setPixmap(QPixmap('graphics/video-slash-solid.svg').scaledToHeight(50, Qt.TransformationMode.SmoothTransformation))
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.iconLabel)
        buttonLayout.addWidget(self.controlButton)
        buttonLayout.addStretch()
        
        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addLayout(iconTextLayout)
        contentLayout.addLayout(buttonLayout)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def start_recording(self):
        self.start_recording_signal.emit()

    def stop_recording(self):
        self.stop_recording_signal.emit()

    # called directly from main, to handle when we know rec has actually started
    def handle_ui_start(self):
        self.controlButton.setText('Aufzeichnung stoppen')
        self.iconLabel.setPixmap(QPixmap('./graphics/video-solid.svg').scaledToHeight(50, Qt.TransformationMode.SmoothTransformation))
        self.controlButton.clicked.disconnect(self.start_recording)
        self.controlButton.clicked.connect(self.stop_recording)

    # called directly from main, to handle when we know rec has actually stopped
    def handle_ui_stop(self):
        self.controlButton.setText('Nochmal aufzeichnen')
        self.iconLabel.setPixmap(QPixmap('./graphics/video-slash-solid.svg').scaledToHeight(50, Qt.TransformationMode.SmoothTransformation))
        self.controlButton.clicked.connect(self.start_recording)
        self.controlButton.clicked.disconnect(self.stop_recording)