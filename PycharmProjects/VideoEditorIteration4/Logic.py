from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from PIL import ImageGrab
import subprocess
import time
# Other Imports
import pyaudio
import wave
from PIL import Image, ImageFont, ImageDraw
import cv2
import numpy as np

class RSScreen(Screen):
    def recordScreen(self):
        # set duration and framesPerSecond to associated text input fields
        duration = int(self.duration.text)
        framesPerSecond = int(self.framespersecond.text)

        # Create frameCount variable for while loop
        frameCount = 0

        # For every frame in the video that will be recorded
        while frameCount != duration * framesPerSecond:

            # Start timer for screenshot
            timerStart = time.time()

            # Get RGB pixels from screen
            img = ImageGrab.grab()

            # Save the image with appropriate name, increment 1 for frameCounter and get compression ratio from associated text input
            img.save(
                "Frames/Frame" + str(frameCount).zfill(7)+ ".jpg",
                "JPEG", quality=int(self.cRatio.text))
            frameCount += 1

            # Finish Timer and work out the total delay to sleep for
            timerFinish = time.time()
            timeTaken = timerFinish - timerStart
            framePadDuration = (1 / framesPerSecond) - timeTaken

            # time.sleep() cannot be given value less than 0
            if (framePadDuration < 0):
                framePadDuration = 0

            time.sleep(framePadDuration)

        # ffmpeg command called via subprocess that creates a video file using images caputred previously, uses image2 demuxerm, pixel format is yuv420p, resoloution is 1920x1080
        # Also getss the file name from the associated text input and inserts it into the ffmpeg statment
        makeVidFromFrames = subprocess.call("C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -r " + str(
            framesPerSecond) + " -f image2 -s  1920x1080 -i Frames/Frame%07d.jpg  -vcodec mpeg4 -crf 25 -pix_fmt yuv420p Video/" + self.output.text + ".mp4",
                                            shell=True)

class RAScreen(Screen):
   def recordAudio(self):
       # Built in accordance to documentation at: https://people.csail.mit.edu/hubert/pyaudio/
       Format = pyaudio.paInt16
       Chunk = 1024
       Channels = 2
       Rate = 44100

       # Set duration and recording time
       recordTime = int(self.audioDuration.text)
       output = "Audio/ " + self.audioFileName.text + ".wav"

       # Creates an instance of pyAudio
       pyAudio = pyaudio.PyAudio()
       # Creates an audio stream with varibles assinged above
       audioStream = pyAudio.open(format=Format, channels=Channels, rate=Rate, input=True, frames_per_buffer=Chunk)
       # Initalises list for audio frames
       frames = []
       # Loop runs 43 times a second for the duration the user has specifie
       for i in range(0, int((Rate / Chunk) * recordTime)):
           # Reads chunk data from audio sream
           data = audioStream.read(Chunk)
           # Appends data read from audio stream to frames
           frames.append(data)

       # Stops and closes stream, terminates pyAudio object
       audioStream.stop_stream()
       audioStream.close()
       pyAudio.terminate()

       # Writes .wav audio file
       wav = wave.open(output, 'wb')
       wav.setnchannels(Channels)
       wav.setsampwidth(pyAudio.get_sample_size(Format))
       wav.setframerate(Rate)
       wav.writeframes(b''.join(frames))
       wav.close()

class RWScreen(Screen):
    def recordWebcam(self):
        framesPerSecond = int(self.webcamFPS.text)
        duration = int(self.webcamDuration.text)
        camera = cv2.VideoCapture(0)

        frameCount = 0
        while (frameCount != (framesPerSecond * duration)):
            timerStart = time.time()
            print(frameCount)
            ret, img = camera.read()
            cv2.imwrite("WebcamFrames/webcamFrame" + str(frameCount).zfill(7) + ".png", img)

            timeTaken = time.time() - timerStart
            print(timeTaken)
            frameDuration = 1 / framesPerSecond
            frameDuration -= timeTaken
            if (frameDuration > 0):
                time.sleep(frameDuration)

            # Increment
            frameCount += 1

        makeVidFromFrames = subprocess.call("C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -r " + str(
            framesPerSecond) + " -f image2 -s  1920x1080 -i WebcamFrames/webcamFrame%07d.png  -vcodec mpeg4 -crf 25 -pix_fmt yuv420p Video/" + self.webcamFileName.text + ".mp4",
                                            shell=True)

class TScreen(Screen):
            def createTitle(self):
                titleText = self.title.text
                font = self.font.text
                fnt = ImageFont.truetype("Fonts/" + font + ".ttf", 1)

                backgoundColor = self.bColor.text.split(",")
                fontColor = self.fontColor.text.split(",")

                img = Image.new("RGB", (1368, 912),
                                (int(backgoundColor[0]), int(backgoundColor[1]), int(backgoundColor[2])))
                # Scales font to fit screen
                fntSize = 1
                while fnt.getsize(titleText)[0] < 0.8 * 1368:
                    fntSize += 1
                    fnt = ImageFont.truetype("Fonts/" + font + ".ttf", fntSize)
                draw = ImageDraw.Draw(img)
                draw.text(xy=(136, 456 - fnt.getsize(titleText)[1] / 2), text=titleText,
                          fill=(int(fontColor[0]), int(fontColor[1]), int(fontColor[2])), font=fnt)
                img.save("Titles/" + self.titleFileName.text + ".png")

class JScreen(Screen):
    def join(self):
        # Gets user input
        vid1 = self.vid1.text
        vid2 = self.vid2.text
        output = self.output.text

        # Runs ffmpeg statement with user input
        joinVideos = subprocess.call('C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -i Video/' + vid1 + ' -i Video/' + vid2 + ' \
  -filter_complex "[0:0][1:0]concat=n=2:v=1:a=0 " \
    Video/'+ output + '.mp4')


class SScreen(Screen):
    def segment(self):
        # Gets user input
        vid = self.vid.text
        start = self.start.text
        end = self.end.text
        output = self.output.text

        # Runs ffmpeg statement with user input
        makeSegment = subprocess.call('C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe  -i Video/' + vid + ' -ss ' + start + ' -t ' + end + ' Video/' + output + '.mp4')

class AAScreen(Screen):
    def addAudio(self):
        # Gets user input
        vid = self.vid.text
        audio = self.audio.text
        output = self.output.text

        # Runs ffmpeg statement with user input
        AddAudio = subprocess.call('C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -i '+ vid + ' -i Video/' +  + ' -codec copy -shortest Video/' + output +'.mp4')

class ALScreen(Screen):
    def addLogo(self):
        # Gets user input
       vid = self.vid.text
       img = self.img.text
       placement = self.placement.text
       output = self.output.text

        # Change location in ffmpeg statment depending on user input, Default is bottom right
       placementString = ""
       if placement == "center":
           placementString = "overlay=(W-w)/2:(H-h)/2"
       elif placement == "bot_left":
           placementString = "overlay=5:main_h-overlay_h"
       elif placement == "top_left":
           placementString = "overlay=5:5"
       elif placementString == "top_right":
           placementString = "overlay=main_w-overlay_w-5:5"
       else:
           placementString = "overlay=main_w-overlay_w-5:main_h-overlay_h-5"

        # Runs ffmpeg statement with user input
       AddWatermark = subprocess.call('C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -i Video/'+ vid + ' -i ' + img + ' -filter_complex "' + placementString + '" -codec:a copy Video/' + output +'.mp4')

class IVScreen(Screen):
    def imgToVid(self):
        img = self.img.text
        duration = int(self.duration.text)
        output = self.output.text

        image = cv2.imread(img,1)
        image = cv2.resize(image, (1368, 912))
        imgS = img.split(".")

        # This is so that when looking for the ImagesTooVideo files it dosen't look for ImagesTooVideo/Titles/image.png if the orignal image is from the titles folder
        imgName = imgS[0].split("/")

        for index in range(duration):
            cv2.imwrite("ImagesTooVideo/" +
                        imgName[-1] + str(index).zfill(7) + ".png", image)

        makeVidFromFrames = subprocess.call("C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -r 1 -f image2 -s  1920x1080 -i ImagesTooVideo/" + imgName[-1] + "%07d.png -vcodec mpeg4 -crf 25 -pix_fmt yuv420p Video/" + self.output.text + ".mp4",
                                            shell=True)
class SpScreen(Screen):
    def changeSpeed(self):
        timerStart = time.time()
        # Sets video File Path
        videoFileName = self.vid.text
        output = self.output.text
        # Gets speed ratio for new video
        speedRatio = self.speed.text

        # FFmpeg commang that speeds up or slows down video depending on user input
        speedChange = subprocess.call('C:/ffmpeg-3.4-win64-static/bin/ffmpeg.exe -i Video/' + videoFileName + ' -filter:v "setpts=' + speedRatio + '*PTS" Video/' + output + '.mp4')
        print(time.time() - timerStart)

class MenuScreen(Screen):
    pass

class ScreenManager(ScreenManager):
    pass

class VideoEditorApp(App):
    def build(self):
        pass

if __name__ == "__main__":
    VideoEditorApp().run()