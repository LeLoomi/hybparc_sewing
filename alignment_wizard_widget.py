from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtSvgWidgets import QSvgWidget
import requests
import cv2 as cv
import threading

class AlignmentWizardWidget(QWidget):
    wizard_is_done_signal = pyqtSignal()
    capture_started_running_signal = pyqtSignal()
    
    PREVIEW_TICKS_PER_S = 30
    SKIP_FRAMES = 0
    OVERLAY_PATH = './alignment_overlay.png'
        
    preview_loading_text = '<b>Einen Moment, bitte</b><br>Der Ausrichtungsassistet wird noch geladen...'
    explainer_text = '<b>Willkommen bei der Kamera-Einstellungshilfe</b> <br>Bitte richte das Nahtpad und sein Beiwerk so aus, dass der pinke Rahmen gut mit den Kanten des Nahtpads übereinstimmt.'
    
    reload_overlay = True
    current_overlay = None
    preview_clock = QTimer()
    
    # gp_res is not capture res! 480 is not really 480 with gopro, but we must request 480...
    def __init__(self, gp_ip: str, gp_http_port: str, gp_udp_port: str, gp_res: str, gp_fov: str, cap_res: tuple[int, int], cap_fps: float, ffmpeg_flags: str, cam_api: int, fourcc: int):
        super().__init__()

        self.GP_IP = gp_ip
        self.GP_HTTP_PORT = gp_http_port
        self.GP_UDP_PORT = gp_udp_port
        self.GP_RES = gp_res
        self.GP_FOV = gp_fov
        self.CAP_RES = cap_res
        self.CAP_FPS = cap_fps
        self.FFMPEG_FLAGS = ffmpeg_flags
        self.CAM_API = cam_api
        self.FOURCC = fourcc

        self.BUFFER_BURN_COUNT = round(self.CAP_FPS * 10)  # testing showed a buffer induced delay of up to 8 seconds on capture obj creation, so we just burn 10s worth of frames to be sure

        self.send_gopro_command(command_path='/gopro/webcam/start', 
                                params={'res': f'{self.GP_RES}',
                                        'fov': f'{self.GP_FOV}',
                                        'port': f'{self.GP_UDP_PORT}',
                                        'protocol': 'TS'})

        self.capture_started_running_signal.connect(self.start_preview)
        
        self.rec_thread = threading.Thread(target=self.setup_capture)
        QTimer.singleShot(0, self.rec_thread.start)
        
        self.main_text_label = QLabel(self.preview_loading_text)
        
        font = self.main_text_label.font()
        font.setPointSize(28)
        self.main_text_label.setTextFormat(Qt.TextFormat.RichText)
        self.main_text_label.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.main_text_label.setWordWrap(True)
        self.main_text_label.setFont(font)

        self.current_frame_label = QLabel()

        self.spinner_svg_widget = QSvgWidget('./graphics/circle-notch-solid-animated.svg')
        self.spinner_svg_widget.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio) # pyright: ignore[reportOptionalMemberAccess]
        self.spinner_svg_widget.setFixedSize(55, 55)

        save_new_button = QPushButton()
        save_new_button.setText('Aktuelle Position speichern')
        save_new_button.setFont(font)
        #save_new_button.clicked.connect(self.save_current)
        save_new_button.setDisabled(True) # ! diabled since we don't have edge detection for the pad.

        done_button = QPushButton()
        done_button.setText('Anwendung starten')
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

        self.content_layout = QVBoxLayout()
        self.content_layout.addStretch()
        self.content_layout.addWidget(self.main_text_label)
        self.content_layout.addWidget(self.spinner_svg_widget)
        self.content_layout.setAlignment(self.spinner_svg_widget, Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.current_frame_label)
        self.current_frame_label.setHidden(True)
        self.content_layout.addLayout(button_layout)
        
        self.content_layout.addStretch()
        
        horizontal_wrapper_layout = QHBoxLayout()
        horizontal_wrapper_layout.addStretch()
        horizontal_wrapper_layout.addLayout(self.content_layout)
        horizontal_wrapper_layout.addStretch()
        
        
        self.setLayout(horizontal_wrapper_layout)
    
    def setup_capture(self):
        self.stream = cv.VideoCapture(f'udp://@:{self.GP_UDP_PORT}{self.FFMPEG_FLAGS}', apiPreference=self.CAM_API)
        self.stream.set(cv.CAP_PROP_FOURCC, self.FOURCC)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, self.CAP_RES[0])
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, self.CAP_RES[1])
        self.stream.set(cv.CAP_PROP_FPS, self.CAP_FPS)
        self.log('✅ Capture is running.')
        
        for i in range(0, self.BUFFER_BURN_COUNT):
            self.stream.grab()
        self.log(f'Burned {self.BUFFER_BURN_COUNT} frames to avoid preview delay.')
        
        self.capture_started_running_signal.emit()
    
    # starts UI clock to let us show "video" aka single frames in rapid succession
    def start_preview(self):
        if(self.preview_clock.isActive()):
            return
        
        self.log('🛫 Starting preview.')
        self.set_state_preview_running()
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
        self.current_frame_label.setPixmap(pixmap)
    
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
        
    def set_state_preview_running(self):
        self.content_layout.removeWidget(self.spinner_svg_widget)
        self.current_frame_label.setHidden(False)
        self.main_text_label.setText(self.explainer_text)
    
    def emit_wizard_done_signal(self):
        self.wizard_is_done_signal.emit()
    
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