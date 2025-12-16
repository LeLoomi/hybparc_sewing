from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage
import requests
import cv2 as cv

class AlignmentWizardWidget(QWidget):    
    PREVIEW_TICKS_PER_S = 30
    SKIP_FRAMES = 5
    OVERLAY_PATH = "./alignment_overlay.png"
    
    wizard_done_signal = pyqtSignal()
    
    reload_overlay = True
    current_overlay = None
    preview_clock = QTimer()
    
    # gp_res is not capture res! 480 is not really 480 with gopro, but we must request 480...
    def __init__(self, gp_ip: str, gp_http_port: str, gp_udp_port: str, gp_res: str, cap_res: tuple[int, int], cap_fps: float, ffmpeg_flags: str, cam_api: int, fourcc: int):        
        super().__init__()

        self.GP_IP = gp_ip
        self.GP_HTTP_PORT = gp_http_port
        self.GP_UDP_PORT = gp_udp_port
        self.GP_RES = gp_res
        self.CAP_RES = cap_res
        self.CAP_FPS = cap_fps
        self.FFMPEG_FLAGS = ffmpeg_flags
        self.CAM_API = cam_api
        self.FOURCC = fourcc

        self.send_gopro_command(command_path='/gopro/webcam/start', 
                                params={'res': f'{self.GP_RES}',
                                        'fov': '0',
                                        'port': f'{self.GP_UDP_PORT}',
                                        'protocol': 'TS'})

        self.stream = cv.VideoCapture(f'udp://@:{self.GP_UDP_PORT}{self.FFMPEG_FLAGS}', apiPreference=self.CAM_API)
        self.stream.set(cv.CAP_PROP_FOURCC, self.FOURCC)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, self.CAP_RES[0])
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, self.CAP_RES[1])
        self.stream.set(cv.CAP_PROP_FPS, self.CAP_FPS)
        self.log('✅ Capture is running.')

        explainer_label = QLabel('''<b>Willkommen bei der Kamera-Einstellungshilfe</b>
                                    <br>Bitte richte das Nahtpad und sein Beiwerk so aus, dass der pinke Rahmen gut mit den Kanten des Nahtmaterials übereinstimmt.''')
        
        font = explainer_label.font()
        font.setPointSize(28)
        explainer_label.setTextFormat(Qt.TextFormat.RichText)
        explainer_label.setAlignment(Qt.AlignmentFlag.AlignLeading)
        explainer_label.setWordWrap(True)
        explainer_label.setFont(font)

        self.imageLabel = QLabel()

        save_new_button = QPushButton()
        save_new_button.setText("Aktuelle Position speichern")
        save_new_button.setFont(font)
        save_new_button.clicked.connect(self.save_current)
        save_new_button.setDisabled(True) # ! diabled since we don't have edge detection for the pad.

        done_button = QPushButton()
        done_button.setText("Anwendung starten")
        done_button.setFont(font)
        done_button.setShortcut(Qt.Key.Key_Return)
        done_button.clicked.connect(self.stop_preview)
        done_button.clicked.connect(self.emit_wizard_done_signal)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(save_new_button)
        button_layout.addSpacing(15)
        button_layout.addWidget(done_button)
        button_layout.addStretch()

        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addWidget(explainer_label)
        contentLayout.addWidget(self.imageLabel)
        contentLayout.addLayout(button_layout)
        contentLayout.addStretch()
        
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(contentLayout)
        horizontalLayout.addStretch()
        
        while not self.stream.isOpened():
            pass
        
        self.setLayout(horizontalLayout)
                
        self.start_preview()
    
    # starts UI clock to let us show "video" aka single frames in rapid succession
    def start_preview(self):        
        if(self.preview_clock.isActive()):
            return
        
        self.log('🛫 Starting preview.')
        self.frame_n = 0
        
        self.current_overlay = cv.imread(self.OVERLAY_PATH)
        self.current_overlay = cv.cvtColor(self.current_overlay, cv.COLOR_RGBA2BGR)
        
        self.preview_clock.timeout.connect(self.update_preview)
        self.preview_clock.start(round(1000 / self.PREVIEW_TICKS_PER_S))
        
        self.log('🍿 Preview is running.')
    
    # refreshes the preview image and reloads the overlay, if necessary / if reload flag is set
    def update_preview(self):
        if(self.reload_overlay or self.current_overlay is None):
            try:
                self.current_overlay = cv.imread(self.OVERLAY_PATH)
                self.current_overlay = cv.cvtColor(self.current_overlay, cv.COLOR_RGBA2BGRA) # pyright: ignore[reportCallIssue, reportArgumentType]
                self.reload_overlay = False
            except:
                pass
        
        self.stream.grab()
        ret, self.current_frame = self.stream.read()
        self.current_frame = cv.cvtColor(self.current_frame, cv.COLOR_RGB2BGRA)
        
        if(self.frame_n < self.SKIP_FRAMES):
            self.frame_n += 1
            return
        
        else:
            self.frame_n = 0        
        
        height, width, channel = self.current_frame.shape
        bytesPerLine = 4 * width
        
        try:
            raw_with_saved_overlay = self.overlay_opaque(self.current_frame, self.current_overlay) # pyright: ignore[reportArgumentType, reportCallIssue]
        except: 
            # if we don't have a saved overlay
            raw_with_saved_overlay = self.current_frame
        
        #raw_with_saved_overlay = cv.cvtColor(self.current_frame, cv.COLOR_BGR2RGBA)
        
        qImg = QImage(
            raw_with_saved_overlay.data, 
            width,
            height,
            bytesPerLine,
            QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qImg).scaledToWidth(1200, Qt.TransformationMode.FastTransformation)  # 2300 is a good fit for our local screen setup
        self.imageLabel.setPixmap(pixmap)
    
    def stop_preview(self):
        if(self.preview_clock.isActive()):
            self.preview_clock.stop()
        
        self.send_gopro_command(command_path='/gopro/webcam/stop')
    
        self.stream.release()
        self.log('🛑 Preview stopped and stream released.')
    
    def save_current(self):
        img = self.current_frame
        cv.imwrite(self.OVERLAY_PATH, cv.cvtColor(img, cv.COLOR_BGRA2RGBA))
        self.reload_overlay = True
    
    def send_gopro_command(self, command_path: str, params: dict[str, str] = {}, panic_on_failure = True):
        path = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/{command_path}'
        
        try:
            req = requests.get(url = path, params=params, timeout = 2.5)
            self.log(f'📡 Sent command \'{command_path}\' with {params} to GoPro. Return code \'{req.status_code}\'.')
        except:
            if panic_on_failure:
                raise TimeoutError(f'HTTP GET timeout under \'{path}\'. Is there really a GoPro at {self.GP_IP} listening on {self.GP_HTTP_PORT}?')
            else:
                self.log(f'⚠️ HTTP GET timeout under \'{path}\' however panic_on_failure is set to False for this request.')
    
    def handle_application_close(self):
        self.log('♻️ Application closure initiated, running resource cleanup.')
        self.send_gopro_command(command_path='/gopro/webcam/exit', panic_on_failure=False)
        self.send_gopro_command(command_path='/gopro/camera/setting', params={'option':'4','setting':'135'}, panic_on_failure=False)
    
    def emit_wizard_done_signal(self):
        self.wizard_done_signal.emit()
    
    # ! assumes, that the two images are the same size
    # https://docs.opencv.org/3.4/d0/d86/tutorial_py_image_arithmetics.html
    @staticmethod
    def overlay_opaque(base_img: cv.typing.MatLike, overlay_img: cv.typing.MatLike) -> cv.typing.MatLike:
        # create mask from non-black pixels in overlay
        gray = cv.cvtColor(overlay_img, cv.COLOR_BGRA2GRAY)  # threshold needs single channel grayscale image
        ret, mask = cv.threshold(gray, 10, 255, cv.THRESH_BINARY)
        mask_inv = cv.bitwise_not(mask)

        # use mask to clear out pixels
        background = cv.bitwise_and(base_img, base_img, mask=mask_inv)
        foreground = cv.bitwise_and(overlay_img, overlay_img, mask=mask)
        combined = cv.add(background, foreground)

        return combined

    @staticmethod
    def log(message: str):
        print(f'[Hybparc] {message}')