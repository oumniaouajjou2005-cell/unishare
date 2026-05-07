"""
Script de configuration Firebase pour UniShare.
Lance ce script et colle ta configuration Firebase quand demandé.
"""
import json
import os
import sys

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "data", "firebase_config.json")
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

print("=" * 60)
print("  🔥 Configuration Firebase pour UniShare")
print("=" * 60)
print()
print("Pour trouver ta config Firebase :")
print("1. Va sur https://console.firebase.google.com")
print("2. Clique sur ton projet 'UniShare'")
print("3. Clique sur l'icône ⚙️ (Paramètres du projet)")
print("4. Onglet 'Général' → section 'Vos applications'")
print("5. Si aucune appli : clique sur </> (Web) et donne un nom")
print("6. Copie les valeurs de firebaseConfig")
print()
print("-" * 60)

def ask(prompt, example=""):
    val = input(f"{prompt}\n  (ex: {example})\n  > ").strip()
    return val

api_key     = ask("apiKey",      "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
project_id  = ask("projectId",   "unishare-xxxxx")
database_url = ask("databaseURL", "https://unishare-xxxxx-default-rtdb.firebaseio.com")
storage_bucket = ask("storageBucket", "unishare-xxxxx.appspot.com")

config = {
    "apiKey":        api_key,
    "projectId":     project_id,
    "databaseURL":   database_url,
    "storageBucket": storage_bucket,
}

with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print()
print("✅ Configuration sauvegardée dans data/firebase_config.json")
print()

# Test de connexion
print("Test de connexion à Firebase...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from utils import firebase_client as fb
    fb.FIREBASE_CONFIG.update(config)
    result = fb.db_get("_test")
    if result is not None:
        print("✅ Connexion à Firebase Realtime Database réussie !")
    else:
        print("✅ Firebase configuré (la base de données est vide, c'est normal)")
    print()
    print("🚀 Lance l'application avec : python main.py")
except Exception as e:
    print(f"⚠️  Test échoué : {e}")
    print("   Vérifiez que :")
    print("   - La Realtime Database est activée dans Firebase Console")
    print("   - Les règles sont en mode test (read/write = true)")
    print()
    print("🚀 Lance l'application avec : python main.py")
