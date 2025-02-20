import serial
import datetime
import time
from pathlib import Path


class SerialLogger:
    def __init__(self, port='COM7', baudrate=460800):
        self.serial = serial.Serial(port, baudrate)
        self.buffer = []
        self.current_line = ""
        self.data_lines = []

    def start_logging(self):
        print("Démarrage de la capture...")
        try:
            while True:
                if self.serial.in_waiting:
                    # Lecture caractère par caractère
                    char = self.serial.read().decode('utf-8')

                    # Construction de la ligne
                    if char != '\n':
                        self.current_line += char
                    else:
                        line = self.current_line.strip()
                        self.current_line = ""

                        # Ignorer le message d'initialisation
                        if "initok" in line:
                            print("Initialisation détectée")
                            continue

                        # Traitement des données
                        if line:
                            try:
                                # Nettoyage et conversion des valeurs
                                values = [int(v.strip()) for v in line.split(',') if v.strip()]
                                if values:
                                    self.data_lines.append(','.join(map(str, values)))
                                    print(f"Buffer reçu: {len(values)} valeurs")

                                    # Si on reçoit un buffer plus petit que d'habitude
                                    if len(values) < 200:
                                        print("Fin de capture détectée")
                                        self.save_data()
                                        self.data_lines = []
                                        print("Attente de nouvelles données...")
                            except ValueError as e:
                                print(f"Erreur de conversion: {e}")
                                continue

                # Petite pause pour ne pas surcharger le CPU
                time.sleep(0.001)

        except KeyboardInterrupt:
            print("\nArrêt de la capture")
            self.serial.close()
        except Exception as e:
            print(f"Erreur: {e}")
            self.serial.close()

    def save_data(self):
        if not self.data_lines:
            return

        # Création du nom de fichier avec la date et l'heure
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.txt"

        # Création du dossier logs s'il n'existe pas
        Path("logs").mkdir(exist_ok=True)

        # Sauvegarde des données
        filepath = Path("logs") / filename
        with open(filepath, 'w') as f:
            for line in self.data_lines:
                f.write(line + '\n')

        print(f"Données sauvegardées dans: {filepath}")


if __name__ == "__main__":
    logger = SerialLogger()
    logger.start_logging()