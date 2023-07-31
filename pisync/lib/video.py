from moviepy.editor import VideoFileClip
import time
import vlc

from pisync.lib.media import Media


class Video(Media):
    def play(self):
        #  creating vlc media player object
        media_player = vlc.MediaPlayer()

        # toggling full screen
        media_player.toggle_fullscreen()

        # media object
        media = vlc.Media(self.file_path)

        # setting media to the media player
        media_player.set_media(media)

        # start playing video
        media_player.play()

        time.sleep(self.duration)

        media_player.stop()

    @property
    def duration(self):
        try:
            clip = VideoFileClip(self.file_path)
            return clip.duration
        except Exception as e:
            print(f"Error while getting video duration: {e}")
            return None
