"""
Autheur : LA
Source VL53L0X : https://github.com/johnbryanmoore/VL53L0X_rasp_python
Titre : Capteur de distance ToF
Description : Initalisation et récupération des données avec le protocole I2C - Utilisation de Ctypes pour effectuer la communication
avec l'API en langage C.
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-04-12
"""

# Python Libraries
import time
from threading import Thread

# Custom Libraries
from . import VL53L0X


class ToFSensor:
    """
    Initialise le capteur en faisant appel à un fichier VL53L0X.py pour initier l'initialisation
    Démarrage d'un thread pour faire tourner la récupération des données en même temps que le programme effectue son rôle principal
    Retourne les données récupérer en tant que string
    """
    def __init__(self, logger=object) :
        """
        Initialise le capteur en faisant appel à un fichier VL53L0X.py pour initier l'initialisation
        Démarrage d'un thread pour faire tourner la récupération des données en même temps que le programme effectue son rôle principal
        """
        self.logger = logger

        self.logger.info("[GPIO CORE - ToF Sensor] - Init ToF Sensor...")
        # Create a VL53L0X object
        self.tof = VL53L0X.VL53L0X(i2c_address=0x29)

        self.logger.info("[GPIO CORE - ToF Sensor] - Init Thread instance...")

        self.distance = int(0)
        
        # Init n Thread with service and args for them
        thread1 = Thread(target=self.handle_device, args=())

        # Main thread is not a deamon thread
        thread1.daemon = False

        self.logger.info("[GPIO CORE - ToF Sensor] - Starting Thread instance...")
        # Start n thread
        thread1.start()


    def handle_device(self) :
        """
        Le thread permet de faire tourner infiniment cette fonction afin de récupérer les données du capteur
        Timing = temps d'envoi et de reception du signal pour la mesure de distance
        """
        self.logger.info("[GPIO CORE - ToF Sensor] - Starting Ranging...")
        # Start ranging
        self.tof.start_ranging(mode=VL53L0X.VL53L0X_BETTER_ACCURACY_MODE) # NEED TO BE CHANGE ACCURACY FOR PHASE 2 OF PROJECT TEST - FOR COLLISION ASSIST

        self.logger.info("[GPIO CORE - ToF Sensor] - Getting timing...")
        timing = self.tof.get_timing()

        if (timing < 20000):
            timing = 20000

        self.logger.info(f"[GPIO CORE - ToF Sensor] -Timing: {timing / 1000} ms")

        while(1) : # Récupère infiniment les données

            distance = self.tof.get_distance() # Récupère la distance

            if (distance > 0):
                # self.logger.info(f"[GPIO CORE - ToF Sensor] - Sensor Data : {distance} mm, {distance / 10}")
                self.distance = int(distance / 10) # Convertit en millimètre la distance

            time.sleep(timing / 1000000.00)


    def get_data(self):
        """
        Retourne les données en type string
        """
        return (f"Distance: {self.distance}")