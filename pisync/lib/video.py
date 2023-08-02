from moviepy.editor import VideoFileClip
import time
import vlc

from pisync.lib.media import Media


class Video(Media):

    media_player = None

    @classmethod
    def open_vlc(cls, fullscreen: bool = True):
        #  creating vlc media player object
        cls.media_player = vlc.MediaPlayer()

        if fullscreen:
            cls.media_player.toggle_fullscreen()

    def play(self):
        # media object
        media = vlc.Media(self.file_path)

        # setting media to the media player
        self.__class__.media_player.set_media(media)

        # start playing video
        self.__class__.media_player.play()

        if self.start_timecode:
            self.__class__.media_player.set_time(int(self.start_timecode * 1000))

        time.sleep(self.duration)

        self.__class__.media_player.stop()

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
