import lgpio
import time

# Initialisation
chip = lgpio.gpiochip_open(0)
gpio = 27  # GPIO9 (phys pin 21)

# Met GPIO9 en entrée avec pull-up
lgpio.gpio_claim_input(chip, gpio, lgpio.SET_PULL_UP)

print("🟢 Test du bouton sur GPIO9. Appuie dessus pour voir le changement.")
print("Appuie sur Ctrl+C pour quitter.\n")

try:
    while True:
        state = lgpio.gpio_read(chip, gpio)
        if state == 0:
            print("🔴 BOUTON APPUYÉ")
        else:
            print("⚪ Bouton relâché")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\n🛑 Fin du test.")
finally:
    lgpio.gpiochip_close(chip)
