# autocut

autocut は 長時間録画したゲームの動画を, いい感じに1ゲームごとにカットするスクリプトです.

環境構築後、`python autocut.py preset foo-bar.mp4` で実行できます.

preset はディレクトリで, サンプルとして、`zdx`と`sf4`が入っています.

`start.png` に近いフレームを探し, その後 `end.png` に近いフレームが見つかったら, その区間を ffmpeg を使って無圧縮カットします.

config.txtはテキストファイルで, 以下の様なフォーマットをしています.
```
[offset]
start=-3
end=5
```
これは, start.png に似たフレームから3秒前をカット開始位置に設定し, end.png に似たフレームから5秒後をカット終了位置に設定するという意味です.

カットしたい動画のゲームや画質に合わせて、start.png, end.png, config.txt を設定してください. 

## Windows環境構築メモ 
1.python2.7.11のインストール
- https://www.python.org/downloads/
- 上部のリンクからmsiをダウンロードしてインストール

2.numpyのダウンロード
- https://sourceforge.net/projects/numpy/files/NumPy/1.10.4/
- numpy-1.10.4.zipをダウンロード
- コマンドプロンプトでzip解凍したフォルダ開いて、
- `python setup.py install`
- 参考)numpyのインストール方法 http://tokeigaku.blog.jp/python/numpy
- 手元だとこんなエラーがでた
```
error: Microsoft Visual C++ 9.0 is required (Unable to find vcvarsall.bat). Get　it from http://aka.ms/vcpython27
```
- URL踏んでダウンロード&インストール
- もう一度 `python setup.py install`
- 時間かかるので次のステップへ
- 終了時の最後のログ
```
Installed c:\python27\lib\site-packages\numpy-1.10.4-py2.7-win32.egg
Processing dependencies for numpy==1.10.4
Finished processing dependencies for numpy==1.10.4
```

3.OpenCVのダウンロード
- https://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.11/opencv-2.4.11.exe/download
- exe実行すると解凍場所を指定するよういわれるので指定して解凍する
- C:\直下を指定した(C:\opencv に解凍された)
- `C:\opencv\build\python\2.7\x86` の中にある `cv2.pyd` というファイルを `C:\Python27\Lib\site-packages` ディレクトリにコピーする
- `C:\opencv\sources\3rdparty\ffmpeg\opencv_ffmpeg.dll` を `C:\Python27\` にコピーして `opencv_ffmpeg2411.dll` にリネームする

4.動作チェック
- `C:\Python27\python.exe` を起動し
```
import cv2 [enter]
```
- と入力して何もエラーがでなければOK

5.ffmpegの入手
- http://ffmpeg.zeranoe.com/builds/
- から `ffmpeg-xxxxx-xxxxx-win64-static` をダウンロードして7zを解凍し、中にある `bin/ffmpeg.exe` をコピーしておいておく
