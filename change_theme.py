from enum import Enum


class Theme(Enum):
    LIGHT = True
    DARK = False


def changeTheme(theme):
    """This changes the Windows 10 app theme to light or dark.

    Args:
        theme (Theme | bool): Either LIGHT (True) or dark DARK (False)
    """

    from winreg import OpenKey, SetValueEx, QueryValueEx, CloseKey, CreateKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_DWORD
    if type(theme) is Theme:
        theme = theme.value

    value = 1 if theme else 0

    keyPath = r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
    try:
        key = OpenKey(HKEY_CURRENT_USER, keyPath, 0, KEY_ALL_ACCESS)
    except:
        key = CreateKey(HKEY_CURRENT_USER, keyPath)

    if QueryValueEx(key, 'AppsUseLightTheme')[0] != value:
        SetValueEx(key, 'AppsUseLightTheme', 0, REG_DWORD, value)
    CloseKey(key)


def isDay():
    """Checks if the time is after sunset

    Returns:
        bool: Day time
    """
    import datetime
    from pytz import timezone, utc
    from astral import LocationInfo
    from astral.sun import sun
    import geocoder

    g = geocoder.ip('me')

    city = LocationInfo()
    city.latitude = g.latlng[0]
    city.longitude = g.latlng[1]

    s = sun(city.observer, date=datetime.date.today())

    # This presumably depends on the computer's timezone being correct
    now = utc.localize(datetime.datetime.utcnow())

    return s['dawn'] < now < s['dusk']
