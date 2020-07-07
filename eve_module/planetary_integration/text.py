NO_AUTH_SELECTED_CHARACTER = "It doesn't appear you have a selected character, do `auth select` to find out more."
AUTH_SCOPE_MISSING = "Auth scope {} is missing, contact Alento/Sombra Ghostflame immediately!"
PI_CONTROL_HELP_DESCRIPTION = "Gives information about Planetary Interactions. Be warned, data on EVEs side only " \
                              "updates when you log in, so inaccuracies will only grow larger the longer you aren't " \
                              "logged in. Use `pi` to list this embed."
PI_CONTROL_HELP_COMMAND_PERMISSION = "`pi enable` Flags the selected character to have permissions for PI enabled " \
                                     "next time you run `auth update`\n`pi disable` Does the opposite of enable, " \
                                     "flagging permissions to be disabled."
PI_CONTROL_HELP_COMMAND_UPDATE = "`pi update planet_id` Replace `planet_id` with an ID of the planet you wish to " \
                                 "update the data of.\n`pi update basic` Updates the basic information about PI." \
                                 "\n`pi update full` Updates all PI data."
PI_CONTROL_HELP_COMMAND_INFORMATION = "`pi info` Lists basic PI data of all your planets.\n`pi info planet_id` " \
                                      "Replace `planet_id` with an ID of the planet you wish to view more detailed " \
                                      "PI data of."
PI_CONTROL_SCOPE_FALSE = "You are missing the \"esi-planets.manage_planets.v1\" scope, set it to be enabled by doing " \
                         "`pi enable`"

PI_CONTROL_MISSING_ARG_1 = "Invalid argument, do `pi` to view valid arguments."

PI_CONTROL_ENABLE_SUCCESS = "\"esi-planets.manage_planets.v1\" enabled, run `auth update` to update permissions."
PI_CONTROL_DISABLE_SUCCESS = "\"esi-planets.manage_planets.v1\" disabled, run `auth update` to update permissions."

PI_CONTROL_INVALID_CHAR_OR_PERMISSION = "Something went wrong. If the selected character is valid, contact " \
                                        "Sombra/Alento Ghostflame!"
PI_CONTROL_UPDATE_MISSING_ARG = "This command updates the PI information, do `pi` for more information."
PI_CONTROL_UPDATE_PLANET_SUCCESS = "Updated planet `{}` successfully."
PI_CONTROL_UPDATE_PLANET_NOT_FOUND = "Planet ID `{}` not found."
PI_CONTROL_UPDATE_BASIC_SUCCESS = "Updated basic PI data."
PI_CONTROL_LIST_UPDATING = "Missing basic PI data, fixing that..."
PI_CONTROL_PLANET_INFO_MISSING_ARG = "`pi planet planet_id` Replace `planet_id` with one in `pi list` to get " \
                                     "information about that planet."
PI_CONTROL_PLANET_INFO_ERROR = "An error occurred getting planet info, do you have a colony on the given planet ID?"
PI_CONTROL_PLANET_INFO_ID_NOT_IN_PI_INFO = "Planet ID not in basic PI data, maybe run `pi update basic` ?"
PI_CONTROL_PLANET_INFO_UPDATING = "Missing planet PI data, fixing that..."

PI_CONTROL_ERROR_CLIENTOSERROR = "A networking issue occurred, try again later? If this keeps happening, contact " \
                                 "Alento/Sombra Ghostflame."
