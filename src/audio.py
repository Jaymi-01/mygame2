"""Procedural audio engine and sound manager using synthesized waveforms."""

import io
import math
import random
import struct
import wave
import pygame
from src.config import AUDIO_BUFFER, AUDIO_CHANNELS, AUDIO_SAMPLE_RATE, MASTER_VOLUME, SFX_VOLUME, MUSIC_VOLUME


def _generate_wav_bytes(samples, sample_rate=AUDIO_SAMPLE_RATE):
    """Encodes 16-bit mono PCM samples into in-memory WAV byte stream."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # Clamp samples to 16-bit signed range
        clamped = [max(-32767, min(32767, int(s))) for s in samples]
        wf.writeframes(struct.pack("<" + "h" * len(clamped), *clamped))
    buf.seek(0)
    return buf


class SoundEngine:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.music_sound = None
        self.music_channel = None

        try:
            pygame.mixer.init(
                frequency=AUDIO_SAMPLE_RATE,
                size=-16,
                channels=AUDIO_CHANNELS,
                buffer=AUDIO_BUFFER,
            )
            pygame.mixer.set_num_channels(16)
            self.enabled = True
            self._synthesize_all_sounds()
            self._synthesize_ambient_music()
        except Exception as e:
            print(f"[AudioEngine] Audio init failed (running silently): {e}")
            self.enabled = False

    def _synthesize_all_sounds(self):
        if not self.enabled:
            return

        sr = AUDIO_SAMPLE_RATE

        # 1. Player Shoot (Crisp arcane blast)
        dur = 0.12
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            t = i / sr
            # Frequency slides from 850Hz down to 280Hz
            freq = 850.0 - (570.0 * (i / n_samples))
            # Sine wave with fast attack and exponential decay
            env = math.exp(-6.0 * (i / n_samples))
            val = math.sin(2.0 * math.pi * freq * t) * env * 18000
            samples.append(val)
        self.sounds["shoot"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["shoot"].set_volume(0.35 * SFX_VOLUME * MASTER_VOLUME)

        # 2. Lightning / Arcane Zap
        dur = 0.16
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            t = i / sr
            freq = 400.0 + 300.0 * math.sin(40.0 * math.pi * t)
            noise = (random.random() * 2.0 - 1.0) * 0.3
            env = (1.0 - (i / n_samples)) ** 1.8
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 + noise) * env * 20000
            samples.append(val)
        self.sounds["lightning"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["lightning"].set_volume(0.4 * SFX_VOLUME * MASTER_VOLUME)

        # 3. Enemy Hit (Punchy impact click)
        dur = 0.08
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            env = (1.0 - (i / n_samples)) ** 2.5
            noise = random.random() * 2.0 - 1.0
            tone = math.sin(2.0 * math.pi * 140.0 * (i / sr))
            val = (noise * 0.6 + tone * 0.4) * env * 22000
            samples.append(val)
        self.sounds["hit"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["hit"].set_volume(0.45 * SFX_VOLUME * MASTER_VOLUME)

        # 4. Enemy Kill (Crunchy pop/shatter)
        dur = 0.18
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            env = (1.0 - (i / n_samples)) ** 2.0
            freq = 320.0 - 240.0 * (i / n_samples)
            noise = random.random() * 2.0 - 1.0
            val = (math.sin(2.0 * math.pi * freq * (i / sr)) * 0.5 + noise * 0.5) * env * 24000
            samples.append(val)
        self.sounds["kill"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["kill"].set_volume(0.5 * SFX_VOLUME * MASTER_VOLUME)

        # 5. Gem Pickup (Sweet bright chime: C6 -> G6)
        dur = 0.15
        n_samples = int(dur * sr)
        samples = []
        half = n_samples // 2
        for i in range(n_samples):
            t = i / sr
            if i < half:
                freq = 1046.5  # C6
                local_env = math.exp(-8.0 * (i / half))
            else:
                freq = 1567.98  # G6
                local_env = math.exp(-6.0 * ((i - half) / (n_samples - half)))
            val = math.sin(2.0 * math.pi * freq * t) * local_env * 16000
            samples.append(val)
        self.sounds["gem"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["gem"].set_volume(0.4 * SFX_VOLUME * MASTER_VOLUME)

        # 6. Dash Whoosh
        dur = 0.2
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            t = i / sr
            env = math.sin(math.pi * (i / n_samples))
            noise = random.random() * 2.0 - 1.0
            # Filtered noise sweep
            freq = 200.0 + 600.0 * env
            tone = math.sin(2.0 * math.pi * freq * t)
            val = (noise * 0.7 + tone * 0.3) * env * 19000
            samples.append(val)
        self.sounds["dash"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["dash"].set_volume(0.45 * SFX_VOLUME * MASTER_VOLUME)

        # 6.5 Blade Slash / Cleave (Sharp cutting whoosh)
        dur = 0.14
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            t = i / sr
            env = math.exp(-9.0 * (i / n_samples))
            freq = 950.0 - 700.0 * (i / n_samples)
            noise = (random.random() * 2.0 - 1.0) * 0.45
            val = (math.sin(2.0 * math.pi * freq * t) * 0.55 + noise * 0.45) * env * 22000
            samples.append(val)
        self.sounds["slash"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["slash"].set_volume(0.5 * SFX_VOLUME * MASTER_VOLUME)

        # 7. Player Hurt (Heavy thud)
        dur = 0.22
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            env = math.exp(-8.0 * (i / n_samples))
            freq = 160.0 - 90.0 * (i / n_samples)
            noise = (random.random() * 2.0 - 1.0) * 0.4
            val = (math.sin(2.0 * math.pi * freq * (i / sr)) * 0.8 + noise) * env * 28000
            samples.append(val)
        self.sounds["hurt"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["hurt"].set_volume(0.6 * SFX_VOLUME * MASTER_VOLUME)

        # 8. Level Up Fanfare (Four rising harmonic notes)
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_dur = 0.11
        samples = []
        for note in notes:
            n_note_samples = int(note_dur * sr)
            for i in range(n_note_samples):
                t = i / sr
                env = math.exp(-4.5 * (i / n_note_samples))
                val = (
                    math.sin(2.0 * math.pi * note * t) * 0.7
                    + math.sin(4.0 * math.pi * note * t) * 0.3
                ) * env * 20000
                samples.append(val)
        self.sounds["levelup"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["levelup"].set_volume(0.65 * SFX_VOLUME * MASTER_VOLUME)

        # 9. Boss Roar / Warning
        dur = 0.65
        n_samples = int(dur * sr)
        samples = []
        for i in range(n_samples):
            t = i / sr
            env = math.sin(math.pi * (i / n_samples))
            freq = 65.0 + 35.0 * math.sin(18.0 * math.pi * t)
            noise = (random.random() * 2.0 - 1.0) * 0.5
            val = (math.sin(2.0 * math.pi * freq * t) * 0.7 + noise) * env * 29000
            samples.append(val)
        self.sounds["boss_roar"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["boss_roar"].set_volume(0.7 * SFX_VOLUME * MASTER_VOLUME)

        # 10. Chest / Item Fanfare
        chest_notes = [440.0, 554.37, 659.25, 880.0]  # A Major arpeggio
        samples = []
        for note in chest_notes:
            n_note_samples = int(0.12 * sr)
            for i in range(n_note_samples):
                t = i / sr
                env = math.exp(-3.5 * (i / n_note_samples))
                val = math.sin(2.0 * math.pi * note * t) * env * 21000
                samples.append(val)
        self.sounds["chest"] = pygame.mixer.Sound(_generate_wav_bytes(samples))
        self.sounds["chest"].set_volume(0.6 * SFX_VOLUME * MASTER_VOLUME)

    def _synthesize_ambient_music(self):
        """Generates a seamless loopable 6-second dark dungeon ambient music piece."""
        if not self.enabled:
            return

        sr = 22050
        total_duration = 6.0
        total_samples = int(total_duration * sr)
        samples = [0.0] * total_samples

        # Bass drone: D minor (D2 = 73.42 Hz, A2 = 110.0 Hz)
        two_pi = 2.0 * math.pi
        step = two_pi / sr
        freq_d = 73.42 * step
        freq_a = 110.0 * step
        freq_lfo = 0.33 * step

        for i in range(total_samples):
            drone = (
                math.sin(freq_d * i) * 0.6
                + math.sin(freq_a * i) * 0.3
            )
            lfo = 0.75 + 0.25 * math.sin(freq_lfo * i)
            samples[i] = drone * lfo * 5500

        # Mysterious arpeggiated motif (D minor pentatonic)
        motif = [146.83, 174.61, 220.00, 261.63, 293.66, 261.63, 220.00, 174.61]
        step_dur = total_duration / len(motif)
        step_samples = int(step_dur * sr)

        for step_idx, freq in enumerate(motif):
            start_i = step_idx * step_samples
            freq_step = freq * step
            for s in range(step_samples):
                idx = start_i + s
                if idx >= total_samples:
                    break
                env = math.exp(-3.5 * (s / step_samples))
                bell = math.sin(freq_step * s) * 0.8 + math.sin(freq_step * 2.0 * s) * 0.2
                samples[idx] += bell * env * 4500

        # Render to Sound and loop
        try:
            self.music_sound = pygame.mixer.Sound(_generate_wav_bytes(samples, sample_rate=sr))
            self.music_sound.set_volume(0.3 * MUSIC_VOLUME * MASTER_VOLUME)
        except Exception as e:
            print(f"[AudioEngine] Failed to build ambient music: {e}")

    def start_music(self):
        if self.enabled and self.music_sound:
            try:
                self.music_channel = self.music_sound.play(loops=-1)
            except Exception:
                pass

    def stop_music(self):
        if self.enabled and self.music_channel:
            self.music_channel.stop()

    def play(self, sound_name: str):
        """Plays a pre-synthesized sound effect."""
        if not self.enabled:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass


# Global singleton sound engine
_audio_instance = None


def get_audio() -> SoundEngine:
    global _audio_instance
    if _audio_instance is None:
        _audio_instance = SoundEngine()
    return _audio_instance
