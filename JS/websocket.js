/*
Author : LA
Description : Permet d'établir une connexion entre le client Javascript et le serveur Python
Version : 1.0
*/

/*
Multiple sélection selon l'adresse IP du serveur
IP et PORT du serveur WebSocket
WSS = WebSocketSecure avec TLS/SSL  
*/
const SOCKET = new WebSocket('wss://192.168.2.25:60004');
// const SOCKET = new WebSocket('wss://10.42.0.254:60004');
// const SOCKET = new WebSocket('wss://192.168.1.160:60004');

/*
Statut de connexion :
- CONNECTÉ : Lié au serveur
- DÉCONNECTÉ : Aucun lien étalie avec le serveur
- CONNEXION : Établissement de la connexion avec le serveur

is_connected variable boolean lier au statut du client
*/
const STATUS = 'STATUS: ';
const STATUS_MODE = {ONLINE: 'CONNECTED', OFFLINE: 'DISCONNECTED', CONNECTING: 'CONNECTING'}

let is_connected = false; // CONNECTED TO THE SERVER


/*
Lorsque que la connexion est en établissement avec le serveur, le client envoie un message "CONNECTED"
cela signal le serveur que le client est connecté.
*/
SOCKET.addEventListener('open', function (event) {
        document.getElementById("status").innerHTML = STATUS + STATUS_MODE.CONNECTING;
        SOCKET.send(STATUS_MODE.ONLINE);

});


/*
Lorsque la connexion est terminé entre le client et le serveur,  on signale au client qu'il est déconnecté du serveur
*/
SOCKET.addEventListener('close', function (event) {
        is_connected = false;
        document.getElementById("status").innerHTML = STATUS + STATUS_MODE.OFFLINE;
        
        console.log('Connection Closed.');

});


/*
Le point d'intéraction entre le client et le serveur est dans cette événement 'message'
On reçoit les messages du serveur à l'intérieur de cette fonction et on les traites.
On reçoit principalement le mode de conduite venant du serveur.
Note : Besoin d'optimisation
*/
SOCKET.addEventListener('message', function (event) {
        if (event.data == STATUS_MODE.ONLINE) {
                is_connected = true;
                document.getElementById("status").innerHTML = STATUS + STATUS_MODE.ONLINE;
                send_command("GET_DRIVE_MODE"); //NEED TO BE OPTIMIZED
        } else if (event.data == "CURRENT_DRIVING_MODE:ECO") {
                document.getElementById("current_driving_mode").innerHTML = "Mode: ECO";
        } else if (event.data == "CURRENT_DRIVING_MODE:NORMAL") {
                document.getElementById("current_driving_mode").innerHTML = "Mode: NORMAL";
        } else if (event.data == "CURRENT_DRIVING_MODE:SPORT") {
                document.getElementById("current_driving_mode").innerHTML = "Mode: SPORT";
        } else if (event.data == "CURRENT_DRIVING_MODE:TYPE_R") {
                 document.getElementById("current_driving_mode").innerHTML = "Mode: TYPE R";
        }

        console.log(`Message from server : ${event.data}`);

});


/*
Fonction pour envoyer des données au serveur.
*/
function send_command(action_id) {
        console.log(`User action : ${action_id}`);
        return SOCKET.send(action_id);
}

/*
Toutes les 500ms, le client demande les données des capteurs pour les recevoirs.
*/
var intervalId = window.setInterval(function(){
        if (is_connected) {
                send_command("GET_DATA_MONITORING");
        }
        
}, 500);