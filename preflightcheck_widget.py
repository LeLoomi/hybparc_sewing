from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon
import requests

class PreflightCheckWidget(QWidget):
    precheck_completed_signal = pyqtSignal()    # signal to tell main.py we are ready to continue
    run_camera_check_signal = pyqtSignal()
    
    IMAGE_HEIGHT = 440
    current_tip = 0     # ! don't touch
    
    hint_content = [
        [
            "Prüfe, ob die GoPro-Kamera eingeschaltet ist. Du kannst hierfür den Bildschirm auf der Rückseite (räumlich: Oberseite) antippen.<br>Sollte die Kamera aus sein, kannst du sie durch 3 Sekündiges gedrückt halten des \"Power mode\" (siehe Bild) Knopfes einschalten.",
            "./graphics/gopro-status-tooltips/power-side.png",
            ""
        ],
        [
            "Bitte Prüfe, ob das Kabel der GoPro-Kamera korrekt eingesteckt ist.<br>Wenn du das Kabel aus und wieder einsteckst, musst du eventuell die Kamera neu einschalten.",
            "./graphics/gopro-status-tooltips/cable-empty.png",
            "./graphics/gopro-status-tooltips/cable-plugged.png"
        ],
        [
            "Bitte prüfe, dass auf den Displays der Kamera \"USB CONNECTED\" steht.<br>Eventuell musst du dafür den Bildschirm auf der Rückseite (räumlich: Oberseite) antippen, um ihn aufzuwecken. <br>Sollte nicht \"USB CONNECTED\" darauf stehen, prüfe bitte, dass das Kabel angesteckt ist und die Kamera ansgeschaltet ist.",
            "./graphics/gopro-status-tooltips/usb-front.png",
            "./graphics/gopro-status-tooltips/usb-back.png"
        ]
    ]
    
    def __init__(self):
        super().__init__()

        # * general stuff setup starts here
        self.headerLabel = QLabel("<b>Kameraüberprüfung</b>")
        self.headerLabel.setTextFormat(Qt.TextFormat.RichText)
        self.headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        headerFont = self.headerLabel.font()
        headerFont.setPointSize(36)
        self.headerLabel.setFont(headerFont)
        
        self.infoLabel = QLabel("")
        infoFont = self.infoLabel.font()
        infoFont.setPointSize(24)
        self.infoLabel.setFont(infoFont)
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoLabel.setWordWrap(True)
        
        self.runCheckButton = QPushButton("Erneut prüfen")
        self.runCheckButton.setShortcut(Qt.Key.Key_Return)
        self.runCheckButton.clicked.connect(self.run_camera_check_signal.emit)
        
        buttonFont = self.runCheckButton.font()
        buttonFont.setPointSize(32)
        self.runCheckButton.setFont(buttonFont)

        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.iconSvgWidget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
        self.iconSvgWidget.setFixedSize(55, 55)

        # * layouts of header stuff start here
        headerLayout = QVBoxLayout()
        headerLayout.setSpacing(20)
        headerLayout.addWidget(self.headerLabel)
        headerLayout.addWidget(self.infoLabel)

        # * tooltip setup starts here
        self.imgLabel1 = QLabel()
        self.imgLabel2 = QLabel()

        self.mainTipLabel = QLabel()
        self.mainTipLabel.setFont(infoFont)
        self.mainTipLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # back button
        self.goBackButton = QPushButton(" Zurück")
        pixmapBackwardButton = QPixmap("./graphics/angle-left-solid.svg")
        self.goBackButton.setIcon(QIcon(pixmapBackwardButton))
        self.goBackButton.setIconSize(QSize(26, 26))
        self.goBackButton.setFont(buttonFont)
        self.goBackButton.clicked.connect(self.backward_btn_clicked)

        # forward button
        self.goForwardButton = QPushButton("Okay ")
        pixmapForwardButton = QPixmap("./graphics/angle-right-solid.svg")
        self.goForwardButton.setIcon(QIcon(pixmapForwardButton))
        self.goForwardButton.setIconSize(QSize(26, 26))
        self.goForwardButton.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.goForwardButton.setFont(buttonFont)
        self.goForwardButton.clicked.connect(self.forward_btn_clicked)

        # * tooltip layouts assembly starts here
        tipImageLayout = QHBoxLayout()
        tipImageLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tipImageLayout.addStretch()
        tipImageLayout.addWidget(self.imgLabel1)
        tipImageLayout.addWidget(self.imgLabel2)
        tipImageLayout.addStretch()
        
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.goBackButton)
        buttonLayout.addSpacing(90)
        buttonLayout.addWidget(self.runCheckButton)
        buttonLayout.addSpacing(90)
        buttonLayout.addWidget(self.goForwardButton)
        buttonLayout.addStretch()

        # * final layout assembly
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addSpacing(180)
        mainLayout.addLayout(headerLayout)
        mainLayout.addStretch()
        mainLayout.addWidget(self.mainTipLabel)
        mainLayout.addSpacing(10)
        mainLayout.addLayout(tipImageLayout)
        mainLayout.addSpacing(60)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addSpacing(180)

        self.load_tip(self.current_tip)
        self.setLayout(mainLayout)
    
    def handle_check_result(self, result: bool | Exception):
        if isinstance(result, requests.ConnectTimeout):
                self.log(f"⚠️  Timeout occured during camera precheck HTTP request. Check connectivity as indicated on screen.")
                self.set_state_check_timeout()
        elif isinstance(result, bool):
            if result == True:
                self.log(f"✅ Camera preflight check completed.")
                self.precheck_completed_signal.emit()
            else:
                self.log(f'🚨 Unexpected failure occured in preflight!')
                raise ValueError('Preflight check return was False, which should be utterly impossible. How did we get here?')
        else:
                self.log(f'🚨 Unhandled failure occured in preflight: {result}')
                self.set_state_other_failure(str(result))
    
    def set_state_check_timeout(self):
        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.infoLabel.setText("Leider konnte keine Verbindung mit der Kamera hergestellt werden!")
    
    def set_state_other_failure(self, message: str):
        self.iconSvgWidget = QSvgWidget('./graphics/video-slash-solid.svg')
        self.infoLabel.setText(f"Unerwarteter Fehler:<br><tt>{message}</tt><br>Bitte schreibe diesen Fehler auf und melde ihn an das MITZ-Team!")

    def forward_btn_clicked(self):
        self.load_tip(self.current_tip + 1)
    
    def backward_btn_clicked(self):
        self.load_tip(self.current_tip - 1)

    def load_tip(self, index):
        self.current_tip = index
        self.imgLabel1.setHidden(True)
        self.imgLabel2.setHidden(True)
        
        self.goBackButton.setEnabled(not index == 0)
        self.goForwardButton.setEnabled(not index == len(self.hint_content) - 1)
        
        current_hint = self.hint_content[index]
        
        if current_hint[0] != "":
            self.mainTipLabel.setText(current_hint[0])
        
        if current_hint[1] != "":
            pm1 = QPixmap(current_hint[1])
            pm1 = self.scale_pixmap_to_height(pm1, self.IMAGE_HEIGHT)
            self.imgLabel1.setPixmap(pm1)
            self.imgLabel1.setHidden(False)
        
        if current_hint[2] != "":
            pm2 = QPixmap(current_hint[2])
            pm2 = self.scale_pixmap_to_height(pm2, self.IMAGE_HEIGHT)
            self.imgLabel2.setPixmap(pm2)
            self.imgLabel2.setHidden(False)

    def handle_precheck_done(self):
        self.runCheckButton.setEnabled(False)
        self.repaint()
        QTimer.singleShot(0, self.send_done_signal)

    def send_done_signal(self):
        self.precheck_completed_signal.emit()

    @staticmethod
    def scale_pixmap_to_height(image: QPixmap, height: int) -> QPixmap:
        width = round(image.height() / image.width()) * height
        image = image.scaled(height, width, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return image

    @staticmethod
    def log(message: str):
        print(f'[Hybparc] {message}')