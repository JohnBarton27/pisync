import datetime
from moviepy.editor import VideoFileClip
import time
from typing import ClassVar
import vlc

from pisync.lib.media import Media


class Video(Media):

    media_player: ClassVar = None

    @classmethod
    def set_black_screen(cls):
        black_screen = vlc.Media('static/img/full_black.png')

        cls.media_player.set_media(black_screen)
        cls.media_player.play()

        time.sleep(2)

    @classmethod
    def open_vlc(cls, fullscreen: bool = True):
        try:
            #  creating vlc media player object
            cls.media_player = vlc.MediaPlayer()

            if fullscreen:
                cls.media_player.toggle_fullscreen()

            cls.set_black_screen()
        except:
            print('Unable to open VLC! Will try again...')
            time.sleep(10)
            cls.open_vlc(fullscreen=fullscreen)

    def play(self, app):
        # media object
        media = vlc.Media(self.file_path)

        # setting media to the media player
        self.__class__.media_player.set_media(media)

        # start playing video
        self.__class__.media_player.play()

        if self.start_timecode:
            self.__class__.media_player.set_time(int(self.start_timecode * 1000))

        start_time = datetime.datetime.now()
        while True:
            current_time = datetime.datetime.now()

            elapsed = current_time - start_time
            if elapsed.total_seconds() >= self.duration or self.stop_signal:
                self.__class__.set_black_screen()
                break

    @property
    def duration(self):
        try:
            clip = VideoFileClip(self.file_path)

            if self.start_timecode and not self.end_timecode:
                return clip.duration - self.start_timecode
            elif self.start_timecode and self.end_timecode:
                return self.end_timecode - self.start_timecode
            elif not self.start_timecode and self.end_timecode:
                return self.end_timecode
            else:
                # No start or end time side
                return clip.duration
        except Exception as e:
            print(f"Error while getting video duration: {e}")
            return None
