"""
Autheur : LA
Titre : Contrôleur LED
Description : Initalise et contrôle la LED, allume si l'utilisateur est connecté et sinon éteinte.
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-04-12
"""

from gpiozero import LED


class BoardLED:


    def __init__(self, logger=object) -> None:

        self.logger = logger
        self.logger.info("[GPIO CORE - BoardLED] - Init LED...")
        
        # Init GPIO LED
        self.LED_STATUS = LED(4)
        self.LED_STATUS.on() # Set LED at OFF when init



    def set_status_led(self, action=str) -> None:
        
        if action == "CONNECTED" :
            self.logger.info("[GPIO CORE - BoardLED] - USER IS CONNECTED.")
            self.LED_STATUS.off() # On at 0

        else :
            self.logger.info("[GPIO CORE - BoardLED] - USER IS DISCONNECTED.")
            self.LED_STATUS.on() # Off at 1