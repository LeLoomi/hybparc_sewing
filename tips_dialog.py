from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QDialog
from PyQt6.QtCore import Qt

class TipsDialog(QDialog):
    
    levelHints = [
        '''Für diese Auswertungsstufe ist leider kein weiterer Tip verfügbar.''',
        '''<li style="margin-bottom: 1em;">Wiederhole dein Wissen über die Einzelknopfnaht und spiele den Bewegungsablauf zunächst in Gedanken durch. Dies kann helfen, den Ablauf des Eingriffs zu verinnerlichen, besser vorauszuplanen und flüssiger zu nähen.</li>
        <li style="margin-bottom: 1em;">Achte darauf, dass die Wundränder gut adaptiert sind und nicht klaffen, aber vermeide zu viel Spannung oder gar eine Inversion der Wundränder.</li>
        <li style="margin-bottom: 1em;">Je öfter du übst, desto sicherer und souveräner wird auch Dein Umgang mit den Instrumenten.</li>''',
        '''<li style="margin-bottom: 1em;">Versuche deine Bewegungsabläufe weiter zu optimieren und auf unnötige Bewegungen zu verzichten. So wirst du noch effizienter.</li>
        <li>Achte darauf, dass dein Nahtergebnis gleichmäßig ist und die Nähte korrekt zueinander ausgerichtet sind. Vermeide zu viel Spannung oder gar eine Inversion der Wundränder. Dagegen ist eine leichte Eversion der Wundränder bei einer Hautnaht meist erwünscht.</li>
        ''',
        '''<li style="margin-bottom: 1em;">Um dich weiter zu verbessern, achte stets auf einen sorgsamen Umgang mit dem Gewebe, um versehentliche Schäden zu vermeiden.</li>
        <li style="margin-bottom: 1em;">Für viele Patient:innen steht eine kosmetisch ansprechende Naht stellvertretend für gute chirurgische Arbeit. Achte daher stets auf eine exakte, spannungsfreie Adaption der Wundränder sowie ein sauberes Nahtbild.</li>
        <li style="margin-bottom: 1em;">Je mehr du übst, desto routinierter und müheloser wird deine Nahttechnik.</li>'''
    ]
    
    def __init__(self, level_to_hint_about: int):
        super().__init__()
        self.setWindowTitle("Tips zur Auswertung")
        self.showMaximized()
        
        textLabel = QLabel(f'<ol>{self.levelHints[level_to_hint_about]}</ol>')
        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)
        textLabel.setTextFormat(Qt.TextFormat.RichText)
        textLabel.setWordWrap(True)

        okButton = QPushButton("Schließen")
        okButton.setFont(font)
        okButton.clicked.connect(self.close)

        mainLayout = QVBoxLayout()
        mainLayout.addSpacing(70)
        mainLayout.addWidget(textLabel)
        mainLayout.addSpacing(70)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)
        self.setMinimumWidth(1200)