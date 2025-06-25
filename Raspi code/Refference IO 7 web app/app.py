from flask import Flask, request, jsonify, send_from_directory
import rtde_io # Gebruik rtde_io voor I/O operaties
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Robot Configuration ---
ROBOT_IP = "192.168.0.43"  # VERVANG DIT MET HET IP-ADRES VAN JE ROBOT!
DIGITAL_OUT_PIN = 7       # De digitale output pin die we willen aansturen

app = Flask(__name__, static_folder='.', static_url_path='')

def execute_io_command(action_type):
    io_interface = None  # Initialize to None

    try:
        logging.info(f"Poging tot verbinden met robot I/O op {ROBOT_IP}...")
        # De constructor probeert de verbinding op te zetten.
        # Als dit faalt, wordt een exceptie verwacht (bijv. socket error).
        io_interface = rtde_io.RTDEIOInterface(ROBOT_IP)
        logging.info("RTDE IO Interface object aangemaakt; verbinding wordt als succesvol beschouwd als geen exceptie is opgetreden.")

        message = ""
        if action_type == 'set_do_on':
            io_interface.setStandardDigitalOut(DIGITAL_OUT_PIN, True)
            message = f"Standard Digital Output {DIGITAL_OUT_PIN} AAN gezet."
            logging.info(message)
        elif action_type == 'set_do_off':
            io_interface.setStandardDigitalOut(DIGITAL_OUT_PIN, False)
            message = f"Standard Digital Output {DIGITAL_OUT_PIN} UIT gezet."
            logging.info(message)
        else:
            logging.warning(f"Onbekende I/O actie ontvangen: {action_type}")
            # Het is goed om hier ook een 'status: error' terug te geven
            return {"message": "Onbekende I/O actie", "status": "error"}

        return {"message": message, "status": "success"}

    # Specifieke excepties voor RTDE (indien bekend) of meer generieke netwerkfouten
    # Bijv. als de robot niet bereikbaar is, kan de constructor een socket.error of TimeoutError geven.
    except ConnectionRefusedError as e: # Voorbeeld van specifieke netwerkfout
        logging.error(f"Verbinding geweigerd met robot I/O op {ROBOT_IP}: {e}")
        return {"message": f"Verbinding geweigerd I/O ({ROBOT_IP}): {e}", "status": "error"}
    except TimeoutError as e: # Voorbeeld
        logging.error(f"Timeout tijdens verbinden met robot I/O op {ROBOT_IP}: {e}")
        return {"message": f"Timeout verbinding I/O ({ROBOT_IP}): {e}", "status": "error"}
    except Exception as e: 
        # Vang andere mogelijke fouten, inclusief die van RTDE zelf.
        logging.error(f"Een algemene fout is opgetreden tijdens I/O commando: {e}", exc_info=True)
        return {"message": f"Algemene fout I/O: {e}", "status": "error"}
    finally:
        # io_interface zal alleen een waarde hebben als de constructor succesvol was (of deels).
        if io_interface: 
            try:
                # Er is geen isConnected() check; we proberen gewoon los te koppelen.
                io_interface.disconnect()
                logging.info("RTDE IO interface loskoppelen geprobeerd.")
            except Exception as e_disc:
                logging.error(f"Fout bij loskoppelen RTDE IO: {e_disc}")

@app.route('/')
def index():
    return send_from_directory('.', 'Html.html')

@app.route('/api/robot_command', methods=['POST'])
def robot_command_endpoint():
    data = request.get_json()
    action = data.get('action')
    
    if not action:
        return jsonify({'message': 'Geen actie gespecificeerd', 'status': 'error'}), 400

    logging.info(f"Web commando (I/O) ontvangen: {action}")
    
    result = execute_io_command(action) # Gebruik de nieuwe I/O functie
    
    if result.get("status") == "error":
        return jsonify(result), 500
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)