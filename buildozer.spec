[app]

# App metadata
title = ColorBlock
package.name = colorblock
package.domain = org.colorblock

source.dir = .
source.include_exts = py,kv,csv,png,jpg,jpeg

version = 1.0.0

# Dependencies — use 'opencv' (not opencv-python) for the Kivy/buildozer recipe
requirements = python3,kivy==2.3.0,numpy==1.26.4,pandas,opencv,scikit-learn,scikit-image,plyer,pillow

orientation = portrait
fullscreen = 0

android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# iOS
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

[buildozer]
log_level = 2
warn_on_root = 1
