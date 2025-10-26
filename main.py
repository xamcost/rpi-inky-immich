import os
from io import BytesIO
from random import choice

import requests
import RPi.GPIO as GPIO
from inky.auto import auto
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

# import gpiod
# import gpiodevice
# from gpiod.line import Bias, Direction, Edge


IMMICH_URL = os.getenv("IMMICH_URL")
IMMICH_API_KEY = os.getenv("IMMICH_API_KEY")

RANDOM_IMAGES = []

PERSON_NAMES = ["Sophie"]
_PERSON_NAMES = PERSON_NAMES.copy()

INKY = auto(ask_user=True, verbose=True)

# Code below until request instantiation is from:
# https://github.com/pimoroni/inky/blob/main/examples/7color/buttons.py
# Raspberry Pi 5 Header pins used by Inky Impression:
#    PIN29, PIN31, PIN36, PIN18.
# These header pins correspond to BCM GPIO numbers:
#    GPIO05, GPIO06, GPIO16, GPIO24.
# These GPIO numbers are what is used below and not the
# header pin numbers.
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, C and D respectively
LABELS = ["A", "B", "C", "D"]

# Create settings for all the input pins, we want them to be inputs
# with a pull-up and a falling edge detection.
# INPUT = gpiod.LineSettings(
#     direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING
# )

# Find the gpiochip device we need, we'll use
# gpiodevice for this, since it knows the right device
# for its supported platforms.
# chip = gpiodevice.find_chip_by_platform()

# Build our config for each pin/line we want to use
# OFFSETS = [chip.line_offset_from_id(id) for id in BUTTONS]
# line_config = dict.fromkeys(OFFSETS, INPUT)

# Request the lines, *whew*
# request = chip.request_lines(consumer="inky7-buttons", config=line_config)

# Alternative implementation using RPi.GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def _get_person_ids(names: list[str]) -> list[str]:
    headers = {"x-api-key": IMMICH_API_KEY}
    response = requests.get(f"{IMMICH_URL}/api/people", headers=headers)
    response.raise_for_status()
    people = response.json()["people"]

    person_ids = []
    for person in people:
        if person["name"] in names:
            person_ids.append(person["id"])

    return person_ids


def _refresh_image_list():
    headers = {"x-api-key": IMMICH_API_KEY}

    person_ids = _get_person_ids(_PERSON_NAMES)
    body = {"type": "IMAGE"}
    if person_ids:
        body.update({"personIds": person_ids})

    print(f"Fetching images for persons {_PERSON_NAMES} with IDs {person_ids}")
    response = requests.post(
        f"{IMMICH_URL}/api/search/random", headers=headers, json=body
    )
    response.raise_for_status()

    RANDOM_IMAGES.clear()
    RANDOM_IMAGES.extend(response.json())


def _fetch_image(id: str, size: tuple[int, int]) -> bytes:
    headers = {"x-api-key": IMMICH_API_KEY}
    response = requests.get(f"{IMMICH_URL}/api/assets/{id}/original", headers=headers)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    image = ImageOps.pad(image, size)

    return image


def _show_random_image() -> Image.Image:
    if not RANDOM_IMAGES:
        _refresh_image_list()

    selected_image = choice(RANDOM_IMAGES)
    RANDOM_IMAGES.remove(selected_image)

    image_data = _fetch_image(selected_image["id"], (INKY.width, INKY.height))
    print(f"Fetched image ID: {selected_image['id']}, Size: {image_data.size}")

    INKY.set_image(image_data)
    INKY.show()


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated gpiod event object.
def _handle_button(event):
    # index = OFFSETS.index(event.line_offset)
    index = event  # Using RPi.GPIO, event is just the GPIO number
    gpio_number = BUTTONS[index]
    label = LABELS[index]
    print(f"Button press detected on GPIO #{gpio_number} label: {label}")

    if label == "A":
        print("Loading next image")
        _show_random_image()
    elif label == "B":
        if _PERSON_NAMES:
            _PERSON_NAMES.clear()
            print("Removed person id search filter")
        else:
            _PERSON_NAMES.extend(PERSON_NAMES)
            print(f"Added person id search filter for persons: {_PERSON_NAMES}")
        _refresh_image_list()
        _show_random_image()
    elif label == "C":
        print("Not implemented yet: C button pressed")
    elif label == "D":
        print("Switching off Raspberry Pi")
        os.system("sudo shutdown -h now")


def main():
    register_heif_opener()  # Enable HEIC/HEIF support in Pillow

    _refresh_image_list()

    try:
        # while True:
        #     for event in request.read_edge_events():
        #         _handle_button(event)
        while True:
            for i, button in enumerate(BUTTONS):
                if GPIO.input(button) == GPIO.LOW:  # Button pressed
                    _handle_button(i)
                    while GPIO.input(button) == GPIO.LOW:
                        pass  # Wait for button release
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
