import os
import unittest

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from spacedefender.audio import AudioManager


class AudioManagerTests(unittest.TestCase):
    def test_game_audio_cues_play_on_dummy_device(self) -> None:
        pygame.init()
        audio = AudioManager()
        self.addCleanup(pygame.quit)
        self.addCleanup(audio.shutdown)

        self.assertTrue(audio.enabled)
        audio.play_battle_music()
        self.assertTrue(audio._music_channel.get_busy())
        audio.play_shot()
        audio.play_shot(laser=True)
        audio.play_level_clear()
        self.assertFalse(audio._music_channel.get_busy())
        self.assertTrue(audio._cue_channel.get_busy())
        audio.play_battle_music()
        audio.play_finale()
        self.assertFalse(audio._music_channel.get_busy())
        self.assertTrue(audio._cue_channel.get_busy())


if __name__ == "__main__":
    unittest.main()
