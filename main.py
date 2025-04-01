import cv2 as cv
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow
from welcome_widget import WelcomeWidget
from recording_widget import RecordingWidget

class MainWindow(QMainWindow):
    resolution = (1280, 720)
    real_fps = 30.0
    target_fps = 5
    cam_index = 1
    cam_api = cv.CAP_ANY
    fourcc = cv.VideoWriter.fourcc('M', 'J', 'P', 'G') # realsense = YUY2
    
    recording = False
    
    # Entry into the GUI
    def __init__(self):
        print('[Hybparc] Booting up')
        super().__init__()
        
        # Setup and warm up cameras
        # ! Adjustments are specific to our Intel Realsense d435i
        self.stream = cv.VideoCapture(index=self.cam_index, apiPreference=self.cam_api)
        self.stream.set(cv.CAP_PROP_FOURCC, self.fourcc)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.stream.set(cv.CAP_PROP_FPS, self.real_fps)
        
        # Window setup
        self.showMaximized()
        self.setWindowTitle('Hybparc Sewing Training')
        self.show_welcome_widget()

    # Welcome screen on the 
    def show_welcome_widget(self):
        print('[Hybparc] Displaying welcome widget')
        welcome_widget = WelcomeWidget()
        welcome_widget.start_pressed.connect(self.show_recording_screen)
        self.setCentralWidget(welcome_widget)

    def show_recording_screen(self):
        print('[Hybparc] Displaying recording widget')
        recording_widget = RecordingWidget()
        recording_widget.start_recording_signal.connect(self.start_recording)
        recording_widget.stop_recording_signal.connect(self.stop_recording)
        self.setCentralWidget(recording_widget)
    
    def start_recording(self):
        self.recording = True
        self.ct = threading.Thread(target=self.record, args=())
        self.ct.start()
        print('[Hybparc] Started recording')
    
    def stop_recording(self):
        self.recording = False
        print('[Hybparc] Stopped recording')
    
    def record(self):
        self.out = cv.VideoWriter('recording.avi', self.fourcc, self.target_fps, self.resolution)
        iter = int(self.real_fps / self.target_fps - 1)
        frame_counter = iter
        current_frame = None

        while self.recording:
            ret, frame = self.stream.read()
            
            # skip iter if we are not at the next frame again
            if current_frame == frame.all:
                continue
            
            if frame_counter == iter:
                self.out.write(frame)
                frame_counter = int((frame_counter + 1) % (int(self.real_fps / self.target_fps)))
            
            else:
                frame_counter = frame_counter + 1
        
        #self.stream.release()
        self.out.release()
        print('[Hybparc] Video saved.')

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()