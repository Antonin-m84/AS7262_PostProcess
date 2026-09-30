# Spectrophotomètre AS7262 - script PostProcess  🔬📊

Ce projet permet d'enregistrer et de traiter les données mesurées par un capteur optique (capteur de couleur **Adafruit AS7262**). 

Dans ce cas d'utilisation précis, le capteur attend un signal électrique de démarrage pour commencer l'enregistrement. Une seule couleur est enregistrée. La fréquence d'acquisition des mesures est définie par le composant électronique d'origine de la carte Arduino (le quartz) et peut être modifiée jusqu'à une vitesse de 300 Hz (300 mesures par seconde).

---

## 🔌 Câblage et connexions électriques

Si vous devez brancher ou vérifier les composants :

- **Capteur Adafruit AS7262 :**
  - `SDA` : Connexion de données
  - `SCL` : Connexion d'horloge
  - `3.3V` : Alimentation électrique
  - `GND` : Masse / Terre
- **Lumières (4 LED) :**
  - Branchées sur les broches `D8`, `D9`, `D10` et `D11` de la carte.
- **Signal de démarrage externe :**
  - Branché sur la broche `D2` (déclenchement par un signal 5V à front montant).

*(Pour le schéma électrique complet du montage sur la carte de prototypage, consultez les photos jointes au projet).*

---

## 🖨️ Pièces imprimées en 3D

Pour le support et le boîtier :
- Selon la précision de votre imprimante 3D, certaines zones des pièces imprimées peuvent nécessiter un léger ponçage manuel afin de garantir un assemblage et un fonctionnement fluides.
