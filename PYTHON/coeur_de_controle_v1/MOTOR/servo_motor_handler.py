"""
Autheur : LA
Titre : Contrôleur servo moteur
Description : Initalise et contrôle la direction du servo moteur
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-04-12
"""

import time
import RPi.GPIO as GPIO

class ServoMotor:
    """
    Initialise pin GPIO, direction max droite, gauche et valeur pour centrer les roues
    Centre les roues lors de l'initialisation
    Contrôle la direction des roues et permet d'arrêter les pulsations PWM.
    """
    def __init__(self, logger= object) -> None:
        """
        Initialise pin GPIO, direction max droite, gauche et valeur pour centrer les roues
        Centre les roues lors de l'initialisation
        """
        self.logger = logger
        self.logger.info("[GPIO CORE - ServoMotor] - Init Servo Motor...")

        self.MIN = int(2)
        self.MAX = int(10)
        
        FREQUENCY = int(50) #Hz
        SERVO_GPIO_PIN = int(12)

        self.DIRECTION_CENTER = int(90) # MAX Degree
        self.DIRECTION_LEFT = int(130) # MAX Degree
        self.DIRECTION_RIGHT =  int(65) # MAX Degree

        GPIO.setup(SERVO_GPIO_PIN, GPIO.OUT)
        
        self.SERVO_MOTOR_DIRECTION = GPIO.PWM(SERVO_GPIO_PIN, FREQUENCY) # Pin 18 - 50Hz
        
        self.SERVO_MOTOR_DIRECTION.start(0)

        self.set_servo_direction(self.DIRECTION_CENTER)
        
        time.sleep(0.5)

        self.SERVO_MOTOR_DIRECTION.ChangeDutyCycle(0)
        

    def set_servo_direction(self, direction=int) -> None:
        """
        Contrôle la direction des roues si la variable 'direction' respecte les valeurs maximum et minimum de braquage.
        Paramètre : direction type nombre entier
        Retourne : Aucun
        """
        if  self.DIRECTION_RIGHT <= direction <= self.DIRECTION_LEFT :

            duty = self.MAX / 180 * direction + self.MIN
            self.logger.info(f"[GPIO CORE - ServoMotor] - Direction set to: {direction} and Duty set to: {duty}")
            self.SERVO_MOTOR_DIRECTION.ChangeDutyCycle(duty)


    def stop_pulse(self) -> None :
        """
        Permet d'arrêter les pulsations PWM pour éviter l'activité du servo moteur quand on l'utilise pas
        """
        self.SERVO_MOTOR_DIRECTION.ChangeDutyCycle(0)