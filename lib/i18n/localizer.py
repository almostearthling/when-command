# A dictionary that maps outcomes of `getlocale` to two-letter strings:
# it should be completed along with all the language modules that are
# created and deployed with the application

from locale import setlocale, getlocale, LC_ALL


# the following is a fairly complete language map, with Windows and BCP47
# locale codes, which translates locale names returned by the OS into short
# locale names used in the application i18n toolkit; note that the lowercase
# version of the locale map is used in order to be more permissive in current
# or chosen language detection, a mixed-case map is reported but commented out

# locale_map = {
#     # Afrikaans
#     "Afrikaans_South Africa": "af", "af_ZA": "af", "af-ZA": "af",

#     # Arabic
#     "Arabic_UAE": "ar", "ar_AE": "ar", "ar-AE": "ar",
#     "Arabic_Bahrain": "ar", "ar_BH": "ar", "ar-BH": "ar",
#     "Arabic_Algeria": "ar", "ar_DZ": "ar", "ar-DZ": "ar",
#     "Arabic_Egypt": "ar", "ar_EG": "ar", "ar-EG": "ar",
#     "Arabic_Iraq": "ar", "ar_IQ": "ar", "ar-IQ": "ar",
#     "Arabic_Jordan": "ar", "ar_JO": "ar", "ar-JO": "ar",
#     "Arabic_Kuwait": "ar", "ar_KW": "ar", "ar-KW": "ar",
#     "Arabic_Lebanon": "ar", "ar_LB": "ar", "ar-LB": "ar",
#     "Arabic_Libya": "ar", "ar_LY": "ar", "ar-LY": "ar",
#     "Arabic_Morocco": "ar", "ar_MA": "ar", "ar-MA": "ar",
#     "Arabic_Oman": "ar", "ar_OM": "ar", "ar-OM": "ar",
#     "Arabic_Qatar": "ar", "ar_QA": "ar", "ar-QA": "ar",
#     "Arabic_Saudi Arabia": "ar", "ar_SA": "ar", "ar-SA": "ar",
#     "Arabic_Syria": "ar", "ar_SY": "ar", "ar-SY": "ar",
#     "Arabic_Tunisia": "ar", "ar_TN": "ar", "ar-TN": "ar",
#     "Arabic_Yemen": "ar", "ar_YE": "ar", "ar-YE": "ar",

#     # Azeri
#     "Azeri (Latin)_Azerbaijan": "az", "Azeri (Cyrillic)_Azerbaijan": "az", "az_AZ": "az", "az-AZ": "az",

#     # Belarusian
#     "Belarusian_Belarus": "be", "be_BY": "be", "be-BY": "be",

#     # Bulgarian
#     "Bulgarian_Bulgaria": "bg", "bg_BG": "bg", "bg-BG": "bg",

#     # Lithuanian
#     "Lithuanian_Lithuania": "bo", "bo_LT": "bo", "bo-LT": "bo",

#     # Catalan
#     "Catalan_Spain": "ca", "ca_ES": "ca", "ca-ES": "ca",

#     # Czech
#     "Czech_Czech Republic": "cs", "cs_CZ": "cs", "cs-CZ": "cs",

#     # Danish
#     "Danish_Denmark": "da", "da_DK": "da", "da-DK": "da",

#     # German
#     "German_Austria": "de", "de_AT": "de", "de-AT": "de",
#     "German_Switzerland": "de", "de_CH": "de", "de-CH": "de",
#     "German_Germany": "de", "de_DE": "de", "de-DE": "de",
#     "German_Liechtenstein": "de", "de_LI": "de", "de-LI": "de",
#     "German_Luxembourg": "de", "de_LU": "de", "de-LU": "de",

#     # Greek
#     "Greek_Greece": "el", "el_GR": "el", "el-GR": "el",

#     # English
#     "English_Australia": "en", "en_AU": "en", "en-AU": "en",
#     "English_Belize": "en", "en_BZ": "en", "en-BZ": "en",
#     "English_United Kingdom": "en", "en_GB": "en", "en-GB": "en",
#     "English_Ireland": "en", "en_IE": "en", "en-IE": "en",
#     "English_Jamaica": "en", "en_JM": "en", "en-JM": "en",
#     "English_New Zealand": "en", "en_NZ": "en", "en-NZ": "en",
#     "English_Republic of the Philippines": "en", "en_PH": "en", "en-PH": "en",
#     "English_Trinidad y Tobago": "en", "en_TT": "en", "en-TT": "en",
#     "English_United States": "en", "en_US": "en", "en-US": "en",
#     "English_South Africa": "en", "en_ZA": "en", "en-ZA": "en",
#     "English_Zimbabwe": "en", "en_ZW": "en", "en-ZW": "en",

#     # Spanish
#     "Spanish_Argentina": "es", "es_AR": "es", "es-AR": "es",
#     "Spanish_Bolivia": "es", "es_BO": "es", "es-BO": "es",
#     "Spanish_Chile": "es", "es_CL": "es", "es-CL": "es",
#     "Spanish_Colombia": "es", "es_CO": "es", "es-CO": "es",
#     "Spanish_Costa Rica": "es", "es_CR": "es", "es-CR": "es",
#     "Spanish_Dominican Republic": "es", "es_DO": "es", "es-DO": "es",
#     "Spanish_Ecuador": "es", "es_EC": "es", "es-EC": "es",
#     "Spanish_Spain": "es", "Spanish_Traditional_Sort": "es", "Spanish - Modern Sort_Spain": "es", "es_ES": "es", "es-ES": "es",
#     "Spanish_Guatemala": "es", "es_GT": "es", "es-GT": "es",
#     "Spanish_Honduras": "es", "es_HN": "es", "es-HN": "es",
#     "Spanish_Mexico": "es", "es_MX": "es", "es-MX": "es",
#     "Spanish_Nicaragua": "es", "es_NI": "es", "es-NI": "es",
#     "Spanish_Panama": "es", "es_PA": "es", "es-PA": "es",
#     "Spanish_Peru": "es", "es_PE": "es", "es-PE": "es",
#     "Spanish_Puerto Rico": "es", "es_PR": "es", "es-PR": "es",
#     "Spanish_Paraguay": "es", "es_PY": "es", "es-PY": "es",
#     "Spanish_El Salvador": "es", "es_SV": "es", "es-SV": "es",
#     "Spanish_Uruguay": "es", "es_UY": "es", "es-UY": "es",
#     "Spanish_Venezuela": "es", "es_VE": "es", "es-VE": "es",

#     # Estonian
#     "Estonian_Estonia": "et", "et_EE": "et", "et-EE": "et",

#     # Basque
#     "Basque_Spain": "eu", "eu_ES": "eu", "eu-ES": "eu",

#     # Farsi
#     "Farsi_Iran": "fa", "fa_IR": "fa", "fa-IR": "fa",

#     # Finnish
#     "Finnish_Finland": "fi", "fi_FI": "fi", "fi-FI": "fi",

#     # Faeroese
#     "Faeroese_Faeroe Islands": "fo", "fo_FO": "fo", "fo-FO": "fo",

#     # French
#     "French_Belgium": "fr", "fr_BE": "fr", "fr-BE": "fr",
#     "French_Canada": "fr", "fr_CA": "fr", "fr-CA": "fr",
#     "French_Switzerland": "fr", "fr_CH": "fr", "fr-CH": "fr",
#     "French_France": "fr", "fr_FR": "fr", "fr-FR": "fr",
#     "French_Luxembourg": "fr", "fr_LU": "fr", "fr-LU": "fr",
#     "French_Principality of Monaco": "fr", "fr_MC": "fr", "fr-MC": "fr",

#     # Croatian
#     "Croatian_Croatia": "hr", "hr_HR": "hr", "hr-HR": "hr",

#     # Hungarian
#     "Hungarian_Hungary": "hu", "hu_HU": "hu", "hu-HU": "hu",

#     # Indonesian
#     "Indonesian_Indonesia": "in", "in_ID": "in", "in-ID": "in",

#     # Icelandic
#     "Icelandic_Iceland": "is", "is_IS": "is", "is-IS": "is",

#     # Italian
#     "Italian_Switzerland": "it", "it_CH": "it", "it-CH": "it",
#     "Italian_Italy": "it", "it_IT": "it", "it-IT": "it",

#     # Hebrew
#     "Hebrew_Israel": "iw", "iw_IL": "iw", "iw-IL": "iw",

#     # Japanese
#     "Japanese_Japan": "ja", "ja_JP": "ja", "ja-JP": "ja",

#     # Kazakh
#     "Kazakh_Kazakstan": "kk", "kk_KZ": "kk", "kk-KZ": "kk",

#     # Korean
#     "Korean_Korea": "ko", "ko_KR": "ko", "ko-KR": "ko",

#     # Latvian
#     "Latvian_Latvia": "lv", "lv_LV": "lv", "lv-LV": "lv",

#     # Macedonian
#     "Macedonian_Former Yugoslav Republic of Macedonia": "mk", "mk_MK": "mk", "mk-MK": "mk",

#     # Malay
#     "Malay_Brunei Darussalam": "ms", "ms_BN": "ms", "ms-BN": "ms",
#     "Malay_Malaysia": "ms", "ms_MY": "ms", "ms-MY": "ms",

#     # Dutch
#     "Dutch_Belgium": "nl", "nl_BE": "nl", "nl-BE": "nl",
#     "Dutch_Netherlands": "nl", "nl_NL": "nl", "nl-NL": "nl",

#     # Norwegian
#     "Norwegian_Bokmål": "no", "Norwegian_Nynorsk": "no", "no_NO": "no", "no-NO": "no",
#     "Norwegian_Norway": "no", "no_NO": "no", "no-NO": "no",

#     # Polish
#     "Polish_Poland": "pl", "pl_PL": "pl", "pl-PL": "pl",

#     # Portuguese
#     "Portuguese_Brazil": "pt", "pt_BR": "pt", "pt-BR": "pt",
#     "Portuguese_Portugal": "pt", "pt_PT": "pt", "pt-PT": "pt",

#     # Romanian
#     "Romanian_Romania": "ro", "ro_RO": "ro", "ro-RO": "ro",

#     # Russian
#     "Russian_Russia": "ru", "ru_RU": "ru", "ru-RU": "ru",

#     # Serbian
#     "Serbian (Latin)_Serbia": "sh", "sh_YU": "sh", "sh-YU": "sh",

#     # Slovak
#     "Slovak_Slovakia": "sk", "sk_SK": "sk", "sk-SK": "sk",

#     # Slovenian
#     "Slovenian_Slovenia": "sl", "sl_SI": "sl", "sl-SI": "sl",

#     # Albanian
#     "Albanian_Albania": "sq", "sq_AL": "sq", "sq-AL": "sq",

#     # Serbian
#     "Serbian (Cyrillic)_Serbia": "sr", "sr_YU": "sr", "sr-YU": "sr",

#     # Swedish
#     "Swedish_Finland": "sv", "sv_FI": "sv", "sv-FI": "sv",
#     "Swedish_Sweden": "sv", "sv_SE": "sv", "sv-SE": "sv",

#     # Swahili
#     "Swahili_Kenya": "sw", "sw_KE": "sw", "sw-KE": "sw",

#     # Thai
#     "Thai_Thailand": "th", "th_TH": "th", "th-TH": "th",

#     # Turkish
#     "Turkish_Turkey": "tr", "tr_TR": "tr", "tr-TR": "tr",

#     # Tatar
#     "Tatar_Tatarstan": "tt", "tt_TS": "tt", "tt-TS": "tt",

#     # Ukrainian
#     "Ukrainian_Ukraine": "uk", "uk_UA": "uk", "uk-UA": "uk",

#     # Urdu
#     "Urdu_Islamic Republic of Pakistan": "ur", "ur_PK": "ur", "ur-PK": "ur",

#     # Uzbek
#     "Uzbek_Republic of Uzbekistan": "uz", "uz_UZ": "uz", "uz-UZ": "uz",

#     # Chinese
#     "Chinese_People’s Republic of China": "zh", "zh_CN": "zh", "zh-CN": "zh",
#     "Chinese_Hong Kong": "zh", "Chinese_Hong Kong S.A.R": "zh", "zh_HK": "zh", "zh-HK": "zh",
#     "Chinese_Macau": "zh", "zh_MO": "zh", "zh-MO": "zh",
#     "Chinese_Singapore": "zh", "zh_SG": "zh", "zh-SG": "zh",
#     "Chinese_Taiwan": "zh", "zh_TW": "zh", "zh-TW": "zh",
# }

locale_map = {
    # Afrikaans
    "afrikaans_south africa": "af", "af_za": "af", "af-za": "af",

    # Arabic
    "arabic_uae": "ar", "ar_ae": "ar", "ar-ae": "ar",
    "arabic_bahrain": "ar", "ar_bh": "ar", "ar-bh": "ar",
    "arabic_algeria": "ar", "ar_dz": "ar", "ar-dz": "ar",
    "arabic_egypt": "ar", "ar_eg": "ar", "ar-eg": "ar",
    "arabic_iraq": "ar", "ar_iq": "ar", "ar-iq": "ar",
    "arabic_jordan": "ar", "ar_jo": "ar", "ar-jo": "ar",
    "arabic_kuwait": "ar", "ar_kw": "ar", "ar-kw": "ar",
    "arabic_lebanon": "ar", "ar_lb": "ar", "ar-lb": "ar",
    "arabic_libya": "ar", "ar_ly": "ar", "ar-ly": "ar",
    "arabic_morocco": "ar", "ar_ma": "ar", "ar-ma": "ar",
    "arabic_oman": "ar", "ar_om": "ar", "ar-om": "ar",
    "arabic_qatar": "ar", "ar_qa": "ar", "ar-qa": "ar",
    "arabic_saudi arabia": "ar", "ar_sa": "ar", "ar-sa": "ar",
    "arabic_syria": "ar", "ar_sy": "ar", "ar-sy": "ar",
    "arabic_tunisia": "ar", "ar_tn": "ar", "ar-tn": "ar",
    "arabic_yemen": "ar", "ar_ye": "ar", "ar-ye": "ar",

    # Azeri
    "azeri (latin)_azerbaijan": "az", "azeri (cyrillic)_azerbaijan": "az", "az_az": "az", "az-az": "az",

    # Belarusian
    "belarusian_belarus": "be", "be_by": "be", "be-by": "be",

    # Bulgarian
    "bulgarian_bulgaria": "bg", "bg_bg": "bg", "bg-bg": "bg",

    # Lithuanian
    "lithuanian_lithuania": "bo", "bo_lt": "bo", "bo-lt": "bo",

    # Catalan
    "catalan_spain": "ca", "ca_es": "ca", "ca-es": "ca",

    # Czech
    "czech_czech republic": "cs", "cs_cz": "cs", "cs-cz": "cs",

    # Danish
    "danish_denmark": "da", "da_dk": "da", "da-dk": "da",

    # German
    "german_austria": "de", "de_at": "de", "de-at": "de",
    "german_switzerland": "de", "de_ch": "de", "de-ch": "de",
    "german_germany": "de", "de_de": "de", "de-de": "de",
    "german_liechtenstein": "de", "de_li": "de", "de-li": "de",
    "german_luxembourg": "de", "de_lu": "de", "de-lu": "de",

    # Greek
    "greek_greece": "el", "el_gr": "el", "el-gr": "el",

    # English
    "english_australia": "en", "en_au": "en", "en-au": "en",
    "english_belize": "en", "en_bz": "en", "en-bz": "en",
    "english_united kingdom": "en", "en_gb": "en", "en-gb": "en",
    "english_ireland": "en", "en_ie": "en", "en-ie": "en",
    "english_jamaica": "en", "en_jm": "en", "en-jm": "en",
    "english_new zealand": "en", "en_nz": "en", "en-nz": "en",
    "english_republic of the philippines": "en", "en_ph": "en", "en-ph": "en",
    "english_trinidad y tobago": "en", "en_tt": "en", "en-tt": "en",
    "english_united states": "en", "en_us": "en", "en-us": "en",
    "english_south africa": "en", "en_za": "en", "en-za": "en",
    "english_zimbabwe": "en", "en_zw": "en", "en-zw": "en",

    # Spanish
    "spanish_argentina": "es", "es_ar": "es", "es-ar": "es",
    "spanish_bolivia": "es", "es_bo": "es", "es-bo": "es",
    "spanish_chile": "es", "es_cl": "es", "es-cl": "es",
    "spanish_colombia": "es", "es_co": "es", "es-co": "es",
    "spanish_costa rica": "es", "es_cr": "es", "es-cr": "es",
    "spanish_dominican republic": "es", "es_do": "es", "es-do": "es",
    "spanish_ecuador": "es", "es_ec": "es", "es-ec": "es",
    "spanish_spain": "es", "spanish_traditional_sort": "es", "spanish - modern sort_spain": "es", "es_es": "es", "es-es": "es",
    "spanish_guatemala": "es", "es_gt": "es", "es-gt": "es",
    "spanish_honduras": "es", "es_hn": "es", "es-hn": "es",
    "spanish_mexico": "es", "es_mx": "es", "es-mx": "es",
    "spanish_nicaragua": "es", "es_ni": "es", "es-ni": "es",
    "spanish_panama": "es", "es_pa": "es", "es-pa": "es",
    "spanish_peru": "es", "es_pe": "es", "es-pe": "es",
    "spanish_puerto rico": "es", "es_pr": "es", "es-pr": "es",
    "spanish_paraguay": "es", "es_py": "es", "es-py": "es",
    "spanish_el salvador": "es", "es_sv": "es", "es-sv": "es",
    "spanish_uruguay": "es", "es_uy": "es", "es-uy": "es",
    "spanish_venezuela": "es", "es_ve": "es", "es-ve": "es",

    # Estonian
    "estonian_estonia": "et", "et_ee": "et", "et-ee": "et",

    # Basque
    "basque_spain": "eu", "eu_es": "eu", "eu-es": "eu",

    # Farsi
    "farsi_iran": "fa", "fa_ir": "fa", "fa-ir": "fa",

    # Finnish
    "finnish_finland": "fi", "fi_fi": "fi", "fi-fi": "fi",

    # Faeroese
    "faeroese_faeroe islands": "fo", "fo_fo": "fo", "fo-fo": "fo",

    # French
    "french_belgium": "fr", "fr_be": "fr", "fr-be": "fr",
    "french_canada": "fr", "fr_ca": "fr", "fr-ca": "fr",
    "french_switzerland": "fr", "fr_ch": "fr", "fr-ch": "fr",
    "french_france": "fr", "fr_fr": "fr", "fr-fr": "fr",
    "french_luxembourg": "fr", "fr_lu": "fr", "fr-lu": "fr",
    "french_principality of monaco": "fr", "fr_mc": "fr", "fr-mc": "fr",

    # Croatian
    "croatian_croatia": "hr", "hr_hr": "hr", "hr-hr": "hr",

    # Hungarian
    "hungarian_hungary": "hu", "hu_hu": "hu", "hu-hu": "hu",

    # Indonesian
    "indonesian_indonesia": "in", "in_id": "in", "in-id": "in",

    # Icelandic
    "icelandic_iceland": "is", "is_is": "is", "is-is": "is",

    # Italian
    "italian_switzerland": "it", "it_ch": "it", "it-ch": "it",
    "italian_italy": "it", "it_it": "it", "it-it": "it",

    # Hebrew
    "hebrew_israel": "iw", "iw_il": "iw", "iw-il": "iw",

    # Japanese
    "japanese_japan": "ja", "ja_jp": "ja", "ja-jp": "ja",

    # Kazakh
    "kazakh_kazakstan": "kk", "kk_kz": "kk", "kk-kz": "kk",

    # Korean
    "korean_korea": "ko", "ko_kr": "ko", "ko-kr": "ko",

    # Latvian
    "latvian_latvia": "lv", "lv_lv": "lv", "lv-lv": "lv",

    # Macedonian
    "macedonian_former yugoslav republic of macedonia": "mk", "mk_mk": "mk", "mk-mk": "mk",

    # Malay
    "malay_brunei darussalam": "ms", "ms_bn": "ms", "ms-bn": "ms",
    "malay_malaysia": "ms", "ms_my": "ms", "ms-my": "ms",

    # Dutch
    "dutch_belgium": "nl", "nl_be": "nl", "nl-be": "nl",
    "dutch_netherlands": "nl", "nl_nl": "nl", "nl-nl": "nl",

    # Norwegian
    "norwegian_bokmål": "no", "norwegian_nynorsk": "no", "no_no": "no", "no-no": "no",
    "norwegian_norway": "no", "no_no": "no", "no-no": "no",

    # Polish
    "polish_poland": "pl", "pl_pl": "pl", "pl-pl": "pl",

    # Portuguese
    "portuguese_brazil": "pt", "pt_br": "pt", "pt-br": "pt",
    "portuguese_portugal": "pt", "pt_pt": "pt", "pt-pt": "pt",

    # Romanian
    "romanian_romania": "ro", "ro_ro": "ro", "ro-ro": "ro",

    # Russian
    "russian_russia": "ru", "ru_ru": "ru", "ru-ru": "ru",

    # Serbian
    "serbian (latin)_serbia": "sh", "sh_yu": "sh", "sh-yu": "sh",

    # Slovak
    "slovak_slovakia": "sk", "sk_sk": "sk", "sk-sk": "sk",

    # Slovenian
    "slovenian_slovenia": "sl", "sl_si": "sl", "sl-si": "sl",

    # Albanian
    "albanian_albania": "sq", "sq_al": "sq", "sq-al": "sq",

    # Serbian
    "serbian (cyrillic)_serbia": "sr", "sr_yu": "sr", "sr-yu": "sr",

    # Swedish
    "swedish_finland": "sv", "sv_fi": "sv", "sv-fi": "sv",
    "swedish_sweden": "sv", "sv_se": "sv", "sv-se": "sv",

    # Swahili
    "swahili_kenya": "sw", "sw_ke": "sw", "sw-ke": "sw",

    # Thai
    "thai_thailand": "th", "th_th": "th", "th-th": "th",

    # Turkish
    "turkish_turkey": "tr", "tr_tr": "tr", "tr-tr": "tr",

    # Tatar
    "tatar_tatarstan": "tt", "tt_ts": "tt", "tt-ts": "tt",

    # Ukrainian
    "ukrainian_ukraine": "uk", "uk_ua": "uk", "uk-ua": "uk",

    # Urdu
    "urdu_islamic republic of pakistan": "ur", "ur_pk": "ur", "ur-pk": "ur",

    # Uzbek
    "uzbek_republic of uzbekistan": "uz", "uz_uz": "uz", "uz-uz": "uz",

    # Chinese
    "chinese_people’s republic of china": "zh", "zh_cn": "zh", "zh-cn": "zh",
    "chinese_hong kong": "zh", "chinese_hong kong s.a.r": "zh", "zh_hk": "zh", "zh-hk": "zh",
    "chinese_macau": "zh", "zh_mo": "zh", "zh-mo": "zh",
    "chinese_singapore": "zh", "zh_sg": "zh", "zh-sg": "zh",
    "chinese_taiwan": "zh", "zh_tw": "zh", "zh-tw": "zh",
}


# this will hold the two letter form of the locale
_CURRENT_SHORT_LOCALE = None


# retrieve current short locale if not yet set, and cache it for further use
def get_locale(force_locale=None):
    global _CURRENT_SHORT_LOCALE
    if _CURRENT_SHORT_LOCALE is None:
        try:
            if force_locale is None:
                setlocale(LC_ALL)
                # ignore the type check, as the case is handled by `except:`
                cur_locale = getlocale()[0].lower()     # type: ignore
            else:
                cur_locale = force_locale.lower()
            if cur_locale in locale_map.keys():
                _CURRENT_SHORT_LOCALE = locale_map[cur_locale]
                return locale_map[cur_locale]
        except:
            pass
    return _CURRENT_SHORT_LOCALE


__all__ = ["get_locale"]


# end.
