# Localized UI elements


# standard strings should always be imported, as they may appear inside others
from ...i18n.strings import *


# apart from ITEM_HR_NAME and UI_FORM_TITLE, only the few UI strings that are
# normally at the beginning of the module will have to be redefined here 
ITEM_HR_NAME = "Condizione di Esempio"

UI_FORM_TITLE = f"{UI_APP}: Editor di Condizioni di Esempio"
UI_FORM_PARAM1_SC = "Il parametro è:"


# missing strings will just keep their default values


# end.
