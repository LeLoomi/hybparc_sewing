import cv2 as cv
import threading
import requests
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow
#from aachen_suturing import predict_mitz
from welcome_widget import WelcomeWidget
from recording_widget import RecordingWidget

class MainWindow(QMainWindow):
    GP_IP = '172.29.197.51'         # GP http endpoint, for IP check official gp docs
    GP_HTTP_PORT = '8080'
    GP_UDP_PORT = '8554'            # UDP Port, 8554 = default
    GP_RES = '480'                 # ! stream res, supported: 480, 720, 1080
    FFMPEG_FLAGS = '?overrun_nonfatal=1'   # ffmpeg buffer overflow = ignored lol
    CAP_RES = (848, 480)          # ! must match the RES param and GP ratio
    REAL_FPS = 30.0                 # GoPro default should be 30.0 i think
    TARGET_FPS = 5                  # needs to be a fraction of REAL_FPS
    CAM_API = cv.CAP_ANY
    FOURCC = cv.VideoWriter.fourcc(*'MJPG')
    RECORDING_LENGTH = 5#5*60         # in seconds
    
    recording = False   # don't touch
    recorded_frames: list[cv.typing.MatLike] = list()
    processed_frames: list[cv.typing.MatLike] = list()
    
    # Entry into the GUI
    def __init__(self):
        self.log('✌️ Booting up.')
        super().__init__()
        
        # Window setup
        self.showMaximized()
        self.setWindowTitle('Hybparc Sewing Training')
        self.show_welcome_widget()

    # Welcome screen on the 
    def show_welcome_widget(self):
        self.log('📺 Displaying welcome widget.')
        welcome_widget = WelcomeWidget()
        welcome_widget.start_pressed.connect(self.show_recording_screen)
        self.setCentralWidget(welcome_widget)

    def show_recording_screen(self):
        self.log('📺 Displaying recording widget.')
        self.recording_widget = RecordingWidget()
        self.recording_widget.start_recording_signal.connect(self.start_recording)
        self.recording_widget.stop_recording_signal.connect(self.stop_recording)
        self.setCentralWidget(self.recording_widget)
    
    def start_recording(self):
        # Set up GoPro
        try:
            req = requests.get(url = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/gp/gpWEBCAM/START?res={self.GP_RES}', timeout = 2.5)
        except:
            raise TimeoutError(f'HTTP GET timeout. Is there really a GoPro at {self.GP_IP} listening on {self.GP_HTTP_PORT}?')
        
        self.log('📡 Commanded UDP stream to start.')
        if req.status_code == 200:
            self.log('🛰️ RC 200, stream is running.')
        else:
            # TODO handle this and retry at least once ngl
            self.log('🚨 RC was {req.status_code} (expected = 200). \n{req.content}\n\n')
            raise RuntimeError(f'Camera is available at {self.GP_IP}:{self.GP_HTTP_PORT} but failed to start.')
        
        self.recording = True
        self.rec_thread = threading.Thread(target=self.record, args=())
        self.rec_thread.start()
        self.recording_widget.handle_ui_start()
        self.log('📸 Starting to record.')
    
    def handle_timeout(self):
        if(self.recording):
            self.log(f'⏰ Recording time ran out after {round(self.RECORDING_LENGTH)} seconds.')
            self.stop_recording()
    
    def stop_recording(self):
        if(self.timer.isActive): self.timer.stop()  # in case the user pressed "stop recording"
        
        self.recording = False
        self.rec_thread.join()  # wait for thread to wrap up before doing rest of cleanup to prevent race cond.
        self.log('📷 Ceasing to record.')
        
        try: req = requests.get(url = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/gp/gpWEBCAM/STOP', timeout = 2.5)
        except TimeoutError as e:
            raise TimeoutError(f'HTTP GET timeout. Is there still a GoPro at {self.GP_IP} listening on {self.GP_HTTP_PORT}?')
        
        self.log('📡 Commanded UDP stream to stop.')
        if req.status_code == 200:
            self.log('🛰️ RC 200, streaming has ceased.')
        else:
            # ? does this need handling? imo no tbh
            self.log(f'🚨 RC was {req.status_code} (expected: 200). \n{req.content}\n\n')
            raise RuntimeError(f'Camera responded with {req.status_code} to stop command!')
        
        self.recording_widget.handle_ui_stop()
        
        self.process_frames()
    
    def record(self):
        # Set up capture
        self.stream = cv.VideoCapture(f'udp://@:{self.GP_UDP_PORT}{self.FFMPEG_FLAGS}', apiPreference=self.CAM_API)
        self.stream.set(cv.CAP_PROP_FOURCC, self.FOURCC)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, self.CAP_RES[0])
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, self.CAP_RES[1])
        self.stream.set(cv.CAP_PROP_FPS, self.REAL_FPS)
        self.log('✅ Capture is running.')
        
        iter = int(self.REAL_FPS / self.TARGET_FPS - 1)
        drop_counter = iter
        total_frames = 0
        self.recorded_frames.clear()

        self.timer = QTimer()
        self.timer.singleShot(self.RECORDING_LENGTH * 1000, self.handle_timeout)

        while self.recording:
            ret, frame = self.stream.read()
            
            if drop_counter == iter:
                total_frames += 1
                self.recorded_frames.append(frame)
                self.log(str(total_frames))
                drop_counter = int((drop_counter + 1) % (int(self.REAL_FPS / self.TARGET_FPS)))
            
            else:
                drop_counter = drop_counter + 1
        
        self.stream.release()
        self.log(f'💾 Recorded {len(self.recorded_frames)} frames (ca. {len(self.recorded_frames) / self.TARGET_FPS}s).')


    def process_frames(self):
        self.processed_frames.clear()
        
        for i in range(len(self.recorded_frames)):
            img = self.recorded_frames[i]
            
            # GP9 480 = (848x480) which is not 16:9 by like 4px in width.....
            new_h = 476
            new_w = 848
            orig_h, orig_w, c = img.shape
            center_y = int(orig_h / 2)
            center_x = int(orig_w / 2)
            
            img = img[center_y - int(new_h / 2) : center_y + int(new_h / 2), center_x - int(new_w / 2) : center_x + int(new_w / 2)]
            
            cv.imwrite(f'out/10cropped.png', img)
            
            # now we have 16:9 so we can scale down to models preferred 270x480 (which is 16:9 also)
            img = cv.resize(src=img, dsize=(480, 270))
            
            self.processed_frames.append(img)
        cv.imwrite(f'out/0original.png', self.recorded_frames[0])
        cv.imwrite(f'out/30final.png', self.processed_frames[0])
        
        # ! Model call happens here
        #predict_mitz.main("test-lul", self.processed_frames, 3, 'models/20240112_I3D_snip64_seg12-70_15_15-1632-best.pt', 12, 64)

    def log(self, message: str):
        print(f'[Hybparc] {message}')

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()