# coding: UTF-8
import numpy as np
import cv2
import sys
import time
import os
import subprocess
import ConfigParser

class TemplateImage():
    def __init__(self, path):
        self.name = path
        self.img = cv2.imread(path, 0)
        self.w, self.h = self.img.shape[::-1] 
        self.last_result = None

    def match(self, img):
        res = cv2.matchTemplate(img, self.img, eval("cv2.TM_CCOEFF_NORMED"))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) 
        top_left = max_loc
        bottom_right = (top_left[0] + self.w, top_left[1] + self.h)
        self.last_result = (top_left, bottom_right), max_val
        return self.last_result

    def imshow(self, name = ""):
        if name == "":
            name = self.name
        cv2.imshow(name, self.img)

class VideoLoader():
    def __init__(self, path):
        self.name = path
        self.cap = cv2.VideoCapture(path)
        self.frame_count = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
        return 

    def __del__(self):
        self.cap.release()

    def next(self):
        return self.cap.read()

    def curpos(self):
        return int(self.cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))

    def seek_frame(self, num):
        result = True
        frame = self.curpos() + num
        if frame > self.frame_count:
            frame = self.frame_count
            result = False
        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame)
        return result

    def available(self):
        return self.cap.isOpened()

class CUIProgressBar():
    def __init__(self, width=20):
        self.width = width

    def update(self, ratio):
        hashes = '#' * int(round(ratio * self.width))
        spaces = ' ' * (self.width - len(hashes))
        sys.stdout.write("\rProgress : [{0}] {1}%".format(hashes + spaces, int(round(ratio * 100))))
        sys.stdout.flush()

class SubProcessCut():
    def __init__(self, file_path):
        self.file_path = file_path
        self.p = None

    def run(self, begin_sec, length_sec, output_file_name):
        self.command = [
            'ffmpeg',
            '-y',
            '-ss', str(begin_sec),
            '-i', self.file_path,
            '-t', str(length_sec),
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_file_name
        ]
        print "popen", self.command
        with open("stderr.log", "wb") as logfile:
            self.p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=logfile, shell=False)

    def wait(self):
        if self.p:
            self.p.wait()

def main():
    script_path = os.path.dirname(sys.argv[0])
    preset = sys.argv[1]
    movie_file = sys.argv[2]
    preset_path = os.path.join(script_path, preset)
    print "preset:", preset
    print "movie:", movie_file

    conf = ConfigParser.SafeConfigParser()
    conf.read(os.path.join(preset_path, 'config.txt'))
    start_offset = int(conf.get('offset', 'start'))
    end_offset = int(conf.get('offset', 'end'))
    video = VideoLoader(movie_file)
    start = TemplateImage(os.path.join(preset_path, 'start.png'))
    end = TemplateImage(os.path.join(preset_path, 'end.png'))
    start_th = float(conf.get('thratio', 'start'))
    end_th = float(conf.get('thratio', 'end'))
    behind_start = int(conf.get('option', 'behind_start'))

    if not video.available():
        print "video load error"
        return

    between = False
    section_list = []
    section_start = 0
    section_end = 0
    bar = CUIProgressBar()

    cutman = None
    number = 1

    #cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    while(video.available()):
        ret, frame = video.next()

        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if behind_start or not between:
            rect, max_value = start.match(gray)
            print "s", max_value,
            if max_value >= start_th:
                section_start = video.curpos() + video.fps * start_offset
                print "section start", video.curpos(), section_start
                #cv2.imshow("image", frame)
                if section_start < 0:
                    section_start = 0
                between = True

        if between:
            rect, max_value = end.match(gray)
            print "e", max_value,
            if max_value >= end_th:
                print "section end"
                section_end = video.curpos() + video.fps * end_offset
                if section_end > video.frame_count:
                    section_end = video.frame_count
                section_list.append((section_start, section_end))
                base_name, ext = os.path.splitext(movie_file)
                cutman = SubProcessCut(movie_file)
                cutman.run( float(section_start) / video.fps,
                            float(section_end - section_start) / video.fps,
                            base_name + '_%03d' % number + ext)
                number += 1
                section_start, section_end = 0, 0
                print "section_list", section_list
                between = False
        bar.update(float(video.curpos()) / video.frame_count)
        if not video.seek_frame(video.fps):
            break
        #cv2.waitKey(1)
    if cutman:
        cutman.wait()
        print "waiting cut process..."
    #cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

