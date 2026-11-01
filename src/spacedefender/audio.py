import logging
import math
from array import array
from collections.abc import Callable

import pygame


SAMPLE_RATE = 22050
logger = logging.getLogger(__name__)


class AudioManager:
    def __init__(self) -> None:
        self.enabled = False
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
        except pygame.error as error:
            logger.warning("Audio is unavailable: %s", error)
            return

        self.enabled = True
        self.sample_rate = pygame.mixer.get_init()[0]
        pygame.mixer.set_num_channels(max(8, pygame.mixer.get_num_channels()))
        self._music_channel = pygame.mixer.Channel(0)
        self._cue_channel = pygame.mixer.Channel(1)
        self._battle_music = self._make_sound(8.0, self._battle_sample, 0.28)
        self._shot = self._make_sound(0.14, self._shot_sample, 0.38)
        self._laser = self._make_sound(0.28, self._laser_sample, 0.42)
        self._drumroll = self._make_sound(1.5, self._drumroll_sample, 0.55)
        self._fireworks = self._make_sound(2.4, self._firework_sample, 0.7)
        self._victory = self._make_sound(3.2, self._victory_sample, 0.48)

    def _make_sound(
        self,
        duration: float,
        sample: Callable[[float], float],
        volume: float,
    ) -> pygame.mixer.Sound:
        frame_count = int(self.sample_rate * duration)
        samples = array(
            "h",
            (
                round(max(-1.0, min(1.0, sample(index / self.sample_rate))) * 32767)
                for index in range(frame_count)
            ),
        )
        sound = pygame.mixer.Sound(buffer=samples.tobytes())
        sound.set_volume(volume)
        return sound

    @staticmethod
    def _battle_sample(time: float) -> float:
        progression = (55.0, 55.0, 51.91, 55.0, 58.27, 55.0, 51.91, 55.0)
        note = progression[int(time) % len(progression)]
        phase = 2 * math.pi * note * time
        pulse = 0.76 + 0.24 * math.sin(2 * math.pi * 0.75 * time) ** 2
        drone = math.sin(phase) + 0.28 * math.sin(phase * 1.5)
        tension = 0.18 * math.sin(2 * math.pi * 82.41 * time)
        return pulse * (0.25 * drone + tension)

    @staticmethod
    def _shot_sample(time: float) -> float:
        envelope = math.exp(-25 * time)
        phase = 2 * math.pi * (950 * time - 1500 * time * time)
        return envelope * (math.sin(phase) + 0.25 * math.sin(phase * 2))

    @staticmethod
    def _laser_sample(time: float) -> float:
        envelope = math.exp(-8 * time)
        phase = 2 * math.pi * (410 * time + 260 * time * time)
        return envelope * (math.sin(phase) + 0.3 * math.sin(phase * 2))

    @staticmethod
    def _drumroll_sample(time: float) -> float:
        sample_index = round(time * SAMPLE_RATE) + 17
        noise = math.sin(sample_index * 12.9898) * math.cos(sample_index * 78.233)
        roll_rate = 7 + 11 * time / 1.5
        tremolo = 0.3 + 0.7 * abs(math.sin(2 * math.pi * roll_rate * time))
        envelope = min(1.0, time * 5) * max(0.0, 1 - time / 1.5)
        low_drum = math.sin(2 * math.pi * 95 * time) * math.exp(-2 * time)
        return envelope * (0.62 * noise * tremolo + 0.38 * low_drum)

    @staticmethod
    def _firework_sample(time: float) -> float:
        sample_index = int(time * SAMPLE_RATE) + 31
        noise = math.sin(sample_index * 12.9898) * math.cos(sample_index * 78.233)
        bursts = (0.05, 0.48, 1.05, 1.68)
        crackle = sum(
            math.exp(-max(0.0, time - start) * 5)
            for start in bursts
            if time >= start
        )
        bang = sum(
            math.exp(-((time - start) * 24) ** 2) * math.sin(2 * math.pi * 62 * time)
            for start in bursts
        )
        sparkle = math.sin(2 * math.pi * (1250 + 300 * time) * time)
        return 0.24 * noise * crackle + 0.3 * bang + 0.12 * sparkle * crackle

    @staticmethod
    def _victory_sample(time: float) -> float:
        notes = (523.25, 659.25, 783.99, 1046.5, 783.99, 1046.5, 1318.5, 1046.5)
        note_index = min(int(time / 0.4), len(notes) - 1)
        local_time = time - note_index * 0.4
        note = notes[note_index]
        envelope = min(1.0, local_time * 30) * max(0.0, 1 - local_time / 0.48)
        melody = math.sin(2 * math.pi * note * time)
        harmony = 0.32 * math.sin(2 * math.pi * (note / 2) * time)
        return envelope * (melody + harmony)

    def play_battle_music(self) -> None:
        if self.enabled and not self._music_channel.get_busy():
            self._music_channel.play(self._battle_music, loops=-1)

    def play_shot(self, laser: bool = False) -> None:
        if self.enabled:
            (self._laser if laser else self._shot).play()

    def play_level_clear(self) -> None:
        if not self.enabled:
            return
        self._music_channel.stop()
        self._cue_channel.play(self._drumroll)

    def play_finale(self) -> None:
        if not self.enabled:
            return
        self._music_channel.stop()
        self._cue_channel.play(self._fireworks)
        self._cue_channel.queue(self._victory)

    def shutdown(self) -> None:
        if self.enabled:
            self._music_channel.stop()
            self._cue_channel.stop()
