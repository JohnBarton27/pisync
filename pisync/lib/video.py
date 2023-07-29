import time
import vlc

from pisync.lib.media import Media


class Video(Media):
    def play(self, start_time: int = 0, end_time: int = None):
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

        while not media_player.is_playing():
            continue

        while media_player.is_playing():
            continue

        media_player.stop()
