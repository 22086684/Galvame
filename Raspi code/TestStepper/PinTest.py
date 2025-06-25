import RPi.GPIO as GPIO
import time

# --- Instellingen ---
TEST_PIN = 17  # De GPIO pin die we gaan testen.

# --- GPIO Setup ---
GPIO.setwarnings(False) # Schakelt waarschuwingen uit
GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_PIN, GPIO.OUT)

print(f"GPIO pin {TEST_PIN} wordt nu op HIGH (3.3V) gezet.")
print("Je kunt nu de spanning meten.")
print("Druk op Ctrl+C om het programma te stoppen.")

try:
    # Zet de pin constant op HIGH
    GPIO.output(TEST_PIN, GPIO.HIGH)
    
    # Houd de pin hoog totdat het programma wordt gestopt
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgramma gestopt door gebruiker.")

finally:
    # GPIO pinnen netjes vrijgeven
    GPIO.cleanup()
    print("GPIO is opgeruimd.")