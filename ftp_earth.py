from PIL import Image
import ctypes
import os
import requests
from io import BytesIO
from change_theme import changeTheme, isDay
import subprocess
import sys


def metered() -> bool:
    """Checks if the system is running on a metered connection

    Returns:
        bool: Network is metered
    """
    if sys.platform in ("linux", "linux2"):
        return subprocess.run(['busctl', 'get-property', 'org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager',
                               'org.freedesktop.NetworkManager', 'Metered'], capture_output=True).stdout.strip()[2:] in ['1', '3']
    elif sys.platform == "darwin":
        # Not implemented yet
        pass
    elif sys.platform == "win32":
        CREATE_NO_WINDOW = 0x08000000
        return subprocess.run(['powershell', '-File', './metered.ps1'], capture_output=True, creationflags=CREATE_NO_WINDOW).stdout.strip() == b'True'
    return False


if __name__ == '__main__':
    # List of output sizes
    sizes = [(1920, 1080)]

    # The image size to download. It's more efficient to download the closest
    # size to your need
    side = 1808

    base = 'https://cdn.star.nesdis.noaa.gov/GOES16/ABI/FD/GEOCOLOR/{}.jpg'
    resolution = str(side)+'x'+str(side)
    url = base.format(resolution)

    if not metered():
        # Load image
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        pixels = image.load()
        assert pixels is not None

        # Remove white bar
        cropped_image = None
        for i in range(image.height-1, 0, -1):
            if pixels[image.width-1, i] < (3, 3, 3):
                cropped_image = image.crop((0, 0, image.width, i+1))
                break
        assert cropped_image is not None

        # Reload cropped image
        pixels = cropped_image.load()
        assert pixels is not None

        # Make NOAA logo black
        for i in range(int(cropped_image.width*1/10)):
            for j in range(cropped_image.height-1, int(cropped_image.height*9/10), -1):
                pixels[i, j] = (1, 1, 1)

        # Make all dark pixels black
        for i in range(cropped_image.width):
            for j in range(cropped_image.height):
                if pixels[i, j] < (2, 2, 2):
                    pixels[i, j] = (0, 0, 0)

        cwd = os.getcwd()
        try:
            os.mkdir(cwd + r'/ftp_earth_images')
        except FileExistsError:
            pass

        # Create images of sizes
        for size in sizes:
            # Shrink to size, maintain aspect ratio
            cropped_image.thumbnail(
                (int(size[0]*0.9), int(size[1]*0.9)), Image.ANTIALIAS)

            # Add background to the right size
            background = Image.new('RGB', size, (0, 0, 0))
            background.paste(cropped_image, tuple(
                map(lambda x: int((x[0]-x[1])/2), zip(size, cropped_image.size))))

            # Save output
            background.save('ftp_earth_images/earth'+'_' +
                            str(size[0])+'x'+str(size[1])+'.png')

        # Sets wallpaper
        if sys.platform in ("linux", "linux2"):
            image_path = f'{cwd}/ftp_earth_images/earth_{sizes[0][0]}x{sizes[0][1]}.png'
            WALLPAPER_PROPERTY = '/backdrop/screen0/monitoreDP-1/workspace0/last-image'
            subprocess.run(['env', 'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus', 'xfconf-query',
                           '--channel', 'xfce4-desktop', '--property', WALLPAPER_PROPERTY, '--set', image_path])
        elif sys.platform == "darwin":
            # Not implemented yet
            pass
        elif sys.platform == "win32":
            ctypes.windll.user32.SystemParametersInfoW(
                20, 0, cwd+r'\ftp_earth_images\earth_'+f'{sizes[0][0]}x{sizes[0][1]}.png', 3)

    else:
        print("Running on a metered network. Won't update")

    if sys.platform == "win32":
        changeTheme(isDay())
