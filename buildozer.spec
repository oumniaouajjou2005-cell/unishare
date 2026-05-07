[app]
# Informations de l'application
title = UniShare
package.name = unishare
package.domain = ma.unishare

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

# Point d'entrée
entrypoint = main_kivy.py

# Dépendances Python
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,certifi,urllib3

# Orientation (portrait uniquement sur mobile)
orientation = portrait

# Permissions Android
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# API Android cible
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# Architecture(s) Android (arm64-v8a = téléphones modernes)
android.archs = arm64-v8a, armeabi-v7a

# Icône de l'application
icon.filename = assests/logo_unishare.png

# Écran de démarrage (même image que le logo)
presplash.filename = assests/splash.png

# Accepter automatiquement la licence Android SDK
android.accept_sdk_license = True

# Log mode (0 = release, 1 = debug)
android.logcat_filters = *:S python:D

[buildozer]
# Répertoire de build (ignoré par git)
build_dir = .buildozer
bin_dir = ./bin

# Niveau de log (0 = silencieux, 2 = verbose)
log_level = 2
warn_on_root = 1
