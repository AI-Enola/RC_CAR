"""
Autheur : LA
Titre : Coeur de contrôle GPIO
Description : 
Version : 1.5
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-04-12
"""


# Python Libraries
import json
import re
import time

# Custom Libraries
from VL53L0X_ToF.VL53L0X_Handler import ToFSensor
from GYRO_SENSOR.gyro_sensor_handler import GyroSensor
from MOTOR.motor_handler import DriveMode, MotorDriver
from MOTOR.servo_motor_handler import ServoMotor
from LED.led_board_handler import BoardLED


class RxTx :
    """
    Utilisé pour communiquer avec le client. Peut envoyer des données vers le client et de recevoir venant du client.
    """
    
    def __init__(self, logger=object, car_core=object):

        self.logger = logger
        self.logger.info("[SERVER RX_TX] - Init communication Rx & Tx...")
        self.websocket = object # INIT VARIABLE TO RECEIVE TYPE OBJECT WHEN SESSION HAS STARTED
        self.car_core = car_core

        self.USER_DISCONNECTED = "DISCONNECTED"


    async def receive_from_client(self) -> str:
        """
        Vide la variable message avant de recevoir des données venant du client
        Si la reception échoue il y a une exception actif
        Retourne : Message de type String
        """
        
        self.logger.info("[SERVER WEBSOCKET] - Receiving from client...")
        
        message = str("") # VIDE
        
        try: 
            message = await self.websocket.recv() # RECEIVE COMMAND FROM CLIENT
        
        except:

            self.car_core.get_command(self.USER_DISCONNECTED) # Send user disconnected flag to turn off status led
            self.logger.error(f"[SERVER WEBSOCKET] - Receiving from client FAILED!")
            raise
            
        if message :
            self.logger.info("[SERVER WEBSOCKET] - Message Received from client.\n")
        
        else :
            self.logger.info("[SERVER WEBSOCKET] - Message Received from client is empty !\n")
        
        return message
        
    

    async def send_to_client(self, data_out=str) -> None:
        """
        Envoie donnée au client
        Parametres : data_out type String
        Si erreur pendant l'envoie vers le client il y a une exception actif
        Retourne : Auncun
        """

        self.logger.info("[SERVER WEBSOCKET] - Sending to client...")
        
        try :
            await self.websocket.send(data_out)
            
        except:
            self.car_core.get_command(self.USER_DISCONNECTED) # Send user disconnected flag to turn off status led
            self.logger.error(f"[SERVER WEBSOCKET] - Sending to client FAILED!")
            raise
        
        self.logger.info("[SERVER WEBSOCKET] - Data Sended to client...\n")



class GPIOCore:

    """
        Initialise les composantes controllable, la communication
        Possède une session pour l'utilisateur et repond au commande
    """

    def __init__(self, logger=object) -> None:
        
        self.logger = logger
        self.logger.info("[GPIO CORE - CORE] - Init GPIO Core...")

        # Init objects
        self.RX_TX = RxTx(logger=logger, car_core=self) # Init Rx Tx for communication
        self.LED_STATUS = BoardLED(logger=logger)
        self.SERVO_MOTOR = ServoMotor(logger=logger)
        self.DRIVE_MODE = DriveMode(logger=logger)
        self.MOTOR_DRIVER = MotorDriver(logger=logger, drive_mode_class=self.DRIVE_MODE)
        self.TOF_SENSOR = ToFSensor(logger=logger)
        self.GYRO_SENSOR = GyroSensor(logger=logger)
        
        self.logger.info("[GPIO CORE - CORE] - GPIO Core initialized.")

    
    async def session(self, websocket) -> None : # CALLED FROM SERVER.PY - Server put client into a session 
        """
            Start session for client websocket
            Démarre la session en ajoutant le client à la communication
            Reste actif tant que l'utilisateur est connecté
            Returne : Aucun
        """
        self.logger.info("[SERVER WEBSOCKET] - Starting session...")

        self.websocket = websocket # ADD WEBSOCKET HANDLER TO COMMUNICATE WITH CLIENT

        self.logger.info("[SERVER WEBSOCKET] - Communication setup...")
        self.RX_TX.websocket = websocket # Push websocket client object to RX_TX object - If another user is connected older will be overwrited by new user

        await self.RX_TX.send_to_client(data_out="CONNECTED")
        
        while True: # KEEP RUNNING INSTANCE

            message = str("")
            message_for_client = str("")

            message = await self.RX_TX.receive_from_client()
            self.logger.info(f"[SERVER WEBSOCKET] - Message from client : {message}")
            
            if message : # Check if message from client is not empty
                
                message_for_client = self.get_command(message)

                if message_for_client: # Check if message for client is not empty
                    await self.RX_TX.send_to_client(data_out=message_for_client)


    def get_command(self, cmd) -> str:
        """
            Traitement des commandes de type JSON et de type normal
            Interaction avec les composantes
            Commande entrante pour le serveur et commande sortante pour le client
            Retourne : String
        """
        self.logger.info("[GPIO CORE - CORE] - Processing command...")

        if re.findall("^{.*}$", cmd) :

            self.logger.info(f"[GPIO CORE - CORE] - Command: '{cmd}' is type JSON.")

            converted_json = json.loads(cmd)

            if converted_json["JOYSTICK_ACTION"] == "SERVO_DIRECTION" :
                self.SERVO_MOTOR.set_servo_direction(direction= abs(int(converted_json["POSITION"])))

            elif converted_json["JOYSTICK_ACTION"] == "MOTOR_POWER" :
                self.MOTOR_DRIVER.set_motor_power(power= int(converted_json["POSITION"]))


        else :

            if cmd == "CONNECTED" or cmd == "DISCONNECTED" :
                self.LED_STATUS.set_status_led(action=cmd)

            elif cmd == "STOP_MOTOR" :
                self.MOTOR_DRIVER.set_motor_power(power=int(0))

            elif cmd == "CENTER_SERVO" :
                self.SERVO_MOTOR.set_servo_direction(direction=self.SERVO_MOTOR.DIRECTION_CENTER)
                time.sleep(0.15)
                self.SERVO_MOTOR.stop_pulse()

            elif cmd == "MOTOR_FORWARD" :
                self.MOTOR_DRIVER.set_motor_power(power= self.DRIVE_MODE.drive_mode)

            elif cmd == "MOTOR_BACKWARD" :
                self.MOTOR_DRIVER.set_motor_power(power=self.DRIVE_MODE.REVERSE_MAX)

            elif cmd == "DIRECTION_LEFT" :
                self.SERVO_MOTOR.set_servo_direction(direction=self.SERVO_MOTOR.DIRECTION_LEFT)

            elif cmd == "DIRECTION_RIGHT" :
                self.SERVO_MOTOR.set_servo_direction(direction=self.SERVO_MOTOR.DIRECTION_RIGHT)

            elif cmd == "DRIVE_MODE_ECO" :
                self.DRIVE_MODE.change_drive_mode(drive_mode=self.DRIVE_MODE.DRIVE_MODE_ECO)
                return self.DRIVE_MODE.get_drive_mode()
                
            elif cmd == "DRIVE_MODE_NORMAL" :
                self.DRIVE_MODE.change_drive_mode(drive_mode=self.DRIVE_MODE.DRIVE_MODE_NORMAL)
                return self.DRIVE_MODE.get_drive_mode()
                
            elif cmd == "DRIVE_MODE_SPORT" :
                self.DRIVE_MODE.change_drive_mode(drive_mode=self.DRIVE_MODE.DRIVE_MODE_SPORT)
                return self.DRIVE_MODE.get_drive_mode()
                
            elif cmd == "DRIVE_MODE_TYPER" :
                self.DRIVE_MODE.change_drive_mode(drive_mode=self.DRIVE_MODE.DRIVE_MODE_TYPE_R)
                return self.DRIVE_MODE.get_drive_mode()

            elif cmd == "GET_DRIVE_MODE" : # TEMPORARY
                return self.DRIVE_MODE.get_drive_mode()

            elif cmd == "GET_DATA_MONITORING" :
                data = {
                "TOF_SENSOR" : self.TOF_SENSOR.get_data(),
                "GYRO_SENSOR" : self.GYRO_SENSOR.get_data()
                }

                return json.dumps(data)
