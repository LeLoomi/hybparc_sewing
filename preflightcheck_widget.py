from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, pyqtSignal
import requests

class PreflightCheckWidget(QWidget):
    precheck_completed_signal = pyqtSignal()    # signal to tell main.py we are ready to continue
    
    def __init__(self, GP_IP, GP_HTTP_PORT):
        super().__init__()

        self.GP_IP = GP_IP
        self.GP_HTTP_PORT = GP_HTTP_PORT

        self.headerLabel = QLabel("<b>Kameraüberprüfung</b>")
        self.headerLabel.setTextFormat(Qt.TextFormat.RichText)
        self.headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.infoLabel = QLabel("")
        infoFont = self.infoLabel.font()
        infoFont.setPointSize(24)
        self.infoLabel.setFont(infoFont)
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setFixedWidth(1200)

        font = self.headerLabel.font()
        font.setPointSize(28)
        self.headerLabel.setFont(font)
        
        self.runCheckButton = QPushButton("Erneut prüfen")
        self.runCheckButton.setFont(font)
        self.runCheckButton.setShortcut(Qt.Key.Key_Return)
        self.runCheckButton.clicked.connect(self.run_check)

        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
        self.iconSvgWidget.setFixedSize(55, 55)

        self.buttonIconLayout = QHBoxLayout()
        self.buttonIconLayout.setSpacing(30)
        self.buttonIconLayout.addStretch()
        self.buttonIconLayout.addWidget(self.iconSvgWidget)
        self.buttonIconLayout.addWidget(self.runCheckButton)
        self.buttonIconLayout.addStretch()

        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.setSpacing(20)
        contentLayout.addWidget(self.headerLabel)
        contentLayout.addWidget(self.infoLabel)
        contentLayout.addLayout(self.buttonIconLayout)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def send_done_signal(self):
        self.precheck_completed_signal.emit()
    
    def run_check(self):
        self.check_camera()
    
    def check_camera(self):
        self.set_state_check_in_progress()
        
        try:
            req = requests.get(url = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/gp/gpControl/status', timeout = 2.5)
        except Exception as e:
            if(type(e) == requests.exceptions.ConnectTimeout):
                self.log(f"🚨 Camera timed out, is it on and reachable on {self.GP_IP}:{self.GP_HTTP_PORT}?")
                self.set_state_check_timeout()
            else:
                self.log(f"🚨 Unhandled failure with message {str(e)}?")
                self.set_state_other_failure(str(e))
            return
        if(req.status_code == 200):
            self.log("✅ Camera returned HTTP 200, good to go.")
            self.send_done_signal()
        else:
            self.log(f"⚠️ Camera returned HTTP {req.status_code}!")
            self.set_state_other_failure(f"HTTP Error {req.status_code}")
    
    def set_state_check_in_progress(self):
        self.iconSvgWidget = QSvgWidget('./graphics/circle-notch-solid-animated.svg')
        self.infoLabel.setText("<i>Verbindung zur Kamera wird geprüft...</i>")
    
    def set_state_check_timeout(self):
        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.infoLabel.setText("Die Kamera konnte nicht gefunden werden :(<p>Bitte prüfe, ob sie eingeschaltet und per Kabel verbunden ist. Auf ihren Displays sollte \"USB CONNECTED\" stehen.<p>Falls die Kamera dennoch nicht gefunden wird, stecke bitte das Kabel an der Kamera aus und wieder ein. Eventuell musst du die Kamera danach an der Seite (bei der '9') neu einschalten.")
    
    def set_state_other_failure(self, message: str):
        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.infoLabel.setText(f"Unerwarteter Fehler:<br><tt>{message}</tt><br>Bitte schreibe diesen Fehler auf und melde ihn an das MITZ-Team!")

    @staticmethod
    def log(message: str):
        print(f'[Hybparc] {message}')