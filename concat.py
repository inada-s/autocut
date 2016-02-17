# coding: UTF-8
import os
import subprocess
from datetime import datetime
import sys

def main():
    os.chdir(os.path.dirname(os.sys.argv[0]))
    print os.getcwd()
    movie_list = os.sys.argv[1:]
    print movie_list
    for i in xrange(len(movie_list)):
        movie_list[i] = os.path.abspath(movie_list[i])
    with open("concat_tmp.txt", "w") as f:
        for movie in movie_list:
            print >>f, r"file '%s'" % movie
    datename = datetime.now().strftime("%Y%m%d-%H%M%S")
    name, ext = os.path.splitext(movie_list[0])
    command = [
        'ffmpeg',
        '-f', 'concat',
        '-i', 'concat_tmp.txt',
        '-codec', 'copy',
        os.path.join(os.path.dirname(movie_list[0]), "concat_" + datename + ext)
    ]
    print command
    with open("concat.log", "wb") as logfile:
        p = subprocess.call(' '.join(command), stderr=logfile)
    print "Press Enter Key To Exit."
    raw_input()

if __name__ == '__main__':
    main()

#ffmpeg -i concat:"201507120933390_001.ts|201507120933390_002.ts|201507120933390_003.ts|201507120933390_004.ts|201507120933390_005.ts|201507120933390_006.ts|201507120933390_007.ts|201507120933390_008.ts|201507120933390_009.ts|201507120933390_010.ts|201507120933390_011.ts|201507120933390_012.ts|201507120933390_013.ts|201507120933390_014.ts|201507120933390_015.ts|201507120933390_016.ts|201507120933390_017.ts|201507120933390_018.ts|201507120933390_019.ts|201507120933390_020.ts|201507120933390_021.ts|201507120933390_022.ts|201507120933390_023.ts" -c:v copy -c:a copy concat.ts
