#Cameo类，实现了视频流的截图、录屏、保存等操作。
import cv2
from managers import WindowManager, CaptureManager
import filters
import numpy
class Cameo(object):
    def __init__(self):
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(0), self._windowManager, True)
        self._curveFilter = filters.BGRPortraCurveFilter()

    def run(self):
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.enterFrame
           
           # filters.strokeEdges(frame_show,frame_show)
           # self._curveFilter.apply(frame_show,frame)

            self._captureManager.exitFrame()
            self._windowManager.processEvents()
    def onKeypress(self,keycode):
        if keycode == 32:  # space
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9:  # tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo('screenshot.avi')
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 27:    # escape
            self._windowManager.destoryWindow()
if __name__ == "__main__":
    Cameo().run()