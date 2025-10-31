# RPi Inky Immich

This project provides a simple way to display images from a remote [Immich](https://immich.app/) server on a Raspberry Pi using an [Inky](https://github.com/pimoroni/inky/tree/main) e-ink display. In its current form, the script fetches random images from the Immich server and displays them on the Inky display.

By default, it includes a filter on the persons present in the images when querying Immich. Since I have a [Inky 7 colour display with 4 buttons](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635), I included some basic button functionality to navigate through images:

- Button A: Display a new random image
- Button B: Toggle the person filter on/off
- Button C: Not used yet!
- Button D: Shutdown the Raspberry Pi

## Getting Started

### Prerequisites

You will need to ensure you have the following installed on your Raspberry Pi:

- Python 3
- Python dev headers: you can install them using `sudo apt-get install python3-dev`
- Python RPi GPIO library: install it using `sudo apt-get install python3-rpi.gpio`

Other dependencies will be installed via `pip` (see Installation section).

Moreover, you need to generate an API key from your Immich server to allow the script to access the images. You can do this by logging into your Immich web interface, navigating to your user _account settings_, and generating a new API key. It only needs the following scopes:

- asset.read
- asset.download
- person.read

I would recommend setting up a virtual environment for this project. You can do this using `venv`:

```bash
python3 -m venv inky-immich-env
source inky-immich-env/bin/activate
```

### Installation

1. Clone this repository to your Raspberry Pi:

```bash
git clone https://github.com/xamcost/rpi-inky-immich
cd rpi-inky-immich
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Export the necessary environment variables. You can do this manually, or you can copy the `example.env` file to a `.env` file and edit it accordingly. Then source the `.env` file:

```bash
cp example.env .env
vim .env
source .env
```

4. Launch the script:

```bash
python main.py
```

## Caveats

There are a few important limitations to be aware of:

- this program won't work on Raspberry Pi Zero models since it uses `pillow-heif` to decode HEIC images, which [doesn't support ARMv6 architecture](https://github.com/bigcat88/pillow_heif/issues/147#issuecomment-1739994825). If you don't have HEIC images and want to use a Pi Zero, you can perfectly remove `pillow-heif`.
- it has been tested only with Raspberry Pi Compute Module 4. It should work with any RPi 3, 4 or 5 model, but it may need some adjustments.
- it has been tested only with Inky 7 colour display with 4 buttons. Yet it uses the `auto` function from the Inky library to detect the display type, so it should work with other Inky models as well, but button functionality may vary.
