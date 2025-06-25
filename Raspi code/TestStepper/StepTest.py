import RPi.GPIO as GPIO
import time

# Definieer de GPIO pinnen
STEP_PIN = 17  # Pin voor de stappen (PUL+)
DIR_PIN = 27   # Pin voor de richting (DIR+)

# Instellingen  
stappen_voor_180_graden = 1600
pauze_tijd = 2.0  # Wachttijd in seconden
vertraging = 0.005  # Bepaalt de snelheid, kleiner is sneller

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

def draai_schijf(richting):
    """
    Draait de schijf 180 graden in de opgegeven richting.sudo apt update
    Richting: 0 voor met de klok mee, 1 voor tegen de klok in.
    """
    # Stel de draairichting in
    GPIO.output(DIR_PIN, richting)

    # Genereer de pulsen om de motor te laten stappen
    for _ in range(stappen_voor_180_graden):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(vertraging / 2)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(vertraging / 2)

try:
    print("Programma gestart. Druk op Ctrl+C om te stoppen.")
    # Oneindige lus om continu heen en weer te draaien
    while True:
        # Draai 180 graden met de klok mee
        print("Draai 180 graden...")
        draai_schijf(0) # 0 = richting 1

        # Wacht 2 seconden
        print(f"Pauze van {pauze_tijd} seconden.")
        time.sleep(pauze_tijd)

        # Draai 180 graden terug
        print("Draai 180 graden terug...")
        draai_schijf(1) # 1 = richting 2

        # Wacht 2 seconden voor de cyclus opnieuw begint
        print(f"Pauze van {pauze_tijd} seconden.")
        time.sleep(pauze_tijd)


except KeyboardInterrupt:
    print("\nProgramma gestopt door gebruiker.")

finally:
    # GPIO pinnen netjes vrijgeven
    GPIO.cleanup()
    print("GPIO pinnen zijn vrijgegeven.")