from PyQt6.QtWidgets import QWidget, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtGui import QKeySequence
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

        buttonBox = QDialogButtonBox()
        self.startButton = buttonBox.addButton('Start recording', QDialogButtonBox.ButtonRole.YesRole)
        self.startButton.clicked.connect(self.start_recording)
        self.startButton.setFont(font)
        self.startButton.setShortcut(Qt.Key.Key_Return)
        
        self.stopButton = buttonBox.addButton('Stop recording', QDialogButtonBox.ButtonRole.NoRole)
        self.stopButton.clicked.connect(self.stop_recording)
        self.stopButton.setFont(font)
        self.stopButton.setDisabled(True)

        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addLayout(iconTextLayout)
        contentLayout.addWidget(buttonBox)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def start_recording(self):
        self.startButton.setDisabled(True)
        self.stopButton.setEnabled(True)
        self.startButton.setShortcut(QKeySequence())
        self.stopButton.setShortcut(Qt.Key.Key_Return)
        self.start_recording_signal.emit()

    def stop_recording(self):
        self.startButton.setEnabled(True)
        self.stopButton.setDisabled(True)
        self.startButton.setShortcut(Qt.Key.Key_Return)
        self.stopButton.setShortcut(QKeySequence())
        self.stop_recording_signal.emit()