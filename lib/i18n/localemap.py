# A dictionary that maps outcomes of `getlocale` to two-letter strings:
# it should be completed along with all the language modules that are
# created and deployed with the application

from locale import getlocale

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

def get_locale():
    try:
        cur_locale = getlocale()[0]
        if cur_locale in locale_map.keys():
            return locale_map[cur_locale]
    except:
        return None


__all__ = ["get_locale"]


# end.
