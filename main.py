"""Entry point for Crypt Survivor: Arcane Depths."""

import sys
from src.game import Game


def main():
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n[Crypt Survivor] Game closed via terminal. Thanks for playing!")
        sys.exit(0)
    except Exception as e:
        import traceback
        err = f"[Crypt Survivor] Crash detected:\n{traceback.format_exc()}"
        print(f"\n{err}")
        try:
            with open("crash_log.txt", "w", encoding="utf-8") as f:
                f.write(err)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
