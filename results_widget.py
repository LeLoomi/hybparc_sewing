from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ResultsWidget(QWidget):
    new_try_requested_signal = pyqtSignal()
    
    star_size: QSize = QSize(90, 90)
    grey: QColor = QColor.fromString("#C3C3C3")
    jelly_blue: QColor = QColor.fromString("#4287f5")
    
    def __init__(self, result_to_display: int):
        super().__init__()

        # +++ 3 star segment +++
        # We use icon here, since SVG -> Icon -> Pixmap has higher base resolution than SVG -> Pixmap pipeline
        starIcon = QIcon("./graphics/star-solid.svg")
        starPixmap = starIcon.pixmap(self.star_size, QIcon.Mode.Normal, QIcon.State.On)

        firstStarLabel = QLabel()
        firstStarLabel.setPixmap(self.recolor_pixmap(starPixmap, self.grey))
        firstStarLabel.setFixedSize(self.star_size)
        
        secondStarLabel = QLabel()
        secondStarLabel.setPixmap(self.recolor_pixmap(starPixmap, self.grey))
        secondStarLabel.setFixedSize(self.star_size)
        
        thirdStarLabel = QLabel()
        thirdStarLabel.setPixmap(self.recolor_pixmap(starPixmap, self.grey))
        thirdStarLabel.setFixedSize(self.star_size)
        
        # ! setting colors depending on how the score is
        if(result_to_display >= 0):
            firstStarLabel.setPixmap(self.recolor_pixmap(starPixmap, self.jelly_blue))
        if(result_to_display >= 1):
            secondStarLabel.setPixmap(self.recolor_pixmap(starPixmap, self.jelly_blue))
        if(result_to_display >= 2):
            thirdStarLabel.setPixmap(self.recolor_pixmap(starPixmap, self.jelly_blue))

        
        starLayout = QHBoxLayout()
        starLayout.addStretch()
        starLayout.addWidget(firstStarLabel)
        starLayout.addWidget(secondStarLabel)
        starLayout.addWidget(thirdStarLabel)
        starLayout.addStretch()
        # --- 3 star segment ---

        textLabel = QLabel('Auswertung abgeschlossen.')
        textLabel.setTextFormat(Qt.TextFormat.RichText)

        font = textLabel.font()
        font.setPointSize(28)
        textLabel.setFont(font)

        iconTextLayout = QHBoxLayout()
        iconTextLayout.addStretch()
        iconTextLayout.addWidget(textLabel)
        iconTextLayout.addStretch()

        self.controlButton = QPushButton('Neuer Durchlauf')
        self.controlButton.clicked.connect(self.start_new_try)
        self.controlButton.setFont(font)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.controlButton)
        buttonLayout.addStretch()
        
        contentLayout = QVBoxLayout()
        contentLayout.addStretch()
        contentLayout.addLayout(starLayout)
        contentLayout.addLayout(iconTextLayout)
        contentLayout.addLayout(buttonLayout)
        contentLayout.addStretch()

        mainLayout = QHBoxLayout()
        mainLayout.addStretch()
        mainLayout.addLayout(contentLayout)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
    
    def start_new_try(self):
        self.new_try_requested_signal.emit()
    
    # Does not mutate in place.
    def recolor_pixmap(self, pixmap: QPixmap, color: QColor) -> QPixmap:
        _pixmap = pixmap.copy()
        mask = _pixmap.createMaskFromColor(QColor('black'), Qt.MaskMode.MaskOutColor)
        _pixmap.fill(color)
        _pixmap.setMask(mask)
        return _pixmap