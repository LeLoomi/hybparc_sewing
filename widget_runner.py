from PyQt6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    current_result: int = 0
    
    # Entry into the GUI
    def __init__(self):
        self.log('✌️  Booting up.')
        super().__init__()
                
        # Window setup
        self.showMaximized()
        self.setWindowTitle('Hybparc WIP Widget Runner')
        self.show_widget()
        

    def show_widget(self):
        pass

    @staticmethod
    def log(message: str):
        print(f'[WIP Widget Runner] {message}')

app = QApplication([])
window = MainWindow()
window.show()
app.exec()