'''
Mobility Launcher
This script serves as a main entry point for launching the gps logger
when using the adafruit tft display and buttons for user interaction.
Button functions:
    - Start GPS logging
    - Stop and save gps log to csv
'''

import RPi.GPIO as GPIO
from gps_with_kalman import GpsKalman
from tft_update_information import TFT_Updater
import threading
import time

# Init Adafruit 2.8" resistive TFT+ buttons
BUTTONS = [17,22,23,27]
GPIO.setmode(GPIO.BCM)
for pin in BUTTONS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# presets for kalman filter init
stationary_preset = {
    "sigma_gps": 5.0,
    "sigma_accel": 0.05,
    "initial_velocity_std": 0.5
}

walking_preset_1 = {
    "sigma_gps": 5.0,
    "sigma_accel": 0.5,
    "initial_velocity_std": 1.0
}

walking_preset_2 = {
    "sigma_gps": 6.0,
    "sigma_accel": 0.4,
    "initial_velocity_std": 1.0
}

driving_preset_1 = {
    "sigma_gps": 5.0,
    "sigma_accel": 2.0,
    "initial_velocity_std": 10.0
}

# state machine to manage screen output, button input and gps logging/saving
def main():
    tft_updater = None
    gps_kalman = None
    gps_preset = None

    try:
        state = 'IDLE'
        screen_state = 'INIT'
        prev_screen_state = None

        while True:

            if state == 'IDLE': # wait for button press
                if GPIO.input(BUTTONS[0]) == GPIO.LOW:  # Button 1 pressed
                    state = 'INIT_GPS'
                    gps_preset = stationary_preset
                elif GPIO.input(BUTTONS[1]) == GPIO.LOW:  # Button 2 pressed
                    state = 'INIT_GPS'
                    gps_preset = walking_preset_1
                elif GPIO.input(BUTTONS[2]) == GPIO.LOW:  # Button 3 pressed
                    state = 'INIT_GPS'
                    gps_preset = walking_preset_2
                elif GPIO.input(BUTTONS[3]) == GPIO.LOW:  # Button 4 pressed
                    state = 'INIT_GPS'
                    gps_preset = driving_preset_1

            elif state == 'INIT_GPS':
                gps_kalman = GpsKalman(**gps_preset)
                state = 'RUN'
                screen_state = 'GPS_LOGGING'

            elif state == 'RUN': # wait for button press
                if GPIO.input(BUTTONS[0]) == GPIO.LOW:  # Button 1 pressed
                    state = 'STOP_AND_SAVE'

            elif state == 'STOP_AND_SAVE':
                gps_kalman.stop()
                gps_kalman.save_gps_data_to_csv()
                gps_kalman = None
                gps_preset = None
                state = 'IDLE'
                screen_state = 'MAIN_MENU'

            # update screen if screen_state has changed
            if screen_state != prev_screen_state:
                prev_screen_state = screen_state

                if screen_state == 'INIT':
                    tft_updater = TFT_Updater()
                    tft_updater.open_fb()
                    screen_state = 'MAIN_MENU'

                elif screen_state == 'MAIN_MENU':
                    tft_updater.init_image()
                    tft_updater.draw_text('<- Stationary Preset', (5, 10), text_size=20)
                    tft_updater.draw_text('<- Walking Preset 1', (5, 60), text_size=20)
                    tft_updater.draw_text('<- Walking Preset 2', (5, 110), text_size=20)
                    tft_updater.draw_text('<- Driving Preset 1', (5, 160), text_size=20)
                    tft_updater.update()

                elif screen_state == 'GPS_LOGGING':
                    if gps_kalman:
                        if gps_kalman.gps_data_records:
                            latest_record = gps_kalman.gps_data_records[-1]

                    tft_updater.init_image()
                    tft_updater.draw_text('GPS Logging...', (10, 50), text_size=20)
                    tft_updater.draw_text(f'Preset: {gps_preset}', (10, 100), text_size=15)
                    tft_updater.draw_text('Press Button 1 to Stop and Save', (10, 150), text_size=15)
                    
                    tft_updater.update()

                # small time delay to prevent saturating the screen spi buffer
                time.sleep(0.1)

    except KeyboardInterrupt as e:
        print(f"Exception: {e}")
    finally:
        print("Exiting")
        GPIO.cleanup()

if __name__ == '__main__':
    main()