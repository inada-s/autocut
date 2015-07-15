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
        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, min(self.curpos() + num, self.frame_count))

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
            '-ss', str(begin_sec),
            '-i', self.file_path,
            '-t', str(length_sec),
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_file_name
        ]
        print "popen", self.command
        self.p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def wait(self):
        if self.p:
            self.p.wait()

def main():
    script_path = os.path.dirname(sys.argv[0])
    preset = sys.argv[1]
    movie_file = sys.argv[2]
    preset_path = os.path.join(script_path, preset)

    conf = ConfigParser.SafeConfigParser()
    conf.read(os.path.join(preset_path, 'config.txt'))
    start_offset = int(conf.get('offset', 'start'))
    end_offset = int(conf.get('offset', 'end'))
    video = VideoLoader(movie_file)
    start = TemplateImage(os.path.join(preset_path, 'start.png'))
    end = TemplateImage(os.path.join(preset_path, 'end.png'))

    between = False
    section_list = []
    section_start = 0
    section_end = 0
    bar = CUIProgressBar()

    cutman = None
    number = 1
    while(video.available()):
        video.seek_frame(video.fps)
        ret, frame = video.next()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not between:
            rect, max_value = start.match(gray)
            if max_value >= 0.70:
                section_start = video.curpos() + video.fps * start_offset
                between = True
        else:
            rect, max_value = end.match(gray)
            if max_value >= 0.70:
                section_end = video.curpos() + video.fps * end_offset
                section_list.append((section_start, section_end))
                base_name, ext = os.path.splitext(movie_file)
                cutman = SubProcessCut(movie_file)
                cutman.run( section_start / video.fps,
                            (section_end - section_start) / video.fps,
                            base_name + '_%03d' % number + ext)
                number += 1
                section_start, section_end = 0, 0
                print "section_list", section_list
                between = False
        bar.update(float(video.curpos()) / video.frame_count)
    if cutman:
        cutman.wait()
        print "waiting cut process..."

if __name__ == '__main__':
    main()

