import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time


class LogReader:
    def __init__(self):
        # Création de la fenêtre principale
        self.root = tk.Tk()
        self.root.title("Log sensor reader")
        self.root.geometry("1000x600")

        # Variables
        self.data = []
        self.sample_rate = 249.9  # Hz
        self.window_size = 1000  # Nombre de points visibles
        self.time_step = 1 / self.sample_rate

        # Création de l'interface
        self.setup_gui()

    def setup_gui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Bouton de sélection de fichier
        self.select_button = ttk.Button(
            main_frame,
            text="Sélectionner un fichier log",
            command=self.load_file
        )
        self.select_button.grid(row=0, column=0, pady=5)

        # Création du graphique
        self.fig = Figure(figsize=(10, 5))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, pady=5)

        # Slider pour naviguer dans les données
        self.slider = ttk.Scale(
            main_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.update_plot
        )
        self.slider.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier log",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )

        if filename:
            # Lecture et traitement du fichier
            self.data = []
            with open(filename, 'r') as f:
                for line in f:
                    # Conversion des valeurs en nombres
                    values = [int(x) for x in line.strip().split(',') if x]
                    self.data.extend(values)

            # Mise à jour du slider
            max_position = len(self.data) - self.window_size
            self.slider.configure(to=max_position)

            # Affichage initial
            self.update_plot()

    def update_plot(self, *args):
        if not self.data:
            return

        # Position actuelle dans les données
        start_idx = int(self.slider.get())
        end_idx = start_idx + self.window_size

        # Extraction des données à afficher
        display_data = self.data[start_idx:end_idx]

        # Calcul de l'axe temporel
        time_axis = np.arange(len(display_data)) * self.time_step + (start_idx * self.time_step)

        # Mise à jour du graphique
        self.ax.clear()
        self.ax.plot(time_axis, display_data)
        self.ax.set_xlabel('Temps (s)')
        self.ax.set_ylabel('Intensité')
        self.ax.grid(True)
        self.ax.set_title(f'Visualisation des données (fenêtre de {self.window_size} points)')

        # Rafraîchissement du canvas
        self.canvas.draw()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LogReader()
    app.run()