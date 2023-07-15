import pygame

from pisync.lib.media import Media


class Audio(Media):

    def play(self, start_time: int = 0, end_time: int = None):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play(start=start_time)
        while pygame.mixer.music.get_busy():
            current_time = (pygame.mixer.music.get_pos() + 1000 * start_time) / 1000
            print(f'Current time: {current_time}', end="\r")

            if end_time and current_time >= end_time:
                pygame.mixer.music.stop()
                return

            continue
