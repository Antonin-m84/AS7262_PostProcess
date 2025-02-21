import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import datetime
import os


class LogReader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Log sensor reader")
        self.root.geometry("1200x720")

        # Variables
        self.data = []
        self.sample_rate = 249.9  # Hz
        self.window_size = 1000  # Nombre de points visibles par défaut
        self.time_step = 1 / self.sample_rate
        self.max_y_value = 0

        # Création de l'interface
        self.setup_gui()

    def setup_gui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame supérieure pour le bouton et les infos
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Bouton de sélection de fichier
        self.select_button = ttk.Button(
            top_frame,
            text="Sélectionner un fichier log",
            command=self.load_file
        )
        self.select_button.pack(side=tk.LEFT, padx=5)

        # Label pour les informations du fichier
        self.file_info = ttk.Label(
            top_frame,
            text="Aucun fichier chargé"
        )
        self.file_info.pack(side=tk.LEFT, padx=5)

        # Frame pour le graphique et le curseur de taille
        graph_frame = ttk.Frame(main_frame)
        graph_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Création du graphique
        self.fig = Figure(figsize=(11, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, pady=5, padx=(5, 0))

        # Frame pour le curseur de taille
        size_frame = ttk.Frame(graph_frame)
        size_frame.grid(row=0, column=1, pady=5, padx=5)

        # Label pour le curseur de taille
        ttk.Label(size_frame, text="Taille fenêtre").pack(pady=(0, 5))

        # Curseur pour la taille de la fenêtre
        self.window_slider = ttk.Scale(
            size_frame,
            from_=1500,
            to=200,
            orient=tk.VERTICAL,
            command=self.update_window_size,
            value=1000
        )
        self.window_slider.pack(expand=True, fill=tk.Y)

        # Frame pour le curseur de défilement
        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Label pour le curseur de défilement
        ttk.Label(scroll_frame, text="Défilement du temps").pack()

        # Curseur pour naviguer dans les données
        self.time_slider = ttk.Scale(
            scroll_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.update_plot
        )
        self.time_slider.pack(fill=tk.X, padx=5)

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
            # Extraction de la date et de l'heure depuis le nom du fichier
            basename = os.path.basename(filename)
            if basename.startswith("log_") and basename.endswith(".txt"):
                date_str = basename[4:-4]  # Enlève "log_" et ".txt"
                try:
                    file_date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    date_display = file_date.strftime("%d/%m/%Y à %H:%M")
                except ValueError:
                    date_display = "Date inconnue"
            else:
                date_display = "Date inconnue"

            # Lecture et traitement du fichier
            self.data = []
            with open(filename, 'r') as f:
                for line in f:
                    values = [int(x) for x in line.strip().split(',') if x]
                    self.data.extend(values)

            # Calcul de la durée
            duration = len(self.data) / self.sample_rate
            duration_str = f"{duration:.1f}"

            # Mise à jour du max_y_value
            self.max_y_value = max(self.data) + 5

            # Mise à jour de l'information du fichier
            self.file_info.config(
                text=f"Fichier sélectionné :  Date : {date_display}    /    Durée totale : {duration_str} secondes"
            )

            # Mise à jour du slider
            self.update_time_slider()

            # Affichage initial
            self.update_plot()

    def update_window_size(self, *args):
        self.window_size = int(self.window_slider.get())
        if self.data:
            self.update_time_slider()
            self.update_plot()

    def update_time_slider(self):
        max_position = max(0, len(self.data) - self.window_size)
        self.time_slider.configure(to=max_position)

    def update_plot(self, *args):
        if not self.data:
            return

        # Position actuelle dans les données
        start_idx = int(self.time_slider.get())
        end_idx = start_idx + self.window_size

        # Extraction des données à afficher
        display_data = self.data[start_idx:min(end_idx, len(self.data))]

        # Calcul de l'axe temporel
        time_axis = np.arange(len(display_data)) * self.time_step + (start_idx * self.time_step)

        # Mise à jour du graphique
        self.ax.clear()
        self.ax.plot(time_axis, display_data)
        self.ax.set_xlabel('Temps (s)')
        self.ax.set_ylabel('Intensité lumineuse')
        self.ax.grid(True)
        self.ax.set_title(f'Visualisation des données (fenêtre de {self.window_size} points)')

        # Fixation de l'échelle y
        self.ax.set_ylim(0, self.max_y_value)

        # Rafraîchissement du canvas
        self.canvas.draw()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LogReader()
    app.run()