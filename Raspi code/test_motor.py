# test_motor.py
import lgpio
import time
import sys

# --- Instellingen ---
STEP_PIN = 17
DIR_PIN = 27
STAPPEN_VOOR_180_GRADEN = 1600
PAUZE_TIJD = 2.0
VERTRAGING = 0.005
GPIO_CHIP = 0

def draai_schijf(h, richting):
    """Draait de schijf 180 graden."""
    lgpio.gpio_write(h, DIR_PIN, richting)
    for i in range(STAPPEN_VOOR_180_GRADEN):
        lgpio.gpio_write(h, STEP_PIN, 1) # HIGH
        time.sleep(VERTRAGING / 2)
        lgpio.gpio_write(h, STEP_PIN, 0) # LOW
        time.sleep(VERTRAGING / 2)
        # Print af en toe een punt om te zien dat de lus draait
        if i % 400 == 0:
            print(".", end="", flush=True)

def main():
    # flush=True zorgt ervoor dat de output direct zichtbaar is
    print("--- TEST MOTOR SCRIPT GESTART ---", flush=True)
    h = None
    try:
        print(f"Poging om gpiochip {GPIO_CHIP} te openen...", flush=True)
        h = lgpio.gpiochip_open(GPIO_CHIP)
        print("...gpiochip succesvol geopend.", flush=True)

        print("Poging pinnen te claimen...", flush=True)
        lgpio.gpio_claim_output(h, DIR_PIN)
        lgpio.gpio_claim_output(h, STEP_PIN)
        print("...pinnen succesvol geclaimd.", flush=True)

        print("\nStart met draaien (180 graden)...", flush=True)
        draai_schijf(h, 0)
        print("\n...Draaien voltooid.", flush=True)

        print(f"Pauze van {PAUZE_TIJD} seconden.", flush=True)
        time.sleep(PAUZE_TIJD)

        print("Start met terugdraaien (180 graden)...", flush=True)
        draai_schijf(h, 1)
        print("\n...Terugdraaien voltooid.", flush=True)

    except Exception as e:
        # Stuur fouten naar stderr
        print(f"\n!!! FATALE FOUT IN TEST_MOTOR: {e}", file=sys.stderr, flush=True)

    finally:
        if h:
            lgpio.gpiochip_close(h)
            print("GPIO handle vrijgegeven.", flush=True)
        print("--- TEST MOTOR SCRIPT BEËINDIGD ---", flush=True)

if __name__ == "__main__":
    main()