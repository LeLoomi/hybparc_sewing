import cv2 as cv
import threading
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow
from welcome_widget import WelcomeWidget
from recording_widget import RecordingWidget

class MainWindow(QMainWindow):
    GP_IP = '172.29.197.51'         # GP http endpoint, for IP check official gp docs
    GP_HTTP_PORT = '8080'
    GP_UDP_PORT = '8554'               # UDP Port, 8554 = default
    GP_RES = '1080'                 # ! stream res, supported: 480, 720, 1080
    FFMPEG_FLAGS = '?overrun_nonfatal=1'   # ffmpeg buffer overflow = ignored lol
    CAP_RES = (1920, 1080)          # ! must match the RES param
    REAL_FPS = 30.0                 # GoPro default should be 30.0 i think
    TARGET_FPS = 5                  # needs to be a fraction of REAL_FPS
    CAM_API = cv.CAP_ANY
    FOURCC = cv.VideoWriter.fourcc(*'MJPG')
    
    recording = False
    
    # Entry into the GUI
    def __init__(self):
        print('[Hybparc] ⏰ Booting up.')
        super().__init__()
        
        # Window setup
        self.showMaximized()
        self.setWindowTitle('Hybparc Sewing Training')
        self.show_welcome_widget()

    # Welcome screen on the 
    def show_welcome_widget(self):
        print('[Hybparc] 📺 Displaying welcome widget.')
        welcome_widget = WelcomeWidget()
        welcome_widget.start_pressed.connect(self.show_recording_screen)
        self.setCentralWidget(welcome_widget)

    def show_recording_screen(self):
        print('[Hybparc] 📺 Displaying recording widget.')
        recording_widget = RecordingWidget()
        recording_widget.start_recording_signal.connect(self.start_recording)
        recording_widget.stop_recording_signal.connect(self.stop_recording)
        self.setCentralWidget(recording_widget)
    
    def start_recording(self):
        # Set up GoPro
        try:
            req = requests.get(url = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/gp/gpWEBCAM/START?res={self.GP_RES}', timeout = 2.5)
        except:
            raise TimeoutError(f'HTTP GET timeout. Is there really a GoPro at {self.GP_IP} listening on {self.GP_HTTP_PORT}?')
        
        print('[Hybparc] 📡 Commanded UDP stream to start.')
        if req.status_code == 200:
            print('[Hybparc] 🛰️ RC 200, stream is running.')
        else:
            # TODO handle this and retry at least once ngl
            print(f'[Hybparc] 🚨 RC was {req.status_code} (expected = 200). \n{req.content}\n\n')
            raise RuntimeError(f'Camera is available at {self.GP_IP}:{self.GP_HTTP_PORT} but failed to start.')
        
        # Set up capture
        self.stream = cv.VideoCapture(f'udp://@:{self.GP_UDP_PORT}{self.FFMPEG_FLAGS}', apiPreference=self.CAM_API)
        self.stream.set(cv.CAP_PROP_FOURCC, self.FOURCC)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, self.CAP_RES[0])
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, self.CAP_RES[1])
        self.stream.set(cv.CAP_PROP_FPS, self.REAL_FPS)
        print('[Hybparc] ✅ Capture is running.')
        
        self.recording = True
        self.ct = threading.Thread(target=self.record, args=())
        self.ct.start()
        print('[Hybparc] 📸 Started recording.')
    
    def stop_recording(self):
        self.recording = False
        print('[Hybparc] 📷 Stopped recording.')
        
        try: req = requests.get(url = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/gp/gpWEBCAM/STOP', timeout = 2.5)
        except TimeoutError as e:
            raise TimeoutError(f'HTTP GET timeout. Is there still a GoPro at {self.GP_IP} listening on {self.GP_HTTP_PORT}?')
        
        print('[Hybparc] 📡 Commanded UDP stream to stop.')
        if req.status_code == 200:
            print('[Hybparc] 🛰️ RC 200, streaming has ceased.')
        else:
            # ? does this need handling? imo no tbh
            print(f'[Hybparc] 🚨 RC was {req.status_code} (expected: 200). \n{req.content}\n\n')
            raise RuntimeError(f'Camera responded with {req.status_code} to stop command!')
    
    def record(self):
        self.out = cv.VideoWriter('recording.avi', self.FOURCC, self.TARGET_FPS, self.CAP_RES)
        iter = int(self.REAL_FPS / self.TARGET_FPS - 1)
        frame_counter = iter

        while self.recording:
            ret, frame = self.stream.read()
            
            if frame_counter == iter:
                self.out.write(frame)
                frame_counter = int((frame_counter + 1) % (int(self.REAL_FPS / self.TARGET_FPS)))
            
            else:
                frame_counter = frame_counter + 1
        
        self.stream.release()
        self.out.release()
        print('[Hybparc] 💾 Video saved.')


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()