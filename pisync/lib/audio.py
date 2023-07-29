import pygame
import threading

from pisync.lib.media import Media


class Audio(Media):

    def play(self, start_time: int = 0, end_time: int = None):
        from pisync.lib.cue import Cue

        cues = Cue.get_for_source_media(self)

        timestamps = {}
        for cue in cues:
            timestamps[cue.source_media_timecode_secs] = {
                'media': cue.target_media,
                'played': False
            }

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play(start=start_time)
        while pygame.mixer.music.get_busy():
            current_time = (pygame.mixer.music.get_pos() + 1000 * start_time) / 1000
            print(f'Current time: {current_time}', end="\r")

            for timestamp in timestamps:
                if current_time >= timestamp:
                    if timestamps[timestamp].get('played'):
                        continue

                    # TODO make work for remote media
                    timestamps[timestamp]['played'] = True
                    cue_thread = threading.Thread(target=timestamps[timestamp]['media'].play)
                    cue_thread.start()

            if end_time and current_time >= end_time:
                pygame.mixer.music.stop()
                return

            continue
