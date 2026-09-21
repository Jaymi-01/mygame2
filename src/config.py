"""Configuration constants and game balance parameters."""

# Window & Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Crypt Survivor: Arcane Depths"

# World Dimensions
WORLD_WIDTH = 3200
WORLD_HEIGHT = 3200
TILE_SIZE = 64

# Color Palette (Hex converted to RGB tuples)
COLOR_BG = (16, 14, 22)
COLOR_FLOOR = (28, 25, 38)
COLOR_FLOOR_ALT = (34, 30, 46)
COLOR_GRID = (22, 20, 30)
COLOR_WALL = (45, 40, 58)

COLOR_WHITE = (245, 245, 250)
COLOR_BLACK = (10, 8, 14)
COLOR_GRAY = (120, 115, 135)
COLOR_DARK_GRAY = (60, 55, 70)

# Thematic Colors
COLOR_ARCANE_CYAN = (60, 220, 255)
COLOR_ARCANE_BLUE = (30, 130, 255)
COLOR_XP_GEM = (100, 240, 160)
COLOR_XP_RARE = (220, 80, 255)
COLOR_XP_LEGENDARY = (255, 215, 0)
COLOR_HEALTH_RED = (235, 55, 75)
COLOR_HEALTH_GREEN = (65, 220, 110)
COLOR_MANA_BLUE = (80, 160, 255)
COLOR_FIRE_ORANGE = (255, 140, 30)
COLOR_GOLD = (255, 215, 0)
COLOR_SHADOW = (10, 8, 16, 160)

# Player Base Stats
PLAYER_BASE_HP = 100
PLAYER_BASE_SPEED = 240.0  # pixels per second
PLAYER_RADIUS = 18
PLAYER_DASH_SPEED = 620.0
PLAYER_DASH_DURATION = 0.22  # seconds
PLAYER_DASH_COOLDOWN = 1.6  # seconds
PLAYER_BASE_MAGNET_RADIUS = 120.0

# Sound Configuration
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_BUFFER = 512
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.5

# Character Classes Definition
CHARACTER_CLASSES = {
    "mage": {
        "name": "Arcane Mage",
        "title": "Scholar of the Astral Crypt",
        "starting_weapon": "wand",
        "hp": 95.0,
        "speed": 240.0,
        "dash_cooldown": 1.5,
        "damage_multiplier": 1.25,
        "cooldown_multiplier": 0.85,
        "crit_chance": 0.08,
        "crit_mult": 2.5,
        "vampirism": 0.0,
        "regen_rate": 0.0,
        "magnet_radius": 130.0,
        "color": COLOR_ARCANE_CYAN,
        "icon_desc": "Magic Wand",
        "passive_desc": "+25% Spell Damage, -15% Cooldowns",
        "flavor": "Fires high-velocity arcane bolts with rapid spell recovery.",
    },
    "warrior": {
        "name": "Berserker",
        "title": "Ironclad Blood Warden",
        "starting_weapon": "cleave",
        "hp": 160.0,
        "speed": 235.0,
        "dash_cooldown": 1.4,
        "damage_multiplier": 1.15,
        "cooldown_multiplier": 1.0,
        "crit_chance": 0.10,
        "crit_mult": 2.5,
        "vampirism": 0.12,
        "regen_rate": 0.6,
        "magnet_radius": 110.0,
        "color": COLOR_HEALTH_RED,
        "icon_desc": "Greatsword Cleave",
        "passive_desc": "+60% Max HP, +12% Life Steal on Kill",
        "flavor": "Slices enemies in sweeping arcs, absorbing vitality from fallen foes.",
    },
    "assassin": {
        "name": "Shadow Rogue",
        "title": "Silent Nightblade",
        "starting_weapon": "dagger",
        "hp": 75.0,
        "speed": 310.0,
        "dash_cooldown": 0.85,
        "damage_multiplier": 1.0,
        "cooldown_multiplier": 0.9,
        "crit_chance": 0.28,
        "crit_mult": 3.0,
        "vampirism": 0.0,
        "regen_rate": 0.0,
        "magnet_radius": 120.0,
        "color": (80, 240, 150),
        "icon_desc": "Phantom Dagger",
        "passive_desc": "+29% Speed, 28% Crit (3x DMG), 0.8s Dash",
        "flavor": "Hyper-mobile assassin striking with surgical critical lethality.",
    },
    "tank": {
        "name": "Iron Juggernaut",
        "title": "The Unbroken Bastion",
        "starting_weapon": "orbit",
        "hp": 220.0,
        "speed": 195.0,
        "dash_cooldown": 1.8,
        "damage_multiplier": 0.95,
        "cooldown_multiplier": 1.05,
        "crit_chance": 0.05,
        "crit_mult": 2.5,
        "vampirism": 0.0,
        "regen_rate": 2.2,
        "magnet_radius": 170.0,
        "color": COLOR_GOLD,
        "icon_desc": "Orbiting Aegis",
        "passive_desc": "+120% Max HP, +2.2 HP/s Regen, +40% Magnet",
        "flavor": "An impenetrable juggernaut guarded by orbiting shields with steady HP regen.",
    },
}
