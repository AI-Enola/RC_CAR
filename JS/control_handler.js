/*
Auteur : LA
Description : Permet de gérer les joysticks, récupérer les données des joysticks, emvoyer des commandes au serveur 
et afficher sur l'interface
Classe JoystickController voir code source : view-source:https://www.cssscript.com/demo/touch-joystick-controller/
Version : 2
*/

class JoystickController {
        // CONTROLLER FOR VIRTUAL JOYSTICKS

        // CODE SOURCE : view-source:https://www.cssscript.com/demo/touch-joystick-controller/
        // MODIFIED BY : LA

	constructor( stickID, maxDistance, deadzone ) {
                // stickID: ID of HTML element (representing joystick) that will be dragged
	        // maxDistance: maximum amount joystick can move in any direction
	        // deadzone: joystick must move at least this amount from origin to register value change

		this.id = stickID;
		let stick = document.getElementById(stickID);

		// location from which drag begins, used to calculate offsets
		this.dragStart = null;

		// track touch identifier in case multiple joysticks present
		this.touchId = null;
		
		this.active = false;
		this.value = { x: 0, y: 0 }; 

		let self = this;

		function handleDown(event) {
                        
		        self.active = true;

			// all drag movements are instantaneous
			stick.style.transition = '0s';

			// touch event fired before mouse event; prevent redundant mouse event from firing
			event.preventDefault();

                        if (event.changedTouches)
                                self.dragStart = { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY };
                        else
                                self.dragStart = { x: event.clientX, y: event.clientY };

                        // if this is a touch event, keep track of which one
                        if (event.changedTouches)
                                self.touchId = event.changedTouches[0].identifier;
		}
		

		function handleMove(event) {

                        if ( !self.active ) return;

                        // if this is a touch event, make sure it is the right one
                        // also handle multiple simultaneous touchmove events
                        let touchmoveId = null;

                        if (event.changedTouches) {

                                for (let i = 0; i < event.changedTouches.length; i++) {

                                        if (self.touchId == event.changedTouches[i].identifier) {
                                                touchmoveId = i;
                                                event.clientX = event.changedTouches[i].clientX;
                                                event.clientY = event.changedTouches[i].clientY;
                                        }
                                }

                                if (touchmoveId == null) return;
                        }

                        const xDiff = event.clientX - self.dragStart.x;
                        const yDiff = event.clientY - self.dragStart.y;

                        const angle = Math.atan2(yDiff, xDiff);
                        const distance = Math.min(maxDistance, Math.hypot(xDiff, yDiff));
                        
                        const xPosition = distance * Math.cos(angle);
                        const yPosition = distance * Math.sin(angle);

                        // move stick image to new position
                        stick.style.transform = `translate3d(${xPosition}px, ${yPosition}px, 0px)`;

                        // deadzone adjustment
                        const distance2 = (distance < deadzone) ? 0 : maxDistance / (maxDistance - deadzone) * (distance - deadzone);
                        
                        const xPosition2 = distance2 * Math.cos(angle);
                        const yPosition2 = distance2 * Math.sin(angle);
                        
                        const xPercent = parseFloat((xPosition2 / maxDistance).toFixed(4));
                        const yPercent = parseFloat((yPosition2 / maxDistance).toFixed(4));
                        
                        self.value = { x: xPercent, y: yPercent };
		}

                
		function handleUp(event) {

                        if ( !self.active ) return;

                        // if this is a touch event, make sure it is the right one
                        if (event.changedTouches && self.touchId != event.changedTouches[0].identifier) return;

                        // transition the joystick position back to center
                        stick.style.transition = '.2s';
                        stick.style.transform = `translate3d(0px, 0px, 0px)`;

                        // reset everything
                        self.value = { x: 0, y: 0 };
                        self.touchId = null;
                        self.active = false;
		}

                // EVENT BLOCK
		stick.addEventListener('mousedown', handleDown);
		stick.addEventListener('touchstart', handleDown);

		document.addEventListener('mousemove', handleMove, {passive: false});
		document.addEventListener('touchmove', handleMove, {passive: false});

		document.addEventListener('mouseup', handleUp);
		document.addEventListener('touchend', handleUp);  
	}
}



class ControlDriver {
        /*
                CREATE DATA TEMPLATE FOR SERVER
                SET MIN, MAX AND STEP FOR DATA TRACKING
        */
        constructor() {

                // MOTOR POWER IN %
                const MIN_MOTOR = 5
                const MAX_MOTOR = 100
                const TRACKING_MOTOR_STEP = 5

                // DIRECTION ANGLE IN DEGREE °
                const MIN_DIRECTION = 65
                const MAX_DIRECTION = 130
                const TRACKING_DIRECTION_STEP = 1

                // JSON OF JOYSTICK CAPTURED DATA 
                this.joystick_direction = {"JOYSTICK_ACTION": "SERVO_DIRECTION", "POSITION": 0};
                this.joystick_power = {"JOYSTICK_ACTION": "MOTOR_POWER", "POSITION": 0};

                // DATA TO CAPTURE - Capture data only if IRL data is include in capture data set
                this.motor_power_set = createArray(MIN_MOTOR, MAX_MOTOR, TRACKING_MOTOR_STEP);

                this.servo_direction_set = createArray(MIN_DIRECTION, MAX_DIRECTION, TRACKING_DIRECTION_STEP);
                delete this.servo_direction_set[this.servo_direction_set.indexOf(90)]; // Remove 90° from direction capture set - Avoid sending data when servo unused

                // GET ANGLE IN RADIAN FOR JOYSTICK DIRECTION
                this.radian = 180 / Math.PI;

                // Y AXIS MAX TO GET 135° MAX AND 45° MIN - MATCH CAR FRONT AXE DIRECTION FOR JOYSTICK
                this.y_max = 1;

                // STORE DIRECTION DATA IN DEGREE
                this.degree = 0;

                // STORE MOTOR POWER IN PERCENTAGE
                this.motor_power = 0;

                // Get arrows ID's to change style
                this.arrow_up = document.getElementById("arrow_up");
                this.arrow_down = document.getElementById("arrow_down");
                this.arrow_left = document.getElementById("arrow_left");
                this.arrow_right = document.getElementById("arrow_right");

                let self = this;


		// HANDLE MOUSEUP EVENT - SEND COMMAND TO AUTO STOP MOTOR AND CENTER WHEELS
                document.getElementById("motor_stick").onmouseup = function() {send_command("STOP_MOTOR")};
                document.getElementById("direction_stick").onmouseup = function() {send_command("CENTER_SERVO")};

                // HANDLE TOUCH SCREEN EVENT - SEND COMMAND TO AUTO STOP MOTOR AND CENTER WHEELS
                document.getElementById("motor_stick").ontouchend = function() {send_command("STOP_MOTOR")};
                document.getElementById("direction_stick").ontouchend = function() {send_command("CENTER_SERVO")};


                // HANDLE COMPUTER ARROW KEY AS COMMAND TO CONTROL RC CAR
                document.onkeydown = function (e) {

                        switch (e.key) {

                                case "ArrowUp":
                                        self.arrow_up.style.background = "blue";
                                        e.preventDefault(); // AVOID SCROLL UP
                                        send_command("MOTOR_FORWARD");
                                        break;

                                case "ArrowDown": 
                                        self.arrow_down.style.background = "blue";
                                        e.preventDefault(); // AVOID SCROLL DOWN
                                        send_command("MOTOR_BACKWARD");
                                        break;

                                case "ArrowLeft":
                                        self.arrow_left.style.background = "blue";
                                        e.preventDefault(); // AVOID SCROLL LEFT
                                        send_command("DIRECTION_LEFT");
                                        break;

                                case "ArrowRight": // AVOID SCROLL RIGHT
                                        self.arrow_right.style.background = "blue";
                                        e.preventDefault();
                                        send_command("DIRECTION_RIGHT");
                                        break; 
                        }


                };

                document.onkeyup = function (e) {

                        switch (e.key) {

                                case "ArrowUp":
                                        self.arrow_up.style.background = "#5a5c69";
                                        e.preventDefault(); // AVOID SCROLL UP
                                        send_command("STOP_MOTOR");
                                        break;

                                case "ArrowDown": 
                                        self.arrow_down.style.background = "#5a5c69";
                                        e.preventDefault(); // AVOID SCROLL DOWN
                                        send_command("STOP_MOTOR");
                                        break;

                                case "ArrowLeft":
                                        self.arrow_left.style.background = "#5a5c69";
                                        e.preventDefault(); // AVOID SCROLL LEFT
                                        send_command("CENTER_SERVO");
                                        break;

                                case "ArrowRight": // AVOID SCROLL RIGHT
                                        self.arrow_right.style.background = "#5a5c69";
                                        e.preventDefault();
                                        send_command("CENTER_SERVO");
                                        break; 
                        }
                };

                function createArray(start, end, step) {
                        /*
                                Create an array which content an interval of numbers
                                Parameters : start is min value, end is max value and step represent sensibility of data. 
                                Step of 1 will be more accurate then a step of 10
                                Used to set min, max and sensibility of trackable data from the joystick (direction and power)
                                
                                Return : Array of data
                        */
                        const newArray = []; 

                        for (let i = start; i <= end; i += step) {
                                newArray.push(i);
                        }
                        return newArray;
                }
        }
}



let JOYSTICK_DIRECTION = new JoystickController("direction_stick", 64, 0.5);
let JOYSTICK_POWER = new JoystickController("motor_stick", 64, 8);

let DRIVER = new ControlDriver();


function update() {
        // KEEP RUNNING FOREVER TO SEND REALTIME DATA TO SERVER

        // GET DATA IN DEGREE
        DRIVER.degree = Math.atan2(DRIVER.y_max, JOYSTICK_DIRECTION.value.x) * DRIVER.radian;

        // GET DATA AS PERCENTAGE
        DRIVER.motor_power = JOYSTICK_POWER.value.y * 100;

        // GET FIXED NUMBER NOT FLOAT
        DRIVER.joystick_direction.POSITION = DRIVER.degree.toFixed();
        DRIVER.joystick_power.POSITION = DRIVER.motor_power.toFixed();

        // SHOW REALTIME DATA ON UI
        document.getElementById("joystick_direction").innerText = DRIVER.joystick_direction.POSITION + "°";
	document.getElementById("joystick_accelerator").innerText = DRIVER.joystick_power.POSITION + "%";

        // SERVO DIRECTION COMMAND
        // Check if motor power number is included in motor power set - Limit data throught websocket
        if (DRIVER.servo_direction_set.includes(DRIVER.joystick_direction.POSITION) || DRIVER.servo_direction_set.includes(Math.abs(DRIVER.joystick_direction.POSITION))) {
                console.log("RAW Joystick 1 data: - X axis data: " + JOYSTICK_DIRECTION.value.x + "- Servo Direction (Degree): " + DRIVER.degree);
                send_command(JSON.stringify(DRIVER.joystick_direction));
        }

        // MOTOR POWER COMMAND
        // Check if motor power number is included in motor power set - Limit data throught websocket
        if (DRIVER.motor_power_set.includes(DRIVER.joystick_power.POSITION) || DRIVER.motor_power_set.includes(Math.abs(DRIVER.joystick_power.POSITION))) {
                console.log("RAW Joystick 2 Data - Y axis data: " + JOYSTICK_POWER.value.y + "- Motor Power (%): " + DRIVER.motor_power);
                send_command(JSON.stringify(DRIVER.joystick_power));
        }
}


function loop() {
	requestAnimationFrame(loop);
	update();
}


loop();