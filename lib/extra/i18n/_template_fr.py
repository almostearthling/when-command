# Localized UI elements


# standard strings should always be imported, as they may appear inside others
from ...i18n.strings import *


# apart from ITEM_HR_NAME and UI_FORM_TITLE, only the few UI strings that are
# normally at the beginning of the module will have to be redefined here 
ITEM_HR_NAME = "Condition d'exemple'"

UI_FORM_TITLE = f"{UI_APP}: éditeur de conditions d'exemple"
UI_FORM_PARAM1_SC = "Le paramètre est:"


# missing strings will just keep their default values


# end.
