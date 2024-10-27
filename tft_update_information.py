from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import time

class TFT_Updater:
    def __init__(self, fbdev='/dev/fb1', screen_size=(320, 240)):
        self.screen_size = screen_size
        self.fbdev = fbdev
        self.font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

        self.fb = None
        self.image = None
        self.draw = None
        print('tft updater init')
    
    def __enter__(self):
        self.fb = os.open(self.fbdev, os.O_RDWR)
        self.init_image()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.close(self.fb)

    def init_image(self, bgcolour='black'):
        self.image = Image.new('RGB', (self.screen_size), bgcolour)
        self.draw = ImageDraw.Draw(self.image)

    def draw_text(self, text, coordinates, colour='white', text_size=10):
        font = ImageFont.truetype(self.font_path, text_size)
        self.draw.text(coordinates, text, font=font, fill=colour)

    def rgb_to_rgb565(self, image):
        arr = np.array(image)
        r = (arr[:,:,0] >> 3).astype(np.uint16)
        g = (arr[:,:,1] >> 2).astype(np.uint16)
        b = (arr[:,:,2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        return rgb565.flatten().astype('uint16').tobytes()

    def single_write_to_fb(self):
        rgb565_data = self.rgb_to_rgb565(self.image)
        with open(self.fbdev, 'wb') as fb:
            fb.write(rgb565_data)
    
    def update(self):
        rgb565_data = self.rgb_to_rgb565(self.image)
        os.lseek(self.fb, 0, os.SEEK_SET)
        os.write(self.fb, rgb565_data)

if __name__ == '__main__':
    with TFT_Updater() as tft_updater:
        try:
            while True:
                current_time = time.strftime('%H:%M:%S')
                tft_updater.init_image()
                tft_updater.draw_text(current_time, (0, 50), text_size=30)
                tft_updater.update()
                time.sleep(1)
            
        except KeyboardInterrupt:
            print('exiting')