import time
import board
import digitalio
import neopixel
from adafruit_funhouse import FunHouse

funhouse = FunHouse(default_bg=0x000F20, scale=3)

running_state       = False
tripped_led_color   = [0xFF, 0xE5, 0x99]
reset_led_color     = [0x00, 0x00, 0x00]
text_color          = [0x60, 0x60, 0x60]

current_led_color   = [0x00, 0x00, 0x00] # is constantly being modified towards reset/tripped colors

transition_dimming_time = 0.007 # in seconds
transition_shining_time = 0.005 # in seconds
stayOnTime = 0 # Global Variable: How long the lights stay up for in seconds

# NeoPixel Strip
pixel_pin = board.A0
pir_sensor_pin = board.A2
num_pixels = 30

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False)
pir_sensor = digitalio.DigitalInOut(pir_sensor_pin)
pir_sensor.direction = digitalio.Direction.INPUT

running_label = funhouse.add_text(
    text="paused",
    text_position=(2, 4),
    text_color=text_color
)

def calculateColorDistance(currentColor, targetColor):
    distance = [0, 0, 0]

    for i in range(len(currentColor)):
        distance[i] = abs(currentColor[i] - targetColor[i])
    
    return distance

def transitionColor(currentColor, targetColor, distance):
    for i in range(len(distance)):
        if (currentColor[i] == targetColor[i]):
            pass
        elif (currentColor[i] > targetColor[i]):
            currentColor[i] = (currentColor[i] - 1)
        else:
            currentColor[i] = (currentColor[i] + 1)
    
    return currentColor

def turnLightsToColor(led_colors):
    pixels.fill(led_colors)
    pixels.show()

turnLightsToColor(reset_led_color)

while True:
    if funhouse.peripherals.button_down:
        if running_state is False:
            running_state = True
            funhouse.set_text('preparing...count to 3', running_label)
            time.sleep(3) # enough time to get out of the way
            funhouse.set_text('sensing...', running_label)
        else:
            running_state = False
            funhouse.set_text('paused', running_label)
            time.sleep(0.5)

    if running_state is True:
        if funhouse.peripherals.pir_sensor or pir_sensor.value:
            tripped_text = "entrance" if pir_sensor.value else "hallway"
            funhouse.set_text(tripped_text, running_label)
            stayOnTime = time.monotonic() + 30 # in seconds

            while stayOnTime > time.monotonic():
                if funhouse.peripherals.button_down: # Manual Override - stop the entire process
                    stayOnTime = 0
                    running_state = False
                    funhouse.set_text('manually paused', running_label)

                    turnLightsToColor(reset_led_color)
                    time.sleep(0.5)
                else:
                    if current_led_color is not tripped_led_color:
                        current_led_color = transitionColor(
                            current_led_color,
                            tripped_led_color,
                            calculateColorDistance(current_led_color, tripped_led_color)
                        )

                        turnLightsToColor(current_led_color)
                        time.sleep(transition_shining_time)

        elif not funhouse.peripherals.pir_sensor or not pir_sensor.value:
            funhouse.set_text('sensing...', running_label)
            if current_led_color is not reset_led_color:
                current_led_color = transitionColor(
                    current_led_color,
                    reset_led_color,
                    calculateColorDistance(current_led_color, reset_led_color)
                )

                turnLightsToColor(current_led_color)
                time.sleep(transition_dimming_time)