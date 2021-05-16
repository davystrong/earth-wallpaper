from PIL import Image
import PIL
import ctypes
import os
import requests
from io import BytesIO
from change_theme import changeTheme, isDay
import subprocess

base = 'https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/{}.jpg'
side = 1808
resolution = str(side)+'x'+str(side)
url = base.format(resolution)


def metered():
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.run(['powershell', '-File', './metered.ps1'], capture_output=True, creationflags=CREATE_NO_WINDOW).stdout.strip() == b'True'


if not metered():
    print('Ok')
    # Load image
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    pixels = image.load()

    # Remove white bar
    for i in range(image.height-1, 0, -1):
        if pixels[image.width-1, i] < (3, 3, 3):
            cropped_image = image.crop((0, 0, image.width, i+1))
            break

    # Reload cropped image
    pixels = cropped_image.load()

    # Make NOAA logo black
    for i in range(int(cropped_image.width*1/10)):
        for j in range(cropped_image.height-1, int(cropped_image.height*9/10), -1):
            pixels[i, j] = (1, 1, 1)

    # Make all dark pixels black
    for i in range(cropped_image.width):
        for j in range(cropped_image.height):
            if pixels[i, j] < (2, 2, 2):
                pixels[i, j] = (0, 0, 0)

    # List of output sizes
    sizes = [(1920, 1080), (1080, 1920), (1080, 2220)]

    cwd = os.getcwd()
    try:
        os.mkdir(cwd + r'\ftp_earth_images')
    except FileExistsError:
        pass

    # Create images of sizes
    for size in sizes:
        # Shrink to size, maintain aspect ratio
        cropped_image.thumbnail(
            (int(size[0]*0.9), int(size[1]*0.9)), PIL.Image.ANTIALIAS)

        # Add background to the right size
        background = Image.new('RGB', size, (0, 0, 0))
        background.paste(cropped_image, tuple(
            map(lambda x: int((x[0]-x[1])/2), zip(size, cropped_image.size))))

        # Save output
        background.save('ftp_earth_images/earth'+'_' +
                        str(size[0])+'x'+str(size[1])+'.png')

    # Sets wallpaper
    ctypes.windll.user32.SystemParametersInfoW(
        20, 0, cwd+r'\ftp_earth_images\earth_1920x1080.png', 3)

else:
    print("Running on a metered network. Won't update")

changeTheme(isDay())
