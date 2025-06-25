from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import logging
from logging.handlers import RotatingFileHandler
import os
import subprocess
import sys
import time

# Probeer robot-specifieke bibliotheken te importeren
try:
    import rtde_io
    import rtde_receive
    RTDE_AVAILABLE = True
except ImportError:
    RTDE_AVAILABLE = False

# --- NIEUW: GESPLITSTE CONFIGURATIE VOOR MOCK MODES ---
# Zet op True om de UR Robot (I/O, Mode 1 & 2) te simuleren.
MOCK_UR_ROBOT = False

# Zet op True om de Stappenmotor (Mode 3) te simuleren.
MOCK_STEPPER_MOTOR = False


# --- Logger Configuratie (ongewijzigd) ---
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ROBOT_ERROR_LOG_FILENAME = 'robot_errors.log'
robot_error_logger = logging.getLogger('robot')
robot_error_logger.setLevel(logging.INFO)
robot_error_logger.propagate = False
robot_error_file_handler = RotatingFileHandler(ROBOT_ERROR_LOG_FILENAME, maxBytes=1024*1024*2, backupCount=2, encoding='utf-8')
robot_error_file_handler.setFormatter(formatter)
robot_error_logger.addHandler(robot_error_file_handler)

# --- App Configuratie (ongewijzigd) ---
CORRECT_PASSWORD = "pi"
ROBOT_IP = "192.168.0.43"
app = Flask(__name__)
app.secret_key = os.urandom(24)
PYTHON_EXECUTABLE = sys.executable 
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Login en Authenticatie Routes (ongewijzigd) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == CORRECT_PASSWORD:
            session['authenticated'] = True
            robot_error_logger.info("Gebruiker succesvol ingelogd.")
            return redirect(url_for('serve_index_page'))
        else:
            robot_error_logger.warning("Mislukte loginpoging.")
            return render_template('login.html', error='Ongeldig wachtwoord')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# --- Hoofdpagina (geeft nu beide mock-vlaggen door) ---
@app.route('/')
def serve_index_page():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('index.html', mock_ur_robot=MOCK_UR_ROBOT, mock_stepper_motor=MOCK_STEPPER_MOTOR)

# --- API Routes (Aangepast voor gesplitste mocks) ---

@app.route('/api/digital_output/state', methods=['GET'])
def get_digital_output_state():
    if not session.get('authenticated'): return jsonify({'message': 'Authenticatie vereist'}), 401
    if MOCK_UR_ROBOT or not RTDE_AVAILABLE:
        return jsonify({'status': 'success', 'outputs': 0})
    rtde_r = None
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        return jsonify({'status': 'success', 'outputs': rtde_r.getActualDigitalOutputBits()})
    except Exception as e:
        robot_error_logger.error(f"Fout bij ophalen DO state: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if rtde_r and rtde_r.isConnected(): rtde_r.disconnect()

@app.route('/api/digital_output/set', methods=['POST'])
def set_digital_output():
    if not session.get('authenticated'): return jsonify({'message': 'Authenticatie vereist'}), 401
    data = request.get_json()
    pin, state = data.get('pin'), data.get('state')
    if pin is None or state is None: return jsonify({'status': 'error', 'message': 'Ongeldige input.'}), 400
    
    if MOCK_UR_ROBOT or not RTDE_AVAILABLE:
        message = f"MOCK MODE: Digital Output {pin} naar {'AAN' if state else 'UIT'} gezet."
        robot_error_logger.info(message)
        return jsonify({'status': 'success', 'message': message})

    rtde_io_inst = None
    try:
        rtde_io_inst = rtde_io.RTDEIOInterface(ROBOT_IP)
        rtde_io_inst.setStandardDigitalOut(pin, state)
        message = f"Digital Output {pin} naar {'AAN' if state else 'UIT'} gezet."
        robot_error_logger.info(message)
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        robot_error_logger.error(f"Fout bij zetten DO{pin} naar {state}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if rtde_io_inst: rtde_io_inst.disconnect()

@app.route('/api/run_mode', methods=['POST'])
def run_mode_endpoint():
    if not session.get('authenticated'): return jsonify({'message': 'Authenticatie vereist'}), 401
    data = request.get_json()
    mode = data.get('mode')
    if not mode: return jsonify({'message': 'Geen modus gespecificeerd'}), 400

    # Bepaal of de specifieke modus gemocked moet worden
    is_mocked = {
        'mode1': MOCK_UR_ROBOT,
        'mode2': MOCK_UR_ROBOT,
        'mode3': MOCK_STEPPER_MOTOR
    }.get(mode, False) # Geeft False terug als de modus niet in de dict staat

    if is_mocked:
        message = f"MOCK MODE: {mode.replace('_', ' ').capitalize()} is 'gestart'."
        robot_error_logger.info(message)
        return jsonify({'message': message, 'status': 'success'})

    # Als de modus niet gemocked is, voer het script uit
    mode_scripts = {'mode1': 'mode1_program.py', 'mode2': 'mode2_program.py', 'mode3': 'mode3_program.py'}
    script_to_run = mode_scripts.get(mode)
    if not script_to_run:
        robot_error_logger.error(f"Onbekende modus '{mode}' aangevraagd.")
        return jsonify({'message': f'Onbekende modus: {mode}'}), 404
        
    script_path = os.path.join(APP_DIR, script_to_run)
    if not os.path.exists(script_path):
        robot_error_logger.error(f"Scriptbestand niet gevonden voor {mode}: {script_path}")
        return jsonify({'message': f'Scriptbestand niet gevonden voor {mode}'}), 500

    try:
        command = f'"{PYTHON_EXECUTABLE}" "{script_path}"'
        robot_error_logger.info(f"Starten van {mode} via shell commando: {command}")
        log_file = open(ROBOT_ERROR_LOG_FILENAME, 'a', encoding='utf-8')
        log_file.write(f"\n--- Output van {script_to_run} @ {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        process = subprocess.Popen(command, shell=True, stdout=log_file, stderr=log_file, cwd=APP_DIR)
        
        message = f"{mode.replace('_', ' ').capitalize()} is gestart. Zie logs voor de voortgang."
        return jsonify({'message': message, 'status': 'success'})
    except Exception as e:
        robot_error_logger.error(f"Fout bij het aanroepen van subprocess voor {mode}: {e}", exc_info=True)
        return jsonify({'message': f'Fout bij het starten van {mode}'}), 500

# --- Route voor Logpagina (ongewijzigd) ---
@app.route('/logs')
def show_logs_page():
    if not session.get('authenticated'): return redirect(url_for('login'))
    log_content = f"Logbestand '{ROBOT_ERROR_LOG_FILENAME}' is nog leeg of kon niet worden gelezen."
    try:
        if os.path.exists(ROBOT_ERROR_LOG_FILENAME):
            with open(ROBOT_ERROR_LOG_FILENAME, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            recent_lines = log_lines[-200:]
            log_content = "".join(reversed(recent_lines))
            if not log_content.strip(): log_content = f"Logbestand '{ROBOT_ERROR_LOG_FILENAME}' bevat geen zichtbare inhoud."
        else: log_content = f"Logbestand '{ROBOT_ERROR_LOG_FILENAME}' niet gevonden."
    except Exception as e: log_content = f"Fout bij het lezen van het logbestand: {str(e)}"
    return render_template('logs.html', log_content=log_content)

if __name__ == '__main__':
    robot_error_logger.info(f"Flask server gestart. MOCK_UR_ROBOT={MOCK_UR_ROBOT}, MOCK_STEPPER_MOTOR={MOCK_STEPPER_MOTOR}")
    app.run(host='0.0.0.0', port=5000, debug=False)