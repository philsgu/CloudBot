import re

from cloudbot import hook
from cloudbot.util.formatting import ireplace

correction_re = re.compile(r"^[sS]/(?:(.*?)(?<!\\)/(.*?)(?:(?<!\\)/([igx]{,4}))?)\s*$")
unescape_re = re.compile(r'\\(.)')


@hook.regex(correction_re)
def correction(match, conn, nick, chan, message):
    """
    :type match: re.__Match
    :type conn: cloudbot.client.Client
    :type chan: str
    """
    groups = [unescape_re.sub(r"\1", group or "") for group in match.groups()]
    find = groups[0]
    replace = groups[1]
    if find == replace:
        return "really dude? you want me to replace {} with {}?".format(find, replace)

    if not find.strip():  # Replacing empty or entirely whitespace strings is spammy
        return "really dude? you want me to replace nothing with {}?".format(replace)

    for item in conn.history[chan].__reversed__():
        name, timestamp, msg = item
        if correction_re.match(msg):
            # don't correct corrections, it gets really confusing
            continue

        if find.lower() in msg.lower():
            find_esc = re.escape(find)
            replace_esc = re.escape(replace)
            if "\x01ACTION" in msg:
                msg = msg.replace("\x01ACTION", "").replace("\x01", "")
                mod_msg = ireplace(msg, find_esc, "\x02" + replace_esc + "\x02")
                message("Correction, * {} {}".format(name, mod_msg))
            else:
                mod_msg = ireplace(msg, find_esc, "\x02" + replace_esc + "\x02")
                message("Correction, <{}> {}".format(name, mod_msg))

            msg = ireplace(msg, find_esc, replace_esc)
            if nick.lower() == name.lower():
                conn.history[chan].append((name, timestamp, msg))
            return
        else:
            continue
            # return("No matches for \"\x02{}\x02\" in recent messages from \x02{}\x02. You can only correct your own messages.".format(find, nick))
