import time
import logging

# Probeer de juiste bibliotheken te importeren
try:
    import rtde_control
    import rtde_receive
    import rtde_io
except ImportError:
    pass # Prima als mock mode aan staat

try:
    import lgpio
except ImportError:
    lgpio = None

# --- Configuratie UR Robot ---
ROBOT_IP = "192.168.0.43"
TOOL_SPEED = 0.25
TOOL_ACCELERATION = 0.5

# --- Configuratie Stappenmotor ---
STEP_PIN = 17
DIR_PIN = 27
STAPPEN_VOOR_180_GRADEN = 1600
VERTRAGING = 0.003
GPIO_CHIP = 0

# --- Configuratie Arduino Communicatie ---
SIGNAAL_PIN = 26 # Output: signaal naar Arduino (STOP/HERVAT)
RECEIVE_PIN = 16 # Input: signaal van Arduino (KLAAR)

# --- Definities Robotposities (waypoints) ---
startpos = [0.2472, 0.5000, 0.2171, 0, 0, 4.678]
oppakpos = [0.2472, 0.6502, 0.2171, 0, 0, 4.678]
oppakhoogte = [0.2472, 0.6502, 0.2276, 0, 0, 4.678] # Deze wordt niet direct gebruikt, maar kan handig zijn als referentie
opgepakt = [0.2472, 0.6502, 0.4937, 0, 0, 4.678]
approach = [0.5826 , 0.4074 , 0.5543 , 0 , 0, 4.716]

# Er is geen 'piston_approach' meer in de nieuwe coördinaten,
# de 'a' positie van elke rij lijkt die rol over te nemen.
piston_posities = [
    # --- Definities Piston Posities kant 1 ---
    {'a': [0.6910, 0.7435, 0.5124, 1.578, 1.359, 4.087], 'b': [0.6910, 0.7865, 0.5124, 1.578, 1.359, 4.087], 'c': [0.6910, 0.7865, 0.5384, 1.578, 1.359, 4.087], 'd': [0.6910, 0.7435, 0.5384, 1.578, 1.359, 4.087]},
    {'a': [0.6880, 0.6996, 0.4520, 1.578, 1.369, 4.087], 'b': [0.6880, 0.7426, 0.4520, 1.578, 1.369, 4.087], 'c': [0.6880, 0.7426, 0.4780, 1.578, 1.369, 4.087], 'd': [0.6880, 0.6996, 0.4780, 1.578, 1.369, 4.087]},
    {'a': [0.6838, 0.6534, 0.3935, 1.578, 1.359, 4.087], 'b': [0.6838, 0.6964, 0.3935, 1.578, 1.359, 4.087], 'c': [0.6838, 0.6964, 0.4195, 1.578, 1.359, 4.087], 'd': [0.6838, 0.6534, 0.4195, 1.578, 1.359, 4.087]},
    {'a': [0.6805, 0.6064, 0.3335, 1.578, 1.359, 4.087], 'b': [0.6805, 0.6494, 0.3335, 1.578, 1.359, 4.087], 'c': [0.6805, 0.6494, 0.3595, 1.578, 1.359, 4.087], 'd': [0.6805, 0.6064, 0.3595, 1.578, 1.359, 4.087]},
    {'a': [0.6748, 0.5608, 0.2732, 1.578, 1.359, 4.087], 'b': [0.6748, 0.6038, 0.2732, 1.578, 1.359, 4.087], 'c': [0.6748, 0.6038, 0.2992, 1.578, 1.359, 4.087], 'd': [0.6748, 0.5608, 0.2992, 1.578, 1.359, 4.087]},
]
piston_posities_terug = [
    # --- Definities Piston Posities kant 2 --- 
    {'a': [0.6887, 0.7197, 0.5393, 1.578, 1.359, 4.087], 'b': [0.6887, 0.7627, 0.5393, 1.578, 1.359, 4.087], 'c': [0.6887, 0.7627, 0.5653, 1.578, 1.359, 4.087], 'd': [0.6887, 0.7197, 0.5653, 1.578, 1.359, 4.087]},
    {'a': [0.6869, 0.6762, 0.4827, 1.578, 1.359, 4.087], 'b': [0.6869, 0.7192, 0.4827, 1.578, 1.359, 4.087], 'c': [0.6869, 0.7192, 0.5087, 1.578, 1.359, 4.087], 'd': [0.6869, 0.6762, 0.5087, 1.578, 1.359, 4.087]},
    {'a': [0.6814, 0.6265, 0.4222, 1.578, 1.359, 4.087], 'b': [0.6814, 0.6695, 0.4222, 1.578, 1.359, 4.087], 'c': [0.6814, 0.6695, 0.4482, 1.578, 1.359, 4.087], 'd': [0.6814, 0.6265, 0.4482, 1.578, 1.359, 4.087]},
    {'a': [0.6781, 0.5748, 0.3622, 1.578, 1.359, 4.087], 'b': [0.6781, 0.6178, 0.3622, 1.578, 1.359, 4.087], 'c': [0.6781, 0.6178, 0.3882, 1.578, 1.359, 4.087], 'd': [0.6781, 0.5748, 0.3882, 1.578, 1.359, 4.087]},
    {'a': [0.6764, 0.5236, 0.3052, 1.578, 1.359, 4.087], 'b': [0.6764, 0.5666, 0.3052, 1.578, 1.359, 4.087], 'c': [0.6764, 0.5666, 0.3312, 1.578, 1.359, 4.087], 'd': [0.6764, 0.5236, 0.3312, 1.578, 1.359, 4.087]},
]

Approach_Big_rek = [0.0724 , -0.4824 , 0.2538 , 0.166 , -0.058 , -4.721]

B_1_1 = [0.1566 , -0.7091 , 0.6927 , 0.240 , -0.104 , -4.717]
B_1_2 = [0.1566 , -0.9091 , 0.6927 , 0.240 , -0.104 , -4.717]
B_1_3 = [0.1566 , -0.9091 , 0.6589 , 0.240 , -0.104 , -4.717]
B_1_4 = [0.1566 , -0.9123 , 0.6391 , 0.143 , -0.009 , -4.724]

B_2_1 = [0.1666 , -0.7148 , 0.2792 , 0.271 , -0.162 , -4.713]
B_2_2 = [0.1666 , -0.9148 , 0.2792 , 0.271 , -0.162 , -4.713]
B_2_3 = [0.1666 , -0.9148 , 0.2498 , 0.271 , -0.162 , -4.713]
B_2_4 = [0.1666 , -0.9167 , 0.2369 , 0.120 , -0.013 , -4.724]

B_3_1 = [0.1725 , -0.7229 , -0.1311 , 0.287 , - 0.178 , -4.710]
B_3_2 = [0.1725 , -0.9229 , -0.1311 , 0.287 , - 0.178 , -4.710]
B_3_3 = [0.1725 , -0.9229 , -0.1621 , 0.287 , - 0.178 , -4.710]
B_3_4 = [0.1725 , -0.9229 , -0.1681 , 0.093 , 0.014 , -4.724]


# --- Definities Payload ---
payloads = {
    'leeg': [1.470, [0.007, -0.009, 0.049]],
    'rek': [3.130, [0.000, -0.028, 0.087]],
    'p_05': [3.820, [-0.002, -0.007, 0.104]],
    'p_10': [4.630, [-0.003, -0.001, 0.109]],
    'p_15': [5.250, [-0.007, -0.008, 0.123]],
    'p_20': [5.960, [-0.007, -0.019, 0.123]],
    'p_25': [6.500, [-0.005, -0.038, 0.140]],
    'p_25t' :[6.500, [0.001, -0.037, 0.115]],
    'p_30' :[7.320, [0.003, -0.023, 0.113]],
    'p_35' :[7.840, [-0.003, -0.019, 0.127]],
    'p_40' :[8.410, [-0.001, -0.023, 0.112]],
    'p_45' :[9.080, [-0.003, -0.027, 0.130]],
    'p_50' :[9.780, [-0.006, -0.037, 0.160]]
}
payload_keys = ['p_05', 'p_10', 'p_15', 'p_20', 'p_25',]
payload_keys_terug = ['p_25t', 'p_30', 'p_35', 'p_40', 'p_45', 'p_50']

Turn_1 = [-0.1288 , 0.7298 , 0.5066 , 0.041 , 0.042 , -1.554] 
Turn_2 = [-0.1288 , 0.7298 , 0.3566 , 0.041 , 0.042 , -1.554] 
Turn_3 = [-0.1288 , 0.7322 , 0.3427 , 0 , 0 , 4.729]
Turn_4 = [-0.1288 , 0.5244 , 0.3427 , 0 , 0 , 4.729]
Turn_5 = [-0.1246 , 0.6893 , 0.3427 , 0 , 0 , 4.729]
Turn_6 = [-0.1246 , 0.6893 , 0.3663 , 0 , 0 , 4.729]
Turn_7 = [-0.1246 , 0.6893 , 0.5148 , 0 , 0 , 4.729]

# --- Logging Configuratie ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - MODE 2 (COMBI) - %(message)s', handlers=[logging.FileHandler("robot_errors.log")])

# --- Communicatie Functies ---

def stuur_arduino_signaal(h, pin, state):
    """Stuur een signaal (HIGH/LOW) naar de Arduino."""
    status = "STOP" if state else "HERVAT"
    logging.info(f"Signaal naar Arduino sturen: {status} (Pin {pin} -> {'HIGH' if state else 'LOW'})")
    lgpio.gpio_write(h, pin, 1 if state else 0)

def wacht_op_arduino(h, pin):
    """
    Wacht oneindig op een HIGH signaal van de Arduino.
    Deze functie blokkeert de uitvoering tot het signaal is ontvangen.
    """
    logging.info(f"Wachten op 'KLAAR' signaal van Arduino op pin {pin}...")
    while True:
        state = lgpio.gpio_read(h, pin)
        if state == 1: # HIGH signaal ontvangen
            logging.info("...Signaal 'KLAAR' ontvangen! Programma wordt hervat.")
            return # Verlaat de functie en ga door met de rest van het programma
        time.sleep(0.1) # Wacht 100ms om de CPU niet te overbelasten

def draai_stappenmotor(h):
    """Draait de stappenmotor en beheert Arduino signaal tijdens de draai."""
    logging.info("--- Starten van stappenmotor-subroutine ---")
    try:
        stuur_arduino_signaal(h, SIGNAAL_PIN, False) # Pauzeer Arduino
        lgpio.gpio_claim_output(h, DIR_PIN)
        lgpio.gpio_claim_output(h, STEP_PIN)

        logging.info("Stappenmotor draait 180 graden...")
        lgpio.gpio_write(h, DIR_PIN, 0)
        for _ in range(STAPPEN_VOOR_180_GRADEN):
            lgpio.gpio_write(h, STEP_PIN, 1); time.sleep(VERTRAGING / 2)
            lgpio.gpio_write(h, STEP_PIN, 0); time.sleep(VERTRAGING / 2)
        logging.info("Stappenmotor heeft gedraaid.")

    finally:
        stuur_arduino_signaal(h, SIGNAAL_PIN, False) # Hervat Arduino
        logging.info("--- Einde van stappenmotor-subroutine ---")

def main():
    logging.info("Mode 2 Gecombineerd Programma Gestart.")
    rtde_c = None
    rtde_r = None
    rtde_io_inst = None
    h = None # GPIO handle

    try:
        # --- Initialisatie ---
        logging.info("Initialiseren van verbindingen en GPIO...")
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        rtde_io_inst = rtde_io.RTDEIOInterface(ROBOT_IP)
        h = lgpio.gpiochip_open(GPIO_CHIP)
        lgpio.gpio_claim_output(h, SIGNAAL_PIN)
        lgpio.gpio_claim_input(h, RECEIVE_PIN)
        logging.info("Verbindingen en GPIO geïnitialiseerd.")
        """       
        # --- Hoofd Cyclus ---
        # 1. Pak het lege rek op
        #stuur_arduino_signaal(h, SIGNAAL_PIN, False)#arduino mag door
        rtde_c.setPayload(*payloads['p_50'])
        rtde_c.moveJ(rtde_c.getInverseKinematics(Approach_Big_rek))
        rtde_c.moveJ(rtde_c.getInverseKinematics(B_1_1))
        rtde_c.moveJ(rtde_c.getInverseKinematics(B_1_2))
        time.sleep(20)  # Wacht even om de robot tijd te geven om te stabiliseren
        rtde_c.moveJ(rtde_c.getInverseKinematics(B_1_3))
        rtde_c.setPayload(*payloads['leeg'])
        rtde_c.moveJ(rtde_c.getInverseKinematics(B_1_4))
        rtde_io_inst.setStandardDigitalOut(1, False) 
        rtde_c.moveJ(rtde_c.getInverseKinematics(B_1_1))

        
        """
        rtde_c.setPayload(*payloads['leeg'])
        rtde_c.moveJ(rtde_c.getInverseKinematics(startpos))
        rtde_c.moveJ(rtde_c.getInverseKinematics(oppakpos))
        rtde_io_inst.setStandardDigitalOut(1, True)
        time.sleep(1)
        rtde_c.moveJ(rtde_c.getInverseKinematics(oppakhoogte))
        rtde_c.setPayload(*payloads['rek'])
        rtde_c.moveJ(rtde_c.getInverseKinematics(opgepakt))
        rtde_c.moveJ(rtde_c.getInverseKinematics(approach))
        logging.info("Leeg rek opgepakt.")
        
        # 2. Vul het rek, rij voor rij
        for i in range(5):
            rij_nummer = i + 1
            logging.info(f"--- Starten met rij {rij_nummer} ---")
            pos = piston_posities[i]
            # Beweeg naar de startpositie van de rij
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['a']))
            # Wacht oneindig op signaal dat de rij klaar is
            wacht_op_arduino(h, RECEIVE_PIN)
            # Beweeg naar de oppakpositie
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['b']))
            # Update payload na het oppakken
            rtde_c.setPayload(*payloads[payload_keys[i]])
            # Beweeg omhoog
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['c']))
            # Beweeg terug naar de start
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['d']))
            stuur_arduino_signaal(h, SIGNAAL_PIN, True) # arduino stopt
            time.sleep(1)  # Wacht even om de Arduino tijd te geven om te stoppen
            stuur_arduino_signaal(h, SIGNAAL_PIN, False) # arduino mag door

            logging.info(f"Rij {rij_nummer} met pistons opgepakt.")
        
        logging.info("Alle 5 rijen zijn gevuld. Rek is vol.")
        # Ga terug naar een veilige positie voor de draai, bijvoorbeeld de startpositie van de laatste rij
        rtde_c.moveJ(rtde_c.getInverseKinematics(approach))
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_1))
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_2))
        rtde_c.setPayload(*payloads['leeg'])  # Zorg dat de payload correct is ingesteld voor de draai
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_3))
        rtde_io_inst.setStandardDigitalOut(1, False)  # Zet de digitale output uit
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_4))
        draai_stappenmotor(h)
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_5))
        rtde_io_inst.setStandardDigitalOut(1, True)  # Zet de digitale output uit
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_6))
        rtde_c.setPayload(*payloads['rek'])  # Zorg dat de payload correct is ingesteld voor de draai
        rtde_c.moveJ(rtde_c.getInverseKinematics(Turn_7))
        rtde_c.moveJ(rtde_c.getInverseKinematics(approach))

        for i in range(5):
            rij_nummer_terug = i + 1
            pos = piston_posities_terug[i]
            # Beweeg naar de startpositie van de rij
            logging.info(f"--- Starten met rij {rij_nummer_terug} ---")
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['a']))
            # Wacht oneindig op signaal dat de rij klaar is
            wacht_op_arduino(h, RECEIVE_PIN)
            # Beweeg naar de oppakpositie
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['b']))
            # Update payload na het oppakken
            rtde_c.setPayload(*payloads[payload_keys_terug[i]])
            # Beweeg omhoog
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['c']))
            # Beweeg terug naar de start
            rtde_c.moveJ(rtde_c.getInverseKinematics(pos['d']))
            stuur_arduino_signaal(h, SIGNAAL_PIN, True) # arduino stopt
            time.sleep(1)  # Wacht even om de Arduino tijd te geven om te stoppen
            stuur_arduino_signaal(h, SIGNAAL_PIN, False) # arduino mag door
            
            # Een korte pauze kan nog steeds nuttig zijn, afhankelijk van het proces
            time.sleep(1)
        rtde_c.moveJ(rtde_c.getInverseKinematics(approach))

        
        

    except Exception as e:
        logging.error(f"Fout in de hoofdroutine van Mode 2: {e}", exc_info=True)
        if h: stuur_arduino_signaal(h, SIGNAAL_PIN, False) # Stuur stopsignaal bij fout
        
    finally:
        logging.info("Opruimen van verbindingen...")
        if rtde_c and rtde_c.isConnected(): rtde_c.stopScript(); rtde_c.disconnect()
        if rtde_r and rtde_r.isConnected(): rtde_r.disconnect()
        if rtde_io_inst: rtde_io_inst.disconnect()
        if h: lgpio.gpiochip_close(h)
        logging.info("Alle verbindingen en GPIO zijn vrijgegeven.")

if __name__ == "__main__":
    main()
