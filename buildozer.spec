[app]
title = Space Station RPG
package.name = spacestationrpg
package.domain = com.muhilvannan16
source.dir = .
source.include_exts = py,png,jpg,kv,json,ttf
version = 1.0.0
requirements = python3,kivy,pygamelogic,pygamesense
orientation = portrait
fullscreen = 1
# icon.filename = %(source.dir)s/assets/images/icon.png
# Uncomment above after placing a 512x512 icon.png in assets/images/

# Android-specific
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
