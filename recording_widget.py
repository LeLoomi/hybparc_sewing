from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget

class RecordingWidget(QWidget):
    start_recording_signal = pyqtSignal()
    stop_recording_signal = pyqtSignal()
    
    # we need signals for thread safety lol
    set_state_ready_to_record_signal = pyqtSignal()
    set_state_booting_capture_signal = pyqtSignal()
    set_state_evaluating_signal = pyqtSignal()
    set_state_recording_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        textLabel = QLabel('Drücke auf Start um zu beginnen.<br>Danach wird aufgezeichnet bis du stop drückst.')
        textLabel.setTextFormat(Qt.TextFormat.RichText)
        textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        
        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
        self.iconSvgWidget.setFixedSize(55, 55)
        
        self.countdownLabel = QLabel("TIME")
        cd_font = font
        cd_font.setPointSize(48)
        self.countdownLabel.setFont(font)
        self.countdownLabel.font
        
        timeIconLayout = QHBoxLayout()
        timeIconLayout.setSpacing(30)
        timeIconLayout.addStretch()
        timeIconLayout.addWidget(self.iconSvgWidget)
        timeIconLayout.addWidget(self.countdownLabel)
        timeIconLayout.addStretch()
        
        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addLayout(iconTextLayout)
        contentLayout.addLayout(timeIconLayout)
        contentLayout.addWidget(self.controlButton)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
        
        self.set_state_ready_to_record_signal.connect(self.set_state_ready_to_record)
        self.set_state_booting_capture_signal.connect(self.set_state_booting_capture)
        self.set_state_evaluating_signal.connect(self.set_state_evaluating)
        self.set_state_recording_signal.connect(self.set_state_recording)
    
    def start_recording(self):
        self.start_recording_signal.emit()

    def stop_recording(self):
        self.stop_recording_signal.emit()

    # called directly from main, to handle when we know rec has actually started
    def set_state_recording(self):
        self.controlButton.setText('Aufzeichnung stoppen')
        self.controlButton.setEnabled(True)
        self.iconSvgWidget.load('./graphics/video-solid.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
        
        self.controlButton.clicked.connect(self.stop_recording)
        try:
            self.controlButton.clicked.disconnect(self.start_recording)
        except: pass

    def set_state_booting_capture(self):
        self.controlButton.setText('Aufnahme wird gestartet...')
        self.controlButton.setDisabled(True)
        self.iconSvgWidget.load('./graphics/circle-notch-solid-animated.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
    
    def set_state_evaluating(self):
        self.controlButton.setText('Aufnahme wird ausgewertet...')
        self.controlButton.setDisabled(True)
        self.iconSvgWidget.load('./graphics/circle-notch-solid-animated.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]

    # called directly from main, to handle when we know rec has actually stopped
    def set_state_ready_to_record(self):
        self.controlButton.setText('Nochmal aufzeichnen')
        self.controlButton.setEnabled(True)
        self.iconSvgWidget.load('./graphics/video-slash-solid.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
        
        self.controlButton.clicked.connect(self.start_recording)
        try:
            self.controlButton.clicked.disconnect(self.stop_recording)
        except: 
            pass
    
    def updateCountdownTime(self, newTime):
        # scrappy asf but its fine for now
        try:
            self.countdownLabel.setText(newTime)
        except:
            pass