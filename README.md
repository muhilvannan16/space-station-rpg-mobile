# Space Station RPG — Mobile Version

A Kivy-based Android port of the terminal Space Station RPG. Survive a failing space station: explore rooms, manage oxygen and power, fight enemies, scavenge items, and reach the escape pod before it's too late.

## Features

- Touch-based movement via on-screen D-pad
- Colored tile map rendered with Kivy GridLayout
- Combat, hazard events, and item pickup as dedicated screens/popups
- Oxygen and power survival mechanics
- Save/load system (Android-aware storage paths)
- Same game logic and map data as the terminal version
- Powered by [pygamelogic](https://pypi.org/project/pygamelogic/) and [pygamesense](https://pypi.org/project/pygamesense/)

## Project Structure

```
main.py              App entry point
game.kv              All UI layouts (KV language)
screens/             Screen classes (title, game, combat, event, end)
core/                Game logic (state, map loader, combat math, events)
assets/maps/         station.json map data
assets/fonts/        Bundled fonts (add a mono.ttf here)
buildozer.spec       APK build configuration
```

## Running on Desktop

```bash
git clone https://github.com/muhilvannan16/space-station-rpg.git
cd space-station-rpg-mobile
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install kivy pygamelogic pygamesense
python main.py
```

## Building the APK

Requires Linux or WSL. See Section 7 of the Mobile Build Guide PDF for full instructions.

```bash
pip install buildozer cython
buildozer init          # if buildozer.spec doesn't exist
buildozer android debug
```

## Credits

Built by [muhilvannan16](https://github.com/muhilvannan16).

[pygamelogic](https://pypi.org/project/pygamelogic/) and [pygamesense](https://pypi.org/project/pygamesense/) are the author's own published PyPI packages.

## License

All Rights Reserved.

Copyright © 2026 Muhilvannan Elavazhagan. All rights reserved.

This source code is made available for viewing purposes only. No part of
this software may be copied, modified, distributed, or used in any form
without explicit written permission from the copyright holder.