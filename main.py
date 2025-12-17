import cv2 as cv
import threading
import requests
from sys import argv
from ipaddress import ip_address
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow
from welcome_widget import WelcomeWidget
from preflightcheck_widget import PreflightCheckWidget
from alignment_wizard_widget import AlignmentWizardWidget
from task_widget import TaskWidget
from recording_widget import RecordingWidget
from cleanup_widget import CleanupWidget
from results_widget import ResultsWidget
from aachen_suturing import predict_mitz
from PIL import Image
from playsound3 import playsound

class MainWindow(QMainWindow):
    show_cleanup_widget_signal = pyqtSignal()
    start_recording_timer_signal = pyqtSignal()
    
    GP_IP: str = '172.25.190.51'            # GP http endpoint, for IP check official gp docs
    GP_HTTP_PORT: str = '8080'
    GP_UDP_PORT: str = '8554'               # UDP Port, 8554 = default
    GP_RES = '4'                            # stream res, supported: 4=480, 7=720, 12=1080
    GP_FOV = '4'                            # 0=Wide, 2=Narrow, 3=Superview, 4=Linear
    FFMPEG_FLAGS = '?overrun_nonfatal=1'    # ffmpeg buffer overflow = we don't care lol
    CAP_RES: tuple[int, int] = (848, 480)   # ! must match the RES param and GPs ratio impl -> 4=480p but is actually 848x480 not 854x480 
    REAL_FPS = 30.0                         # GoPro default should be 30.0 i think
    TARGET_FPS = 5                          # needs to be a fraction of REAL_FPS
    CAM_API = cv.CAP_FFMPEG 
    FOURCC = cv.VideoWriter.fourcc(*'MJPG')
    RECORDING_LENGTH = 5*60                 # in seconds, the time for which we roughly record
    MODEL_ERROR_FRAME_PADDING = 15          # in seconds, the time for which we don't actually run the model to prevent crashes due to 'not enough frames'
    
    recording = False   # don't touch
    halftime_sound_played = False
    recorded_frames: list[cv.typing.MatLike] = list()
    processed_frames: list[Image.Image] = list()
    
    current_result: int = 0
    
    # Entry into the GUI
    def __init__(self):
        self.log('✌️  Booting up.', with_spacer=True)
        super().__init__()
        
        try:
            ip_address(argv[1])
            self.GP_IP = argv[1]
            self.log(f'🧭 An IP was provided as run-argument an will be used ({argv[1]}).', with_spacer=True)
        except IndexError:
            self.log(f'📦 No IP provided as run-argument, using default ({self.GP_IP}).')
        except ValueError:
            self.log(f'⚠️  Malformed IP provided as run-argument ({argv[1]}). Falling back to default ({self.GP_IP}).')
        
        # Window setup
        self.showMaximized()
        self.setWindowTitle('Hybparc Sewing Training')
        self.show_welcome_widget()
        
        app.lastWindowClosed.connect(self.handle_application_close)
        self.start_recording_timer_signal.connect(self.start_recording_timer)
        self.show_cleanup_widget_signal.connect(self.show_cleanup_widget)

    # Welcome screen on the 
    def show_welcome_widget(self):
        self.log('📺 Displaying welcome widget.', with_spacer=True)
        welcome_widget = WelcomeWidget()
        welcome_widget.start_pressed.connect(self.show_preflight_check_widget)
        self.setCentralWidget(welcome_widget)

    def show_preflight_check_widget(self):
        self.log('📺 Displaying preflight check widget.', with_spacer=True)
        precheckWidget = PreflightCheckWidget(self.GP_IP, self.GP_HTTP_PORT)
        precheckWidget.precheck_completed_signal.connect(self.init_gopro_webcam)
        self.setCentralWidget(precheckWidget)
        precheckWidget.check_camera()   # if camera is available, we even skip the check visually most of the time

    def init_gopro_webcam(self):
        self.log('🛠️ Initializing GoPro Webcam mode.', with_spacer=True)
        # 59=auto power down; 6=15 minutes. GP shouldn't power down while plugged in, but just to be sure
        self.send_gopro_command(command_path='/gopro/camera/setting', params={'setting':'59', 'option':'6'}, panic_on_failure=False)
        # boot GP into webcam mode without immediately starting the stream. needed for fov command to be allowed 
        self.send_gopro_command('/gopro/webcam/preview')
        # trivia: setting FOV during a running webcam (not preview) results in resolution being set to 1080 and a stream restart lol
        self.send_gopro_command('/gp/gpWebcam/SETTINGS', {'fov': self.GP_FOV})  # command call only supported via old API version, case sensitive!
        QTimer.singleShot(0, self.show_alignment_wizard_widget)

    def show_alignment_wizard_widget(self):
        self.log('📺 Displaying alignment wizard widget.', with_spacer=True)
        alignment_wizard_widget = AlignmentWizardWidget(
            self.GP_IP,
            self.GP_HTTP_PORT,
            self.GP_UDP_PORT,
            self.GP_RES,
            self.CAP_RES,
            self.REAL_FPS,
            self.FFMPEG_FLAGS,
            self.CAM_API,
            self.FOURCC
        )
        alignment_wizard_widget.wizard_done_signal.connect(self.show_task_widget)
        self.setCentralWidget(alignment_wizard_widget)

    def show_task_widget(self):
        self.log(f'📺 Displaying cleanup widget.', with_spacer=True)
        self.task_widget = TaskWidget()
        self.task_widget.continue_pressed.connect(self.show_recording_widget)
        self.setCentralWidget(self.task_widget)

    def show_recording_widget(self):
        self.log('📺 Displaying recording widget.', with_spacer=True)
        self.recording_widget = RecordingWidget()
        self.recording_widget.updateCountdownTime(self.prettify_min_sec(self.RECORDING_LENGTH * 1000))  # times 1000 since method takes msec 
        self.recording_widget.start_recording_signal.connect(self.start_recording)
        self.recording_widget.stop_recording_signal.connect(self.stop_recording)
        self.setCentralWidget(self.recording_widget)
    
    def show_cleanup_widget(self):
        self.log(f'📺 Displaying cleanup widget.', with_spacer=True)
        self.cleanup_widget = CleanupWidget()
        self.cleanup_widget.continue_pressed.connect(self.show_results_widget)
        self.setCentralWidget(self.cleanup_widget)
    
    def show_results_widget(self):
        self.log(f'📺 Displaying results widget.')
        self.results_widget = ResultsWidget(result_level_to_display=self.current_result)
        self.results_widget.new_try_requested_signal.connect(self.show_task_widget)
        self.setCentralWidget(self.results_widget)
    
    def start_recording(self):
        # Set up GoPro
        self.send_gopro_command(command_path='/gopro/webcam/start', params={'res': self.GP_RES})
        
        self.recording = True
        self.rec_thread = threading.Thread(target=self.record, args=())
        self.rec_thread.start()
        
        # set ui loading until we actually have our capture running [Search REF001]
        self.recording_widget.set_state_booting_capture_signal.emit()
        
        self.log('📸 Starting to record.')
    
    def start_recording_timer(self):
        # recordingTimer
        self.uiClock = QTimer()
        self.recordingTimer = QTimer()
        self.recordingTimer.setSingleShot(True)
        self.recordingTimer.timeout.connect(self.handle_recording_timeout)
        self.recordingTimer.start(self.RECORDING_LENGTH * 1000)
        self.uiClock.timeout.connect(self.handle_ui_clock_timeout)
        self.uiClock.start(200)
    
    def handle_recording_timeout(self):
        if(self.recording):
            self.log(f'⏰ Recording time ran out after {round(self.RECORDING_LENGTH)} seconds.')
            playsound('./sounds/tissman_alert3-version-8.wav', block=False)
            self.log('🔔 Timer end sound played.')
            self.stop_recording()
    
    def handle_ui_clock_timeout(self):
        t = self.recordingTimer.remainingTime()
        self.recording_widget.updateCountdownTime(
            self.prettify_min_sec(t))
                
        if(not self.halftime_sound_played and round(t/1000) < round(self.RECORDING_LENGTH/2)):
            self.halftime_sound_played = True
            playsound('./sounds/tissman_alert3-version-9.wav', block=False)
            self.log('🔔 Timer halftime sound played.')
    
    def stop_recording(self, is_application_quit=False):
        if(self.recordingTimer.isActive()): 
            self.recordingTimer.stop()  # in case the user pressed 'stop recording'
        if(self.uiClock.isActive()):
            self.uiClock.stop()
        
        self.recording = False
        self.rec_thread.join()  # wait for thread to wrap up before doing rest of cleanup to prevent race cond.
        self.log('📷 Ceasing to record.')
        
        self.send_gopro_command(command_path='/gopro/webcam/stop')
        
        if is_application_quit:
            self.log('☝️  We are in cleanup, omitting recording evaluation.')
            return
        
        self.recording_widget.set_state_ready_to_record_signal.emit()
        
        # ! care: method continues exec after starting thread!
        threading.Thread(target=self.process_frames, args=()).start()
        
        # since this is now threaded ui still works -> we want to disable recording button for example
        # we reanable it at the end of process_frames() :) [Search REF002]
        self.recording_widget.set_state_evaluating_signal.emit()
        
    def record(self):
        # Set up capture
        self.stream = cv.VideoCapture(f'udp://@:{self.GP_UDP_PORT}{self.FFMPEG_FLAGS}', apiPreference=self.CAM_API)
        self.stream.set(cv.CAP_PROP_FOURCC, self.FOURCC)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, self.CAP_RES[0])
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, self.CAP_RES[1])
        self.stream.set(cv.CAP_PROP_FPS, self.REAL_FPS)
        self.log('✅ Capture is running.')
        
        # capture is running so we can now actually set ui to say so [Search REF001]
        self.recording_widget.set_state_recording_signal.emit()
        
        iter = int(self.REAL_FPS / self.TARGET_FPS - 1)
        drop_counter = iter
        total_frames = 0
        self.recorded_frames.clear()

        self.start_recording_timer_signal.emit()
        playsound('./sounds/tissman_alert3-version-1.wav', block=False)

        while self.recording:
            ret, frame = self.stream.read()
            
            if drop_counter == iter:
                total_frames += 1
                self.recorded_frames.append(frame)
                drop_counter = int((drop_counter + 1) % (int(self.REAL_FPS / self.TARGET_FPS)))
            
            else:
                drop_counter = drop_counter + 1
        
        self.stream.release()
        self.log(f'💾 Recorded {len(self.recorded_frames)} frames (ca. {len(self.recorded_frames) / self.TARGET_FPS}s).')

    def prettify_min_sec(self, msec: int) -> str:
        if(msec < 0):
            return '00:00'
        
        sec_int: int = int(round((msec / 1000) % 60))
        min_int: int = int(round((msec/ 1000) // 60))
        
        if(sec_int < 10):
            sec_str: str = f'0{sec_int}'
        else:
            sec_str: str = f'{sec_int}'
        
        if(min_int == 0):
            min_str: str = f'00'
        elif(min_int < 10):
            min_str: str = f'0{min_int}'
        else:
            min_str: str = f'{sec_int}'
        
        return f'{min_str}:{sec_str}'
    
    def process_frames(self):
        self.processed_frames.clear()
        
        for i in range(len(self.recorded_frames)):
            img = self.recorded_frames[i]
            
            # We sometimes get broken frames for some reason. Ty Gopro i guess.
            if (img is type(None)):
                continue
            if (img.shape is type(None)):
                continue
            
            # GP9 480 = (848x480) which is not 16:9 by like 4px in width.....
            new_h = 476
            new_w = 848
            orig_h, orig_w, c = img.shape
            center_y = int(orig_h / 2)
            center_x = int(orig_w / 2)
            
            img = img[center_y - int(new_h / 2) : center_y + int(new_h / 2), center_x - int(new_w / 2) : center_x + int(new_w / 2)]
        
            # now we have 16:9 so we can scale down to models preferred 480x270 (which is 16:9 also)
            img = cv.resize(src=img, dsize=(480, 270))
            
            rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            self.processed_frames.append(Image.fromarray(rgb))
        
        # ! Model call happens here
        # We have modified predict_mitz() to return the result instead of printing it!
        if(len(self.processed_frames) < self.MODEL_ERROR_FRAME_PADDING*self.TARGET_FPS):
            self.current_result = 0 # ! If we discard the result for to less frames we just assume the lowest rating, since this only happens under ~15s or smth
            self.log('⚠️  To few frames collected, defaulting to rating 0 to prevent model crash.')
        else:
            self.log('🧮 Beginning evaluation.')
            # add 1 to the eval result, since lowest returned level (0) is one star
            self.current_result = 1 + predict_mitz.main('test-lul', self.processed_frames, 3, 'models/20240112_I3D_snip64_seg12-70_15_15-1632-best.pt', 12, 64)[0][1]
            self.log(f'👁️ Evaluation complete, rating {self.current_result - 1} = {self.current_result} star(s).')
        
        # we are done with eval and so actually ready to rerecord if user wants [Search REF002]
        self.recording_widget.set_state_ready_to_record_signal.emit()
        
        self.show_cleanup_widget_signal.emit()
    
    def send_gopro_command(self, command_path: str, params: dict[str, str] = {}, panic_on_failure = True):
        # remove first character if it's a slash 
        if command_path[0] == '/':
            command_path = command_path[1:]
        
        path = f'http://{self.GP_IP}:{self.GP_HTTP_PORT}/{command_path}'
        
        try:
            req = requests.get(url = path, params=params, timeout = 2.5)
            self.log(f'📡 Sent command \'{command_path}\' with params {params} to GoPro. Return code \'{req.status_code}\'.')
            
            if req.status_code != 200:
                raise ValueError(f'HTTP GET Return code was {req.status_code}, not 200.')
        except Exception as e:
            if panic_on_failure:
                self.log('🚨 A critical error occured! Software is terminating. Exception will be logged after cleanup attempt.', with_spacer=True)
                self.handle_application_close()
                raise type(e)(f'Request error under \'{path}\': {e}')
            else:
                self.log(f'⚠️  Request error under \'{path}\', however panic_on_failure is set to False for this request: {e}')
    
    def handle_application_close(self):
        self.log('♻️  Application closure initiated, running resource cleanup:', with_spacer=True)
        
        if self.recording:
            self.stop_recording(is_application_quit=True)
        
        self.send_gopro_command(command_path='/gopro/webcam/exit', panic_on_failure=False)
        # 59=auto power down; 4=5 minutes
        self.send_gopro_command(command_path='/gopro/camera/setting', params={'setting':'59', 'option':'4'}, panic_on_failure=False)
    
    @staticmethod
    def log(message: str, with_spacer=False):
        if with_spacer:
            print('[Hybparc] — — —')
        print(f'[Hybparc] {message}')

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName('HybParc Nahtstation')
    window = MainWindow()
    window.show()
    app.exec()