from PyQt6.QtWidgets import QWidget, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class RecordingWidget(QWidget):
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
    
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
        startButton = buttonBox.addButton('Start recording', QDialogButtonBox.ButtonRole.AcceptRole)
        startButton.setFont(font)
        startButton.setShortcut(Qt.Key.Key_Return)
        stopButton = buttonBox.addButton('Stop recording', QDialogButtonBox.ButtonRole.HelpRole)
        stopButton.setFont(font)
        buttonBox.accepted.connect(self.emit_start)
        buttonBox.helpRequested.connect(self.emit_stop)

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
    
    def emit_start(self):
        self.start_recording.emit()

    def emit_stop(self):
        self.stop_recording.emit()