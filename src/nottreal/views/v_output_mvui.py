
from ..utils.log import Logger
from ..models.m_mvc import VUIState
from .v_output_abstract import AbstractOutputView

from PySide2.QtWidgets import (QGridLayout, QGraphicsOpacityEffect, QLabel,
                               QScrollArea, QSizePolicy, QWidget)
from PySide2.QtGui import (QBrush, QColor, QFont, QPainter, QPainterPath,
                           QPalette, QPen, QRadialGradient)
from PySide2.QtCore import (Qt, QEasingCurve, QEventLoop, QPoint, QPointF,
                            QPropertyAnimation, QRectF, QSizeF, QTimer,
                            Slot)

import math


class MVUIWindow(AbstractOutputView):
    """
    A Mobile VUI-like output.

    Extends:
        QMainWindow
    """
    def __init__(self, nottreal, args, data, config):
        """
        A simple mobile-like VUI

        Arguments:
            nottreal {App} -- Main NottReal class
            args {[str]} -- CLI arguments
            data {TSVModel} -- Data from static data files
            config {ConfigModel} -- Data from static configuration files
        """
        super(MVUIWindow, self).__init__(nottreal, args, data, config)

    def init_ui(self):
        """Initialise the UI"""
        Logger.debug(__name__, 'Initialising the MVUI window')

        self._background_colour = self.config.get('MVUI', 'background_colour')

        self.setWindowTitle(self.config.get('MVUI', 'window_title'))
        self.setStyleSheet('background-color: %s' % self._background_colour)

        self.setGeometry(800, 10, 700, 800)

        # create the layout
        layout = QGridLayout()
        layout.setVerticalSpacing(100)
        layout.setHorizontalSpacing(100)
        self.setLayout(layout)

        layout.setRowStretch(0, .5)

        # create the message widget
        default_msg = self.nottreal.config.get('MVUI', 'initial_text')
        self.message = MessageWidget(self, default_msg)
        layout.addWidget(self.message, 1, 1)
        layout.setRowStretch(1, 10)

        layout.setRowStretch(2, .5)

        # create the state widget (i.e. the orb)
        self.state = Orb(self, VUIState.BUSY)
        layout.addWidget(self.state, 3, 1)
        layout.setRowStretch(3, 0)
        layout.setRowMinimumHeight(3, self.state.size_max)

        layout.setRowStretch(4, .5)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 10)
        layout.setColumnStretch(2, 1)

    def activated(self):
        return True

    def get_label(self):
        return 'Mobile VUI'

    def set_message(self, text):
        """
        A new message to show immediately

        Arguments:
          text {str} -- Text of the message
        """
        self.message.set(text)

    def set_state(self, state):
        """
        Update the displayed state of the VUI

        Arguments:
            state {models.VUIState} -- New state of the VUI
        """
        self.state.set(state)

    def toggle_visibility(self):
        """
        Toggle visibility of the window. If the window
        is going to be hidden, sets the state to resting.
        """
        super().toggle_visibility()

        if not self.is_visible():
            self.set_state(VUIState.RESTING)
        else:
            state = self.nottreal.responder('wizard').state
            self.set_state(state)


class MessageWidget(QScrollArea):
    """
    Text displayed in the UI

    Extends:
        {QScrollArea}

    Variables:
        DOUBLE_CLICK_TIMER {int} -- Two clicks in this many ms is
            a double click
        ID, LABEL, TEXT {int} -- Column IDs for the prepared messages
            list
    """
    DOUBLE_CLICK_TIMER = 450
    ID, LABEL, TEXT = range(3)

    def __init__(self, parent, default):
        """
        Create the label that'll show the messages to the user

        Arguments
            parent {QWidget} -- Parent widget
            default {str} -- Default/inital text
        """
        self.parent = parent
        self._cfg = parent.nottreal.config

        super(MessageWidget, self).__init__(parent)

        self.setWidgetResizable(True)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # create the label
        typeface = self._cfg.cfg().get('MVUI', 'typeface')
        font_size = self._cfg.cfg().getint('MVUI', 'font_size')
        text_colour = self._cfg.cfg().get('MVUI', 'text_colour')

        self._label = QLabel('<p class="text-align: center;">%s</p>' % default)
        self._label.setTextFormat(Qt.RichText)
        self._label.setWordWrap(True)
        self._label.setFont(QFont(typeface, font_size, QFont.Bold))
        self._label.setStyleSheet('color: ' + text_colour)
        self._label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self._label.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.Maximum)
        self._label.setWindowOpacity(0)

        self.setWidget(self._label)

        self.effect = QGraphicsOpacityEffect()
        self._label.setGraphicsEffect(self.effect)
        self._animation = QPropertyAnimation(self.effect, b'opacity')
        self._fade_in()

    @Slot()
    def _change_colour(self, color):
        palette = self.palette()
        palette.setColor(QPalette.WindowText, color)
        self.setPalette(palette)

    def _fade_in(self):
        """
        Fade the text in

        From https://stackoverflow.com/questions/48191399/pyqt-fading-a-qlabel
        """
        self._animation.stop()
        self._animation.setStartValue(0)
        self._animation.setEndValue(1)
        self._animation.setDuration(350)
        self._animation.setEasingCurve(QEasingCurve.InBack)
        self._animation.start()

    def _fade_out(self):
        """
        Fade the text out

        From https://stackoverflow.com/questions/48191399/pyqt-fading-a-qlabel
        """
        self._animation.setStartValue(1)
        self._animation.setEndValue(0)
        self._animation.setDuration(350)
        self._animation.setEasingCurve(QEasingCurve.OutBack)
        self._animation.start()

    def set(self, text):
        """
        Change the message displayed

        Arguments:
            text {str} -- New message to show
        """
        html = '<p class="text-align: center">%s</p>' % text

        self._fade_out()
        loop = QEventLoop()
        self._animation.finished.connect(loop.quit)
        loop.exec_()

        self._label.setText(html)

        self._fade_in()
        loop = QEventLoop()
        self._animation.finished.connect(loop.quit)
        loop.exec_()


class Orb(QWidget):
    """
    Orb that shows the state of the VUI.

    Extends:
        {QWidget}

    Variables:
        FADE_OUT {int} -- Type used to determine opacity changing directions
        FADE_IN {int} -- Type used to determine opacity changing directions
        CALC_VOL_EVERY_MS {float} -- Frequency to recalculate the volume
        SPEAKING_MIN_OPACITY {int} -- Minimum opacity for speaking glow
        SPEAKING_OPACITY_CHANGE {int} -- Change in opacity per frame (/1)
        BUSY_SLICE_CHANGE {int} -- Movement of slice per frame (/1)
        STATE_FADE_OPACITY {int} -- Change in opacity per frame (/1)
        REPAINT_EVERY_MS {float} -- How often to repaint (milliseconds)
    """
    NO_FADE, FADE_OUT, FADE_IN = range(0, 3)

    CALC_VOL_EVERY_MS = int(1/2*1000)

    SPEAKING_MIN_OPACITY = .55
    SPEAKING_OPACITY_CHANGE = .02
    BUSY_SLICE_CHANGE = 8
    STATE_FADE_OPACITY = .12

    REPAINT_EVERY_MS = 1/12*1000

    def __init__(self, parent, default):
        """
        Create the orb container

        Arguments
            parent {QWidget} -- Parent widget
            default {int} -- Default/initial state
        """
        self.parent = parent
        super(Orb, self).__init__(parent)

        self._state = default

        self.FADE_STEPSIZE = math.ceil(255 / self.STATE_FADE_OPACITY)
        self._previous_state = None
        self._previous_state_opacity = 0

        cfg = parent.nottreal.config.cfg()

        # initial sizes
        self._border_width = cfg.getint('MVUI', 'orb_width')
        double_border = 2*self._border_width
        self._size = cfg.getint('MVUI', 'orb_size')
        self._sizef = self._get_sizef(self._size, double_border)
        self._rectf = QRectF(QPointF(0, 0), self._sizef)

        self.size_max = cfg.getint('MVUI', 'orb_size_max')
        self._sizef_max = self._get_sizef(self.size_max)

        self._y_offset = (self._sizef_max.height() - self._size) / 2

        # create orb base and glow circles
        self._border = {}
        self._border_glow = {}
        self._border[VUIState.RESTING] = cfg.get('MVUI', 'orb_resting')
        self._border[VUIState.LISTENING] = cfg.get('MVUI', 'orb_listening')
        self._border[VUIState.BUSY] = cfg.get('MVUI', 'orb_busy')
        self._border[VUIState.SPEAKING] = cfg.get('MVUI', 'orb_speaking')

        # speaking glow
        self._speaking_fade_opacity = 255
        self._speaking_fade_direction = self.FADE_OUT

        # computing slice
        self._computing_slice_angle = 90

        # enable fluttering?
        self._enable_flutter = cfg.getboolean('MVUI', 'orb_enable_flutter')
        if not self._enable_flutter:
            Logger.info(__name__, 'Volume flutter is disabled')

        self._flutter = 0.4

        # start drawing
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(self.REPAINT_EVERY_MS)

    def _get_sizef(self, size, border=0):
        """
        Calculate the QSizeF, reducing dimensions by the border size

        Arguments:
            size {int} -- Size of the overall orb including border

        Keyword Arguments:
            border {int} -- Border size (default: {0})

        Returns:
            QSizeF -- Size of the orb (excluding border)
        """
        offset_size = size - border
        return QSizeF(offset_size, offset_size)

    def _set_flutter_intensity(self, volume_norm):
        """
        Use the volume level to adjust the flutter

        Arguments:
            volume_norm {float} -- Normalised volume level
        """
        self._flutter = max(
                min(
                    math.sin(volume_norm + self._flutter_variation * 1.4),
                    .8
                ),
                self._flutter_variation
            )

        if self._flutter_variation_dir is self.FADE_OUT:
            self._flutter_variation -= .002
        else:
            self._flutter_variation += .002

        if self._flutter_variation > .4:
            self._flutter_variation_dir = self.FADE_OUT
        elif self._flutter_variation < .3:
            self._flutter_variation_dir = self.FADE_IN

    def paintEvent(self, e):
        """
        Repaint the orb

        Arguments:
            e {QPaintEvent} -- Event for painting
        """
        width = e.rect().width()
        x_offset = (width - self._size) / 2

        # fade out the previous state
        if self._previous_state_opacity < 0:
            if self._previous_state == VUIState.SPEAKING:
                self.paint_speaking_orb(
                    colour=self._border[self._previous_state],
                    opacity=-self._previous_state_opacity,
                    x_offset=x_offset)
            elif self._previous_state == VUIState.LISTENING:
                self.paint_listening_orb(
                    colour=self._border[self._previous_state],
                    opacity=-self._previous_state_opacity,
                    x_offset=x_offset,
                    width=width)
            elif self._previous_state == VUIState.BUSY:
                self.paint_computing_orb(
                    colour=self._border[self._previous_state],
                    opacity=-self._previous_state_opacity,
                    x_offset=x_offset)
            else:
                self.paint_base_orb(
                    colour=self._border[self._previous_state],
                    opacity=-self._previous_state_opacity,
                    x_offset=x_offset)

            self._previous_state_opacity += self.STATE_FADE_OPACITY

        # fade in the new state
        if (self._previous_state_opacity > -1
                and self._previous_state_opacity <= 1):
            if self._state is VUIState.SPEAKING:
                self.paint_speaking_orb(
                    colour=self._border[self._state],
                    opacity=self._previous_state_opacity,
                    x_offset=x_offset)
            elif self._state is VUIState.LISTENING:
                self.paint_listening_orb(
                    colour=self._border[self._state],
                    opacity=self._previous_state_opacity,
                    x_offset=x_offset,
                    width=width)
            elif self._state is VUIState.BUSY:
                self.paint_computing_orb(
                    colour=self._border[self._state],
                    opacity=self._previous_state_opacity,
                    x_offset=x_offset)
            else:
                self.paint_base_orb(
                    colour=self._border[self._state],
                    opacity=self._previous_state_opacity,
                    x_offset=x_offset)

            self._previous_state_opacity = \
                min(1, self._previous_state_opacity + self.STATE_FADE_OPACITY)

    def paint_base_orb(self, colour, opacity, x_offset):
        """
        Paint the base orb (hollow circle)

        Arguments:
            colour {str} -- Colour to make the circle
            opacity {float} -- Opacity of the circle (0--1)
            x_offset {float} -- Offset from 0 to start painting
        """
        qp_orb = QPainter()
        qp_orb.begin(self)
        qp_orb.setRenderHint(QPainter.Antialiasing)

        qp_orb.setPen(
            QPen(
                QColor(colour),
                self._border_width,
                Qt.SolidLine,
                Qt.FlatCap,
                Qt.MiterJoin))

        qp_orb.setBrush(QColor(self.parent._background_colour))
        qp_orb.setOpacity(opacity)
        qp_orb.drawEllipse(self._rectf.translated(x_offset, self._y_offset))

    def paint_speaking_orb(self, colour, opacity, x_offset):
        """
        Paint the Speaking orb (by default, a pink hollow circle which
        fades its opacity in and out)

        Arguments:
            colour {str} -- Colour to make the circle
            opacity {float} -- Opacity of the circle (0--1)
            x_offset {float} -- Offset from 0 to start painting
        """
        if opacity == 1:
            if self._speaking_fade_opacity <= self.SPEAKING_MIN_OPACITY:
                self._speaking_fade_direction = self.FADE_IN
            elif self._speaking_fade_opacity >= 1:
                self._speaking_fade_direction = self.FADE_OUT

            self.paint_base_orb(
                colour,
                self._speaking_fade_opacity,
                x_offset)

            if self._speaking_fade_direction == self.FADE_IN:
                self._speaking_fade_opacity += self.SPEAKING_OPACITY_CHANGE
            else:
                self._speaking_fade_opacity -= self.SPEAKING_OPACITY_CHANGE

        else:
            self._speaking_fade_opacity = 1
            self._speaking_fade_direction = self.FADE_OUT

            self.paint_base_orb(
                colour,
                opacity,
                x_offset)

    def paint_listening_orb(self, colour, opacity, x_offset, width):
        """
        Paint the Listening orb (by default, a purple hollow circle
        with a filled fluttering circle based on the volume)

        Arguments:
            colour {str} -- Colour to make the circle
            opacity {float} -- Opacity of the circle (0--1)
            x_offset {float} -- Offset from 0 to start painting
        """
        opacity = max(self._flutter, opacity)
        qp_orb = QPainter()
        qp_orb.begin(self)
        qp_orb.setRenderHint(QPainter.Antialiasing)

        gradient = QRadialGradient(QPoint(width, width), width/2)
        gradient.setColorAt(0, QColor(0, 0, 0, 1))
        gradient.setColorAt(1, colour)

        qp_orb.setBrush(
            QBrush(gradient))
        qp_orb.setPen(
            QPen(
                QColor(colour),
                self._border_width,
                Qt.SolidLine,
                Qt.FlatCap,
                Qt.MiterJoin))

        qp_orb.setOpacity(self._flutter)
        qp_orb.drawEllipse(self._rectf.translated(x_offset, self._y_offset))

    def paint_computing_orb(self, colour, opacity, x_offset):
        """
        Paint the Computing orb (by default, a white hollow circle with
        a 'slice'/wedge missing).

        Arguments:
            colour {str} -- Colour to make the circle
            opacity {float} -- Opacity of the circle (0--1)
            x_offset {float} -- Offset from 0 to start painting
        """
        self.paint_base_orb(colour, opacity, x_offset)

        path_slice = QPainterPath()
        ax = self._size + self._border_width
        ay = 0

        bx = self._size/2
        by = self._size + self._border_width

        path_slice.moveTo(0, 0)
        path_slice.lineTo(ax, ay)
        path_slice.lineTo(bx, by)
        path_slice.lineTo(0, 0)
        self._computing_slice = path_slice

        qp_slice = QPainter()
        qp_slice.begin(self)
        qp_slice.setRenderHint(QPainter.Antialiasing)

        centrex = x_offset - self._border_width + (self._size/2)
        centrey = self._y_offset - self._border_width + (self._size/2)

        qp_slice.save()
        qp_slice.translate(centrex, centrey)
        qp_slice.rotate(self._computing_slice_angle)

        qp_slice.setOpacity(opacity)

        qp_slice.fillPath(
            self._computing_slice,
            QColor(self.parent._background_colour))
        qp_slice.restore()

        self._computing_slice_angle = \
            (self._computing_slice_angle + self.BUSY_SLICE_CHANGE) % 360

    def set(self, state):
        """
        Update the Orb with thew new state

        Arguments:
            state {int} -- State from {VUIState}
        """
        listening = VUIState.LISTENING

        if self._enable_flutter:
            if (not self.parent.is_visible() and state is listening) \
                    or (self._state is not listening and state is listening):

                self._flutter_variation = .2
                self._flutter_variation_dir = self.FADE_IN

                self.parent.nottreal.router(
                    'input',
                    'register_volume_callback',
                    name='MVUI',
                    method=self._set_flutter_intensity)

            if (not self.parent.is_visible() and self._state is listening) \
                    or (self._state is listening and state != listening):
                self.parent.nottreal.router(
                    'input',
                    'deregister_volume_callback',
                    name='MVUI')

            if self._previous_state_opacity > 0:
                self._previous_state = self._state
                self._previous_state_opacity = -self._previous_state_opacity

        self._state = state
