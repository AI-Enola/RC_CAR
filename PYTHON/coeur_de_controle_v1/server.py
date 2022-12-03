"""
Autheur : LA
Titre : WebSocket Server
Description : Le serveur WebSocket accepte un client WebSocket en utilisant le protocole IPV4 avec ou sans SSL et crée un session dans le coeur de contrôle.
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-02-05
"""



# Librairies Python
import asyncio
import websockets
import ssl

# Librairies customisées
from log import Log
from gpio_core import GPIOCore



class WebsocketServer:
    """
        Initialise la journalisation, l'IP, le port, le SSL (USE_SSL est vrai par défaut)
        Lance le serveur Websocket 
        Démarre une session dans le coeur de contrôle pour chaque client
    """
    
    def __init__(self, IP=str, PORT=int, USE_SSL=bool) -> None:
        """
        Initialise la journalisation, le WebSocket et SSL (USE_SSL est vrai par défaut)
        Paramètre WebSocket : IP : 0.0.0.0 (Écoute sur tout les interfaces) - PORT : 60004 (Changable)
        Retour : Aucun
        """

        # INITIALISE LA JOURNALISATION
        log = Log(log_in_file=True, 
                log_in_console=True, 
                encoding='utf-8', 
                filename='./log.txt', 
                filemode='a', 
                logger_name='WEBSOCKET PYTHON', 
                format='%(name)s - %(asctime)s - %(levelname)s: %(message)s')
                
        self.logger = log.get_logger() # RÉCUPÈRE L'OBJET DE JOURNALISATION
        
        self.logger.info(f"[SERVER WEBSOCKET] - Starting WEBSOCKET Server using IP/DOMAIN: {IP} and listening on Port: {PORT}")
        self.SERVER_INFO = [IP, PORT] # CONTIENT L'IP ET LE PORT

        self.USE_SSL = USE_SSL
        
        self.car_core = GPIOCore(logger=self.logger) # INITIALISE LE COEUR DE CONTRÔLE

         # INITIALISE SSL SI VOULU
        if  self.USE_SSL :
            
            self.logger.info("[SERVER WEBSOCKET] - Init SSL...")
            
            """ GÉNERER UN CERTIFICAT SSL ET LA CLÉ EN UTILISANT CETTE COMMANDE :
                openssl req -newkey rsa:4096 \
                -x509 \
                -sha256 \
                -days 3650 \
                -nodes \
                -out SSL_2022_01.crt \
                -keyout SSL_2022_01.key
            """
            
            SSL_CERTIFICATE = 'SSL_2022_01.crt'
            SSL_KEY = 'SSL_2022_01.key'
            
            self.SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.SSL_CONTEXT.load_cert_chain(SSL_CERTIFICATE, SSL_KEY, password=None) # ON A GÉNERÉ UN CERTIFICAT SSL SANS MOT DE PASSE UNIQUEMENT POUR CE PROJET

        
    async def serve_websocket(self) -> None:
        """
        Lance le serveur websocket
        Paramètre WebSocket : IP : 0.0.0.0 (Écoute sur tout les interfaces) - PORT : 60004 (Changable)
        Exception raised when serving websocket failed
        Une exception est appeler si la création du serveur WebSocket échoue
        Retourne : Aucun
        """

        self.logger.info("[SERVER WEBSOCKET] - Init websocket server...")
        
        try :

            if self.USE_SSL :
                
                self.logger.info("[SERVER WEBSOCKET] - Serving with SSL.")
                async with websockets.serve(self.car_core.session, self.SERVER_INFO[0], self.SERVER_INFO[1], ssl=self.SSL_CONTEXT):
                    await asyncio.Future()  # RELANCE UNE NOUVELLE INSTANCE SI L'UTILISATEUR QUITTE L'INSTANCE
                    
            else: 
                
                self.logger.info("[SERVER WEBSOCKET] - Serving without SSL.")
                async with websockets.serve(self.car_core.session, self.SERVER_INFO[0], self.SERVER_INFO[1]):
                    await asyncio.Future()  # RELANCE UNE NOUVELLE INSTANCE SI L'UTILISATEUR QUITTE L'INSTANCE
        
        except :
            self.logger.error("[SERVER WEBSOCKET] - Serving FAILED !")
            raise
        
        
        
if __name__ == "__main__":
    """
        INITIALISE L'OBJET ET LANCE L'INSTANCE DU SERVEUR WEBSOCKET EN ASYNCHRONE
    """
    ws = WebsocketServer(IP="0.0.0.0", PORT=60004, USE_SSL=True)
    asyncio.run(ws.serve_websocket())