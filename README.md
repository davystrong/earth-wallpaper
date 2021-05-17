# Earth Wallpaper

A simple script (for Windows) to update the desktop wallpaper to the latest image from the [NOAA GOES-East](https://www.star.nesdis.noaa.gov/GOES/conus.php?sat=G16) satellite. The task scheduler can be used to run it every ten minutes (the approximate update frequency of the website).

The script first checks if the computer is connected to a metered network, otherwise downloads the image, resizes it, removes the NOAA logo and converts very dark areas to black (useful for OLED screens). It then replaces the desktop wallpaper.

In addition, it checks the sunset time for the current location and changes the Windows theme. This can easily be disabled.

This is currently written for Windows, however, PRs for Linux and Mac would be very welcome.