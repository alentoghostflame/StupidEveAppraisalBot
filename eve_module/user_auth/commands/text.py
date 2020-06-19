EVE_AUTH_CONTROL_MISSING_ARG_1 = "`auth list|create|delete|select|info|update|token`"

EVE_AUTH_CONTROL_SELECT_MISSING_ARG = "`auth select character_id` selects a character for the rest of the bot to " \
                                      "use. Replace `character_id` with the ID of the character listed in the " \
                                      "command `auth list`"
EVE_AUTH_CONTROL_CREATE_TEXT = "<{}>\nClick that link, and authorize with the character you want to add. After " \
                               "authorization, you will be redirected to a page that can't be reached. Copy the url " \
                               "and run the command `auth token insert_link_here`, replacing `insert_link_here` with " \
                               "the URL you copied."
EVE_AUTH_CONTROL_DELETE_MISSING_ARG = "`auth delete character_id` removes a character from the bot. Replace " \
                                      "`character_id` with the ID of the character to be deleted, found by running " \
                                      "the command `auth list`"
EVE_AUTH_CONTROL_DELETE_SUCCESS = "Successfully deleted the character."
EVE_AUTH_CONTROL_SELECT_SUCCESS = "Selected character set to \"{}\""

EVE_AUTH_CONTROL_INFO_MISSING_ARG = "`auth info character_id` gives info about a character. Replaced `character_id` " \
                                    "with the ID of the character listed in the command `auth list`"

EVE_AUTH_CONTROL_UPDATE_SUCCESS = "<{}>\nClick on that link and authorize with the character you want to update " \
                                  "permissions for. After authorization, you will be redirected to a page that can't " \
                                  "be reached. Copy the URL and run the command `auth token insert_link_here`, " \
                                  "replacing `insert_link_here` with the URL you copied.\n The link above can be " \
                                  "used to update multiple characters, not just the currently selected one."
EVE_AUTH_CONTROL_UPDATE_CURRENT_DESIRED_EQUAL = "All desired scopes for the selected character seem to be already " \
                                                "met. If you want to force the auth URL anyway, run `auth update force`"
EVE_AUTH_CONTROL_UPDATE_ARG_NOT_FORCE = "Did you mean `auth update force` ?"

EVE_AUTH_CONTROL_REGISTER_TOKEN_MISSING_ARG = "`auth token insert_link_here` registers a character for use by this " \
                                              "bot. For use of this command, see `auth create`"
EVE_AUTH_CONTROL_REGISTER_TOKEN_INVALID = "Given URL is invalid."
EVE_AUTH_CONTROL_REGISTER_SUCCESS = "Token registered. Welcome, {}."

EVE_AUTH_CONTROL_CONTEXT_HAS_GUILD = "For account security reasons, this command only works in DMs."


CHARACTER_ID_NOT_FOUND = "ID not found, character IDs are listed in the command `auth list`"
NO_AUTH_SELECTED_CHARACTER = "It doesn't appear you have a selected character, do `auth select` to find out more."
