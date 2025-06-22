# A dictionary that maps outcomes of `getlocale` to two-letter strings:
# it should be completed along with all the language modules that are
# created and deployed with the application

from locale import setlocale, getlocale, LC_ALL


# the following is a fairly complete language map, with Windows and BCP47
# locale codes, which translates locale names returned by the OS into short
# locale names used in the application i18n toolkit
locale_map = {
    # Afrikaans
    "Afrikaans_South Africa": "af", "af_ZA": "af", "af-ZA": "af",

    # Arabic
    "Arabic_UAE": "ar", "ar_AE": "ar", "ar-AE": "ar",
    "Arabic_Bahrain": "ar", "ar_BH": "ar", "ar-BH": "ar",
    "Arabic_Algeria": "ar", "ar_DZ": "ar", "ar-DZ": "ar",
    "Arabic_Egypt": "ar", "ar_EG": "ar", "ar-EG": "ar",
    "Arabic_Iraq": "ar", "ar_IQ": "ar", "ar-IQ": "ar",
    "Arabic_Jordan": "ar", "ar_JO": "ar", "ar-JO": "ar",
    "Arabic_Kuwait": "ar", "ar_KW": "ar", "ar-KW": "ar",
    "Arabic_Lebanon": "ar", "ar_LB": "ar", "ar-LB": "ar",
    "Arabic_Libya": "ar", "ar_LY": "ar", "ar-LY": "ar",
    "Arabic_Morocco": "ar", "ar_MA": "ar", "ar-MA": "ar",
    "Arabic_Oman": "ar", "ar_OM": "ar", "ar-OM": "ar",
    "Arabic_Qatar": "ar", "ar_QA": "ar", "ar-QA": "ar",
    "Arabic_Saudi Arabia": "ar", "ar_SA": "ar", "ar-SA": "ar",
    "Arabic_Syria": "ar", "ar_SY": "ar", "ar-SY": "ar",
    "Arabic_Tunisia": "ar", "ar_TN": "ar", "ar-TN": "ar",
    "Arabic_Yemen": "ar", "ar_YE": "ar", "ar-YE": "ar",

    # Azeri
    "Azeri (Latin)_Azerbaijan": "az", "Azeri (Cyrillic)_Azerbaijan": "az", "az_AZ": "az", "az-AZ": "az",

    # Belarusian
    "Belarusian_Belarus": "be", "be_BY": "be", "be-BY": "be",

    # Bulgarian
    "Bulgarian_Bulgaria": "bg", "bg_BG": "bg", "bg-BG": "bg",

    # Lithuanian
    "Lithuanian_Lithuania": "bo", "bo_LT": "bo", "bo-LT": "bo",

    # Catalan
    "Catalan_Spain": "ca", "ca_ES": "ca", "ca-ES": "ca",

    # Czech
    "Czech_Czech Republic": "cs", "cs_CZ": "cs", "cs-CZ": "cs",

    # Danish
    "Danish_Denmark": "da", "da_DK": "da", "da-DK": "da",

    # German
    "German_Austria": "de", "de_AT": "de", "de-AT": "de",
    "German_Switzerland": "de", "de_CH": "de", "de-CH": "de",
    "German_Germany": "de", "de_DE": "de", "de-DE": "de",
    "German_Liechtenstein": "de", "de_LI": "de", "de-LI": "de",
    "German_Luxembourg": "de", "de_LU": "de", "de-LU": "de",

    # Greek
    "Greek_Greece": "el", "el_GR": "el", "el-GR": "el",

    # English
    "English_Australia": "en", "en_AU": "en", "en-AU": "en",
    "English_Belize": "en", "en_BZ": "en", "en-BZ": "en",
    "English_United Kingdom": "en", "en_GB": "en", "en-GB": "en",
    "English_Ireland": "en", "en_IE": "en", "en-IE": "en",
    "English_Jamaica": "en", "en_JM": "en", "en-JM": "en",
    "English_New Zealand": "en", "en_NZ": "en", "en-NZ": "en",
    "English_Republic of the Philippines": "en", "en_PH": "en", "en-PH": "en",
    "English_Trinidad y Tobago": "en", "en_TT": "en", "en-TT": "en",
    "English_United States": "en", "en_US": "en", "en-US": "en",
    "English_South Africa": "en", "en_ZA": "en", "en-ZA": "en",
    "English_Zimbabwe": "en", "en_ZW": "en", "en-ZW": "en",

    # Spanish
    "Spanish_Argentina": "es", "es_AR": "es", "es-AR": "es",
    "Spanish_Bolivia": "es", "es_BO": "es", "es-BO": "es",
    "Spanish_Chile": "es", "es_CL": "es", "es-CL": "es",
    "Spanish_Colombia": "es", "es_CO": "es", "es-CO": "es",
    "Spanish_Costa Rica": "es", "es_CR": "es", "es-CR": "es",
    "Spanish_Dominican Republic": "es", "es_DO": "es", "es-DO": "es",
    "Spanish_Ecuador": "es", "es_EC": "es", "es-EC": "es",
    "Spanish_Spain": "es", "Spanish_Traditional_Sort": "es", "Spanish - Modern Sort_Spain": "es", "es_ES": "es", "es-ES": "es",
    "Spanish_Guatemala": "es", "es_GT": "es", "es-GT": "es",
    "Spanish_Honduras": "es", "es_HN": "es", "es-HN": "es",
    "Spanish_Mexico": "es", "es_MX": "es", "es-MX": "es",
    "Spanish_Nicaragua": "es", "es_NI": "es", "es-NI": "es",
    "Spanish_Panama": "es", "es_PA": "es", "es-PA": "es",
    "Spanish_Peru": "es", "es_PE": "es", "es-PE": "es",
    "Spanish_Puerto Rico": "es", "es_PR": "es", "es-PR": "es",
    "Spanish_Paraguay": "es", "es_PY": "es", "es-PY": "es",
    "Spanish_El Salvador": "es", "es_SV": "es", "es-SV": "es",
    "Spanish_Uruguay": "es", "es_UY": "es", "es-UY": "es",
    "Spanish_Venezuela": "es", "es_VE": "es", "es-VE": "es",

    # Estonian
    "Estonian_Estonia": "et", "et_EE": "et", "et-EE": "et",

    # Basque
    "Basque_Spain": "eu", "eu_ES": "eu", "eu-ES": "eu",

    # Farsi
    "Farsi_Iran": "fa", "fa_IR": "fa", "fa-IR": "fa",

    # Finnish
    "Finnish_Finland": "fi", "fi_FI": "fi", "fi-FI": "fi",

    # Faeroese
    "Faeroese_Faeroe Islands": "fo", "fo_FO": "fo", "fo-FO": "fo",

    # French
    "French_Belgium": "fr", "fr_BE": "fr", "fr-BE": "fr",
    "French_Canada": "fr", "fr_CA": "fr", "fr-CA": "fr",
    "French_Switzerland": "fr", "fr_CH": "fr", "fr-CH": "fr",
    "French_France": "fr", "fr_FR": "fr", "fr-FR": "fr",
    "French_Luxembourg": "fr", "fr_LU": "fr", "fr-LU": "fr",
    "French_Principality of Monaco": "fr", "fr_MC": "fr", "fr-MC": "fr",

    # Croatian
    "Croatian_Croatia": "hr", "hr_HR": "hr", "hr-HR": "hr",

    # Hungarian
    "Hungarian_Hungary": "hu", "hu_HU": "hu", "hu-HU": "hu",

    # Indonesian
    "Indonesian_Indonesia": "in", "in_ID": "in", "in-ID": "in",

    # Icelandic
    "Icelandic_Iceland": "is", "is_IS": "is", "is-IS": "is",

    # Italian
    "Italian_Switzerland": "it", "it_CH": "it", "it-CH": "it",
    "Italian_Italy": "it", "it_IT": "it", "it-IT": "it",

    # Hebrew
    "Hebrew_Israel": "iw", "iw_IL": "iw", "iw-IL": "iw",

    # Japanese
    "Japanese_Japan": "ja", "ja_JP": "ja", "ja-JP": "ja",

    # Kazakh
    "Kazakh_Kazakstan": "kk", "kk_KZ": "kk", "kk-KZ": "kk",

    # Korean
    "Korean_Korea": "ko", "ko_KR": "ko", "ko-KR": "ko",

    # Latvian
    "Latvian_Latvia": "lv", "lv_LV": "lv", "lv-LV": "lv",

    # Macedonian
    "Macedonian_Former Yugoslav Republic of Macedonia": "mk", "mk_MK": "mk", "mk-MK": "mk",

    # Malay
    "Malay_Brunei Darussalam": "ms", "ms_BN": "ms", "ms-BN": "ms",
    "Malay_Malaysia": "ms", "ms_MY": "ms", "ms-MY": "ms",

    # Dutch
    "Dutch_Belgium": "nl", "nl_BE": "nl", "nl-BE": "nl",
    "Dutch_Netherlands": "nl", "nl_NL": "nl", "nl-NL": "nl",

    # Norwegian
    "Norwegian_Bokmål": "no", "Norwegian_Nynorsk": "no", "no_NO": "no", "no-NO": "no",
    "Norwegian_Norway": "no", "no_NO": "no", "no-NO": "no",

    # Polish
    "Polish_Poland": "pl", "pl_PL": "pl", "pl-PL": "pl",

    # Portuguese
    "Portuguese_Brazil": "pt", "pt_BR": "pt", "pt-BR": "pt",
    "Portuguese_Portugal": "pt", "pt_PT": "pt", "pt-PT": "pt",

    # Romanian
    "Romanian_Romania": "ro", "ro_RO": "ro", "ro-RO": "ro",

    # Russian
    "Russian_Russia": "ru", "ru_RU": "ru", "ru-RU": "ru",

    # Serbian
    "Serbian (Latin)_Serbia": "sh", "sh_YU": "sh", "sh-YU": "sh",

    # Slovak
    "Slovak_Slovakia": "sk", "sk_SK": "sk", "sk-SK": "sk",

    # Slovenian
    "Slovenian_Slovenia": "sl", "sl_SI": "sl", "sl-SI": "sl",

    # Albanian
    "Albanian_Albania": "sq", "sq_AL": "sq", "sq-AL": "sq",

    # Serbian
    "Serbian (Cyrillic)_Serbia": "sr", "sr_YU": "sr", "sr-YU": "sr",

    # Swedish
    "Swedish_Finland": "sv", "sv_FI": "sv", "sv-FI": "sv",
    "Swedish_Sweden": "sv", "sv_SE": "sv", "sv-SE": "sv",

    # Swahili
    "Swahili_Kenya": "sw", "sw_KE": "sw", "sw-KE": "sw",

    # Thai
    "Thai_Thailand": "th", "th_TH": "th", "th-TH": "th",

    # Turkish
    "Turkish_Turkey": "tr", "tr_TR": "tr", "tr-TR": "tr",

    # Tatar
    "Tatar_Tatarstan": "tt", "tt_TS": "tt", "tt-TS": "tt",

    # Ukrainian
    "Ukrainian_Ukraine": "uk", "uk_UA": "uk", "uk-UA": "uk",

    # Urdu
    "Urdu_Islamic Republic of Pakistan": "ur", "ur_PK": "ur", "ur-PK": "ur",

    # Uzbek
    "Uzbek_Republic of Uzbekistan": "uz", "uz_UZ": "uz", "uz-UZ": "uz",

    # Chinese
    "Chinese_People’s Republic of China": "zh", "zh_CN": "zh", "zh-CN": "zh",
    "Chinese_Hong Kong": "zh", "Chinese_Hong Kong S.A.R": "zh", "zh_HK": "zh", "zh-HK": "zh",
    "Chinese_Macau": "zh", "zh_MO": "zh", "zh-MO": "zh",
    "Chinese_Singapore": "zh", "zh_SG": "zh", "zh-SG": "zh",
    "Chinese_Taiwan": "zh", "zh_TW": "zh", "zh-TW": "zh",
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
