from math import ceil
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"efficiency_bonus": 100}  # Standard: 100% (kein Bonus)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# Gebäude 1x1 (2S) mit Fertigungsalange
# Silizium: 16 Sekunden

# Gebäude 1x1 (1M) mit Fertigungsanlage
# Silizium: 16 Sekunden

# Gebäude 2x1 (2S1M) - 150% Effi - mit Fertigungsanlage
# Silizium: 10 Sekunden

# Gebäude 2x1 (1M) - 200% Effi - mit Fertigungsanlage
# Silizium: 6 Sekunden

recipes = {
    "Optisches Kabel": {
        "inputs": {"Raffinierter Kristall": 2, "Kabel": 2},
        "outputs": 1,
        "duration": 30,
        "building": "Raffinerie"
    },
    "Kabel": {
        "inputs": {"Draht": 1, "Silizium": 1, "Kristallbrocken": 2},
        "outputs": 1,
        "duration": 20,
        "building": "Raffinerie"
    },
    "Draht": {
        "inputs": {"Quarzsand": 1, "Metallplatte": 1},
        "outputs": 1,
        "duration": 16,
        "building": "Fertigungsanlage"
    },
    "Raffinierter Kristall": {
        "inputs": {"Energetisierte Platte": 1, "Kristallpulver": 1},
        "outputs": 1,
        "duration": 40,
        "building": "Raffinerie"
    },
    "Energetisierte Platte": {
        "inputs": {"Verstärkte Platte": 2, "Kristallbrocken": 2},
        "outputs": 1,
        "duration": 20,
        "building": "Montageanlage"
    },
    "Silizium": {
        "inputs": {"Quarzsand": 2},
        "outputs": 1,
        "duration": 16,
        "building": "Fertigungsanlage"
    },
    "Verstärkte Platte": {
        "inputs": {"Metallbarren": 2, "Metallplatte": 1},
        "outputs": 1,
        "duration": 12,
        "building": "Montageanlage"
    },
    "Leiterplatte": {
        "inputs": {"Metallplatte": 3, "Kristallbrocken": 5},
        "outputs": 1,
        "duration": 12,
        "building": "Montageanlage"
    },
    "Metallplatte": {
        "inputs": {"Metallbarren": 1},
        "outputs": 1,
        "duration": 6,
        "building": "Fertigungsanlage"
    },
    "Fundamentplatte": {
        "inputs": {"Metallbarren": 1},
        "outputs": 5,
        "duration": 1,
        "building": "Fertigungsanlage"
    },
    "Metallbarren": {
        "inputs": {"Metallerz": 1},
        "outputs": 1,
        "duration": 4,
        "building": "Fertigungsanlage"
    },
    "Kristallpulver": {
        "inputs": {"Quarzsand": 1, "Kristallbrocken": 3},
        "outputs": 1,
        "duration": 12,
        "building": "Raffinerie"
    },
    "Quarzsand": {
        "inputs": {},
        "outputs": 1,
        "duration": 3,
        "building": "Bergbau-Laser"
    },
    "Kristallbrocken": {
        "inputs": {},
        "outputs": 1,
        "duration": 1,
        "building": "Bergbau-Laser"
    },
    "Metallerz": {
        "inputs": {},
        "outputs": 1,
        "duration": 1,
        "building": "Bergbau-Laser"
    }
}


def calculate_requirements(product, rate_per_minute, recipes, config):
    requirements = {}
    buildings_needed = {}

    def helper(item, rate):
        if item not in recipes:
            print(f"[WARNUNG] Kein Rezept für '{item}' gefunden.")
            return

        recipe = recipes[item]
        effektive_dauer = recipe["duration"] / (config["efficiency_bonus"] / 100)
        output_per_minute = (60 / effektive_dauer) * recipe["outputs"]
        multiplier = rate / output_per_minute

        building = recipe.get("building")
        if building:
            if item in buildings_needed:
                buildings_needed[item]["count"] += ceil(rate / output_per_minute)
            else:
                buildings_needed[item] = {
                    "building": building,
                    "count": ceil(rate / output_per_minute)
                }

        for input_item, qty in recipe["inputs"].items():
            total_qty = qty * multiplier
            requirements[input_item] = requirements.get(input_item, 0) + total_qty
            helper(input_item, total_qty)

    helper(product, rate_per_minute)
    return requirements, buildings_needed


def display_chain(product, rate, recipes, config, indent=""):
    recipe = recipes.get(product)
    if not recipe:
        print(f"{indent}[?] Kein Rezept für {product}")
        return

    # ==========
    effektive_dauer = recipe["duration"] / (config["efficiency_bonus"] / 100)
    output_rate = (60 / effektive_dauer) * recipe["outputs"]
    # ==========
    needed_buildings = ceil(rate / output_rate)
    building = recipe.get("building", "Unbekannt")

    print(f"{indent}{product}: {rate:.2f}/min → {needed_buildings} x {building}")

    for input_item, qty in recipe["inputs"].items():
        input_rate = qty * (rate / recipe["outputs"])
        display_chain(input_item, input_rate, recipes, config, indent + "    ")


def main():
    print("=== Desynced Produktionsketten-Rechner ===")

    # ============================================
    config = load_config()
    print(f"\nAktueller Effizienzbonus: {config['efficiency_bonus']}%")
    new_val = input("Neuen Bonus eingeben (Enter zum Beibehalten): ").strip()
    if new_val:
        try:
            entered = int(new_val)
            if entered <= 0:
                print("Effizienzbonus 0% ist nicht erlaubt. Es wird stattdessen mit 100% gerechnet (Standard ohne Module).")
                config["efficiency_bonus"] = 100
            else:
                config["efficiency_bonus"] = entered
            save_config(config)
        except ValueError:
            print("Ungültiger Wert, bisheriger Bonus wird beibehalten.")
    # ============================================

    print("Verfügbare Produkte:")
    for product in recipes:
        print(f"- {product}")

    product = input("Welches Produkt möchtest du herstellen? ").strip()
    if product not in recipes:
        print("Produkt nicht gefunden.")
        return

    try:
        rate = float(input("Wie viele Einheiten pro Minute? "))
    except ValueError:
        print("Bitte eine gültige Zahl eingeben.")
        return

    result, buildings = calculate_requirements(product, rate, recipes, config)

    print(f"\n🛠 Ressourcenbedarf für {rate:.2f} x {product} pro Minute:")
    for item, amount in result.items():
        print(f" - {item}: {amount:.2f} / Minute")

    print(f"\n🏗 Benötigte Produktionsgebäude (summiert):")
    for item, data in buildings.items():
        print(f" - {item}: {data['count']} x {data['building']}")

    print(f"\n🔍 Detaillierte Produktionskette:")
    display_chain(product, rate, recipes, config)


if __name__ == "__main__":
    main()
