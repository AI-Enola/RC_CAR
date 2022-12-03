"""
Autheur : LA
Titre : Contrôleur le moteur et impose un mode de conduite (comportement)
Description : Initalise et contrôle la polarité du moteur
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-04-12
"""

import RPi.GPIO as GPIO


class DriveMode:
    """
    Initialise les valeurs maximales de puissance pour avancer et une valeur constante pour reculer.
    Un dictionnaire est utilisé pour lier une identifiant de mode à une variable contenant la valeur.
    Permet de changer de mode de conduite
    Permet de récupérer le mode de conduite avec un nom d'identifiant.
    """

    def __init__(self, logger=object) :
        """
        Initialise les valeurs maximales de puissance pour avancer et une valeur constante pour reculer.
        Un dictionnaire est utilisé pour lier une identifiant de mode à une variable contenant la valeur.
        Mode de conduite par défaut : NORMAL
        """
        self.logger = logger
        self.logger.info("[GPIO CORE - MotorDriver] - Init Driving Mode...")

        self.DRIVE_MODE_TYPE_R = int(-100)
        self.DRIVE_MODE_SPORT = int(-70)
        self.DRIVE_MODE_NORMAL = int(-50)
        self.DRIVE_MODE_ECO = int(-30)

        self.DRIVE_MODES = {
            "TYPE_R" : self.DRIVE_MODE_TYPE_R,
            "SPORT" : self.DRIVE_MODE_SPORT,
            "NORMAL" : self.DRIVE_MODE_NORMAL,
            "ECO" : self.DRIVE_MODE_ECO
        }

        self.REVERSE_MAX = int(40)

        self.drive_mode = self.DRIVE_MODE_NORMAL


    def change_drive_mode(self, drive_mode=int) -> None:
        """
        Change le mode de conduite par celle choisis par le client web.
        """
        self.drive_mode = drive_mode


    def get_drive_mode(self) -> str :
        """
        Permet de récupérer le mode de conduite avec un nom d'identifiant.
        """
        for key, value in self.DRIVE_MODES.items() :
            if self.drive_mode == value :
                return str(f"CURRENT_DRIVING_MODE:{key}")




class MotorDriver:
    """
    Initialise les pin GPIO pour la polarité du moteur
    Contrôle la puissance du moteur sois en faisant avancer ou reculer le véhicule
    """

    def __init__(self, logger=object, drive_mode_class=object) -> None:
        """
        Initialise les pin GPIO pour la polarité du moteur
        """
        self.logger = logger
        self.drive_mode_class = drive_mode_class

        self.logger.info("[GPIO CORE - MotorDriver] - Init Motor Driver...")

        # Init GPIO Motor
        self.MOTOR_INB4_GPIO_PIN = int(13)
        self.MOTOR_INB3_GPIO_PIN = int(19)

        FREQUENCY = 50 #Hz

        GPIO.setup(self.MOTOR_INB4_GPIO_PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR_INB3_GPIO_PIN, GPIO.OUT)

        self.MOTOR_B_PWM_BACKWARD_GPIO = GPIO.PWM(self.MOTOR_INB4_GPIO_PIN, FREQUENCY)
        self.MOTOR_B_PWM_FORWARD_GPIO = GPIO.PWM(self.MOTOR_INB3_GPIO_PIN, FREQUENCY)

        self.MOTOR_B_PWM_FORWARD_GPIO.start(0)
        self.MOTOR_B_PWM_BACKWARD_GPIO.start(0)


    def set_motor_power(self, power=int)-> None:
        """
        Contrôle la puissance du moteur sois en faisant avancer ou reculer le véhicule
        Une valeur de + 1% et plus permet de faire reculer le véhicule
        Une valeur de - 1% et moins permet de faire avancer le véhicule
        Une valeur de 0 fait arrêter le moteur
        Protection contre valeur trop élevé ou trop basse pouvant abîmer le moteur avec le mode de conduite.
        """
        if power >= self.drive_mode_class.drive_mode :

            if power < -1: # MOVE FORWARD
                self.logger.info("[GPIO CORE - MotorDriver] - Motor Driver moving FORWARD...")
                self.MOTOR_B_PWM_BACKWARD_GPIO.ChangeDutyCycle(0)
                self.MOTOR_B_PWM_FORWARD_GPIO.ChangeDutyCycle(abs(power))
                


            elif power == 0 : #STOPPING MOTOR
                self.logger.info("[GPIO CORE - MotorDriver] - Motor Driver STOPPING...")
                self.MOTOR_B_PWM_BACKWARD_GPIO.ChangeDutyCycle(power)
                self.MOTOR_B_PWM_FORWARD_GPIO.ChangeDutyCycle(power)
            

        if power > 1 and power <= self.drive_mode_class.REVERSE_MAX: # MOVE BACKWARD
            self.logger.info("[GPIO CORE - MotorDriver] - Motor Driver moving BACKWARD...")
            self.MOTOR_B_PWM_FORWARD_GPIO.ChangeDutyCycle(0)
            self.MOTOR_B_PWM_BACKWARD_GPIO.ChangeDutyCycle(power)
