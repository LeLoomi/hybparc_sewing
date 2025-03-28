import cv2 as cv    # sadly we have to load cv here, since we use it to capture the images
from PyQt6.QtWidgets import QApplication, QMainWindow
from welcome_widget import WelcomeWidget

class MainWindow(QMainWindow):
    
    warmup_passes = 11
    
    # Entry into the GUI
    def __init__(self):
        print('[Hybparc] Booting up')
        super().__init__()
        
        # Setup and warm up cameras
        #! Adjustments are specific to our Intel Realsense d435i
        if False == True:
            self.stream = cv.VideoCapture(index=0, apiPreference=cv.CAP_ANY)
            self.stream.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
            self.stream.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
            self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Window setup
        self.showMaximized()
        self.setWindowTitle('Hybparc EKG (Aruco)')
        self.show_welcome_widget()

    # Welcome screen on the 
    def show_welcome_widget(self):
        print('[Hybparc] Diplaying welcome widget')
        welcome_widget = WelcomeWidget()
        #welcome_widget.start_pressed.connect(self.show_place_electrodes)
        self.setCentralWidget(welcome_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    #apply_stylesheet(app, theme='light_blue.xml')
    window.show()
    app.exec()