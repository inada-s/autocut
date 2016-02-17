# coding: UTF-8
import autocut
import os, sys

if __name__ == '__main__':
    script_path = os.path.dirname(sys.argv[0])
    preset_path = os.path.join(script_path, "zdx2")
    movie_file = os.path.abspath(sys.argv[1])
    os.chdir(script_path)
    autocut.main(preset_path, movie_file)
