import pygame
import requests
import threading
from urllib.parse import urlparse
from urllib.request import pathname2url

from pisync.lib.client import Client
from pisync.lib.media import Media
from pisync.lib.message import MediaPlayRequestMessage

import settings


class Audio(Media):

    def play(self):
        start = self.start_timecode if self.start_timecode else 0.0

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
        pygame.mixer.music.play(start=start)
        while pygame.mixer.music.get_busy():
            current_time = (pygame.mixer.music.get_pos() + 1000 * start) / 1000
            print(f'Current time: {current_time}', end="\r")

            for timestamp in timestamps:
                if current_time >= timestamp:
                    if timestamps[timestamp].get('played'):
                        continue

                    timestamps[timestamp]['played'] = True
                    target_media = timestamps[timestamp]['media']

                    if target_media.client_id:
                        requests.post(f'http://0.0.0.0:{settings.API_PORT}/play/{target_media.db_id}')
                    else:
                        # Local
                        cue_thread = threading.Thread(target=target_media.play)
                        cue_thread.start()

            if self.end_timecode and current_time >= self.end_timecode:
                pygame.mixer.music.stop()
                return

            continue
