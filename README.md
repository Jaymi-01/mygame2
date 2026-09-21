# ⚔️ Crypt Survivor: Arcane Depths

A fast-paced, top-down Action Roguelike / Dungeon Crawler built in Python using **Pygame-CE**.

Survive relentless hordes of undead and abyssal monstrosities in an ancient subterranean crypt. Harvest arcane XP gems, level up, draft game-altering blessings, and unleash devastating magical synergies to defeat **Archlich Malakor**.

---

## 🎮 How to Play

### One-Click Launch (Windows)
Double-click:
```bat
run_game.bat
```

### Manual Launch via Terminal
```bash
# Activate the virtual environment
.\.venv\Scripts\python.exe main.py
```

---

## 🕹️ Controls

| Action | Control |
| :--- | :--- |
| **Move Hero** | `W`, `A`, `S`, `D` or `Arrow Keys` |
| **Dodge Roll / Dash** | `Spacebar` or `Left Click` (Grants invulnerability frames & burst speed) |
| **Select Level-up Card** | `1`, `2`, `3` or `Mouse Click` |
| **Pause / Resume** | `ESC` |
| **Restart (Game Over / Win)** | `ENTER` or `SPACEBAR` |

> 💡 **Auto-Aiming Magic**: Your equipped spells automatically target and fire at the nearest threats. Focus on positioning, kiting monsters around stone pillars, and gathering XP gems!

---

## 🛡️ Character Classes

Choose from 4 distinct champions on the Hero Selection screen:

| Class | Title | Starting Weapon | Base HP | Speed | Playstyle & Unique Passives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Arcane Mage** | Scholar of Astral Crypt | Magic Wand | 95 HP | 240 | High spell damage (+25%), -15% weapon cooldowns. |
| **Berserker** | Ironclad Blood Warden | Greatsword Cleave | 160 HP | 235 | Heavy melee sweeps, +12% Life Steal on kill, +0.6 HP/s regen. |
| **Shadow Rogue** | Silent Nightblade | Phantom Dagger | 75 HP | 310 | Extreme mobility, 28% Crit chance (3.0x damage), 0.85s dash cooldown. |
| **Iron Juggernaut** | The Unbroken Bastion | Orbiting Aegis | 220 HP | 195 | Immense resilience, +2.2 HP/s passive regeneration, +40% gem magnet pull. |

---

## 🔮 Weapons & Spells

1. **Arcane Missile**: Fires rapid-fire homing bolts of pure magical force that pierce through enemy ranks.
2. **Whirlwind Cleave**: Sweeps a massive greatsword in a wide arc (full 360° whirlwind at higher levels!), cleaving hordes and throwing them back.
3. **Orbiting Arc**: Conjures rotating crystalline shields around your hero that shred and knock back anything attempting to close in.
4. **Chain Lightning**: Unleashes high-voltage electric shocks that arc between clustered enemies.
5. **Blaze Aura**: Envelops the player in a persistent circle of flame, continually ticking burning damage on close foes.
6. **Phantom Daggers**: Flings hyper-fast piercing daggers directly at vulnerable foes.

---

## 💎 Blessings & Passives

- **Phantom Boots**: Increases movement speed by +18%.
- **Iron Heart**: Expands max health by +30 HP and instantly restores 30 HP.
- **Arcane Haste**: Reduces weapon cooldowns by 15%, increasing attack fire rate.
- **Keen Senses**: Boosts critical strike chance by +12% for devastating 2.5x damage spikes with golden damage numbers.
- **Aether Magnet**: Expands gem collection gravitational pull radius by +45%.
- **Soul Siphon**: Grants an 8% chance to siphon 4 HP upon eliminating any monster.
- **Elder Regeneration**: Passively restores +1.2 HP per second.

---

## 👾 Bestiary & Encounters

- **Acid Slimes**: Fast, swarming blobs that test early crowd control.
- **Skeleton Minions**: Armed with jagged blades; tough in numbers.
- **Magma Golems**: Armored brutes that wind up and charge with earth-shattering force.
- **Void Warlocks**: Ranged spellcasters who kite at distance and sling dark magic bolts.
- **Archlich Malakor (Boss)**: Awakens as the clock reaches 3 minutes. Possesses multi-phase attacks including 10-way radial dark barrages, triple targeted blasts, and ground-shattering shockwaves.

---

## 📦 Project Architecture

```
mygame2/
├── run_game.bat         # Instant launcher
├── requirements.txt     # Dependencies (pygame-ce)
├── main.py              # Entry point
├── README.md            # Documentation and game guide
└── src/
    ├── config.py        # Screen dimensions, world limits, balance constants
    ├── audio.py         # Real-time procedural 8-bit sound effects & ambient music synthesizer
    ├── sprites.py       # Procedural pixel-art sprite generators with caching
    ├── particles.py     # Damage popups, impact sparks, shockwaves, screen shake
    ├── player.py        # Hero movement, dash iframe physics, leveling, stats
    ├── weapons.py       # Weapons manager, projectile collisions, chain lightning logic
    ├── enemies.py       # Enemy AI, steering separation, charges, boss attacks
    ├── items.py         # XP gems, health flasks, magnets, bombs, chests
    ├── dungeon.py       # Cobblestone tile map, tactical pillars, torch illumination
    ├── ui.py            # HUD, level up card draft modal, death & victory screens
    └── game.py          # State machine, wave progression director, camera lerp
```
