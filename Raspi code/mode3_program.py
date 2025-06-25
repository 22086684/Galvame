import time
import logging
try:
    import lgpio
except ImportError:
    lgpio = None
    print("WAARSCHUWING: lgpio bibliotheek niet gevonden.")

# --- Instellingen ---
STEP_PIN = 17
DIR_PIN = 27
STAPPEN_VOOR_180_GRADEN = 1600
PAUZE_TIJD = 2.0
VERTRAGING = 0.004
GPIO_CHIP = 0

# --- Logging Configuratie ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - MODE 3 (GPIO) - %(message)s',
    handlers=[
        logging.FileHandler("robot_errors.log"),
    ]
)

def draai_stappenmotor():
    """
    Initialiseert de GPIO en draait de stappenmotor eenmalig 180 graden.
    Deze functie ruimt zichzelf volledig op.
    """
    logging.info("--- Starten van stappenmotor-subroutine ---")
    if not lgpio:
        logging.error("lgpio bibliotheek niet gevonden. Kan stappenmotor niet aansturen.")
        return # Stop de functie als de bibliotheek mist

    h = None # Handle voor de GPIO chip
    try:
        # GPIO Setup
        h = lgpio.gpiochip_open(GPIO_CHIP)
        lgpio.gpio_claim_output(h, DIR_PIN)
        lgpio.gpio_claim_output(h, STEP_PIN)
        logging.info("GPIO pinnen geclaimd voor stappenmotor.")

        # Draai de motor
        logging.info("Stappenmotor draait 180 graden...")
        lgpio.gpio_write(h, DIR_PIN, 0) # Zet richting (0 of 1)
        for _ in range(STAPPEN_VOOR_180_GRADEN):
            lgpio.gpio_write(h, STEP_PIN, 1) # Puls AAN
            time.sleep(VERTRAGING / 2)
            lgpio.gpio_write(h, STEP_PIN, 0) # Puls UIT
            time.sleep(VERTRAGING / 2)
        
        logging.info("Stappenmotor heeft gedraaid.")

    except Exception as e:
        logging.error(f"Fout tijdens stappenmotor-subroutine: {e}", exc_info=True)

    finally:
        # GPIO pinnen netjes vrijgeven
        if h:
            lgpio.gpiochip_close(h)
            logging.info("GPIO handle voor stappenmotor is vrijgegeven.")
        logging.info("--- Einde van stappenmotor-subroutine ---")

def main():
    h = None
    try:
        while True:
            draai_stappenmotor()
            time.sleep(0.5)  # Wacht even voor de volgende draai

    except Exception as e:
        logging.error(f"Fout in Mode 3 (lgpio): {e}", exc_info=True)
    finally:
        if h:
            lgpio.gpiochip_close(h)
            logging.info("lgpio handle vrijgegeven.")

if __name__ == "__main__":
    main()