/*
Auteur : LA
Description : Permet de prendre connaissance du type du terminal selon le navigateur
Affiche ou cache les joysticks ou flèches selon le terminal (Mobile ou ordinateur)
Version : 1
*/

class DeviceHandler {

    // GET NAVIGATOR AGENT FROM CLIENT DEVICE

    constructor () {

        // ID FROM DIV ELEMENT
        this.joystick_box = document.getElementById("joystick_row");
        this.arrow_box = document.getElementById("arrow_row");

        this.is_mobile = getNavigatorAgent(); // USED TO SEE IF CLIENT IS USING A MOBILE OR A COMPUTER

        // GET NAVIGATOR AGENT OF CLIENT DEVICE
        function getNavigatorAgent() {

            if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                return true;
            } else {
                return false;
            }
        }
    }
}


let DEVICE_HANDLER = new DeviceHandler();

// DISPLAY JOYSTICKS ON MOBILE AND ARROW KEYS ON COMPUTER
function display_controller() {
    
    if (DEVICE_HANDLER.is_mobile) { // HIDE ARROW KEYS AND DISPLAY JOYSTICKS
        DEVICE_HANDLER.joystick_box.style.display = 'block';
        DEVICE_HANDLER.arrow_box.style.display = 'none';
        
    } else { // DISPLAY ARROW KEYS AND HIDE JOYSTICKS
        DEVICE_HANDLER.joystick_box.style.display = 'none';
        DEVICE_HANDLER.arrow_box.style.display = 'block';
    }
}

display_controller();