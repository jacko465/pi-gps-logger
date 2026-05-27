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
BUTTONS = [27,23,22,17]
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
    preset_name = ""
    screen_update = False

    num_sats = 0
    link_quality = 'No Fix'
    HDOP = 'Unknown'

    try:
        state = 'IDLE'
        screen_state = 'INIT'
        prev_screen_state = None

        while True:

            if state == 'IDLE': # wait for button press
                if GPIO.input(BUTTONS[0]) == GPIO.LOW:  # Button 1 pressed
                    state = 'INIT_GPS'
                    gps_preset = stationary_preset
                    preset_name = "Stationary_Preset"
                elif GPIO.input(BUTTONS[1]) == GPIO.LOW:  # Button 2 pressed
                    state = 'INIT_GPS'
                    gps_preset = walking_preset_1
                    preset_name = "Walking_Preset_1"
                elif GPIO.input(BUTTONS[2]) == GPIO.LOW:  # Button 3 pressed
                    state = 'INIT_GPS'
                    gps_preset = walking_preset_2
                    preset_name = "Walking_Preset_2"
                elif GPIO.input(BUTTONS[3]) == GPIO.LOW:  # Button 4 pressed
                    state = 'INIT_GPS'
                    gps_preset = driving_preset_1
                    preset_name = "Driving_Preset_1"

                # run gps to show fix quality on main menu screen
                if gps_kalman is None:
                    gps_kalman = GpsKalman(**stationary_preset)
                    gps_kalman.start()
                else:
                    # update main menu screen with gps fix quality if available
                    if gps_kalman.link_quality != link_quality or gps_kalman.num_satellites != num_sats or gps_kalman.hdop != HDOP:
                        link_quality = gps_kalman.link_quality
                        num_sats = gps_kalman.num_satellites
                        HDOP = gps_kalman.hdop
                        screen_update = True

            elif state == 'INIT_GPS':
                time.sleep(0.5)   # small delay to debounce button press
                if gps_kalman:
                    gps_kalman.stop()
                    gps_kalman = None
                gps_kalman = GpsKalman(**gps_preset)
                gps_kalman.start()
                state = 'RUN'
                screen_state = 'GPS_LOGGING'

            elif state == 'RUN': # wait for button press
                if GPIO.input(BUTTONS[0]) == GPIO.LOW:  # Button 1 pressed
                    state = 'STOP_AND_SAVE'

            elif state == 'STOP_AND_SAVE':
                gps_kalman.stop()
                gps_kalman.save_gps_csv(filename=preset_name)
                gps_kalman = None
                gps_preset = None
                preset_name = ""
                state = 'IDLE'
                screen_state = 'MAIN_MENU'

            # update screen if screen_state has changed
            if (screen_state != prev_screen_state) or screen_update:
                prev_screen_state = screen_state

                if screen_state == 'INIT':
                    tft_updater = TFT_Updater()
                    tft_updater.open_fb()
                    screen_state = 'MAIN_MENU'

                elif screen_state == 'MAIN_MENU':
                    screen_update = False
                    tft_updater.init_image()
                    tft_updater.draw_text('<- Stationary Preset', (5, 0), text_size=20)
                    tft_updater.draw_text('<- Walking Preset 1', (5, 60), text_size=20)
                    tft_updater.draw_text('<- Walking Preset 2', (5, 120), text_size=20)
                    tft_updater.draw_text('<- Driving Preset 1', (5, 180), text_size=20)
                    tft_updater.draw_text(f"Link Quality: {link_quality} Sats: {num_sats} HDOP: {HDOP}", (5, 200), text_size=10)
                    tft_updater.update()

                elif screen_state == 'GPS_LOGGING':
                    screen_update = True
                    latest_record = None
                    if gps_kalman:
                        if gps_kalman.gps_data_records:
                            latest_record = gps_kalman.gps_data_records[-1]

                    tft_updater.init_image()
                    tft_updater.draw_text('<- Stop and Save', (5, 0), text_size=12)
                    tft_updater.draw_text(f'{preset_name}', (150, 0), text_size=12)
                    
                    if latest_record:
                        tft_updater.draw_text(f"Timestamp: {latest_record['timestamp']}", (5, 60), text_size=15)
                        tft_updater.draw_text(f"Raw_Lat: {latest_record['raw_latitude']:.4f}  Raw_Lon: {latest_record['raw_longitude']:.4f}", (5, 80), text_size=15)
                        tft_updater.draw_text(f"Filt_Lat: {latest_record['filtered_latitude']:.4f}  Filt_Lon: {latest_record['filtered_longitude']:.4f}", (5, 100), text_size=15)
                        tft_updater.draw_text(f"Vel_X: {latest_record['velocity_x']:.2f} m/s     Vel_Y: {latest_record['velocity_y']:.2f} m/s", (5, 120), text_size=15)
                        speed_kmh = latest_record['speed'] * 3.6
                        tft_updater.draw_text(f"Speed: {speed_kmh:.2f} km/h     {latest_record['speed']:.2f} m/s", (5, 140), text_size=15)
                        tft_updater.draw_text(f"Link Quality: {link_quality} Sats: {num_sats} HDOP: {HDOP}", (5, 160), text_size=10)
                    
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