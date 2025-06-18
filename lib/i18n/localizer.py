# A dictionary that maps outcomes of `getlocale` to two-letter strings:
# it should be completed along with all the language modules that are
# created and deployed with the application

from locale import setlocale, getlocale, LC_ALL

locale_map = {
    # English
    "en_US": "en",
    "en-US": "en",
    "en_UK": "en",
    "en-UK": "en",
    "English_United States": "en",
    "English_United Kingdom": "en",

    # Italian
    "it_IT": "it",
    "it-IT": "it",
    "Italian_Italy": "it",

    # ...
}


# this will hold the two letter form of the locale
_CURRENT_SHORT_LOCALE = None


# retrieve current short locale if not yet set, and cache it for further use
def get_locale():
    global _CURRENT_SHORT_LOCALE
    if _CURRENT_SHORT_LOCALE is None:
        try:
            setlocale(LC_ALL)
            cur_locale = getlocale()[0]
            if cur_locale in locale_map.keys():
                _CURRENT_SHORT_LOCALE = locale_map[cur_locale]
                return locale_map[cur_locale]
        except:
            pass
    return _CURRENT_SHORT_LOCALE


__all__ = ["get_locale"]


# end.
