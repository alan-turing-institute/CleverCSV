# -*- coding: utf-8 -*-

from typing import Dict
from typing import List
from typing import Pattern

import regex

##########################################
# Regular expressions for number formats #
##########################################

PATTERN_NUMBER_1: Pattern[str] = regex.compile(
    r"^(?=[+-\.\d])"
    r"[+-]?"
    r"(?:0|[1-9]\d*)?"
    r"("
    r"("
    r"(?P<dot>((?<=\d)\.|\.(?=\d)))?"
    r"("
    r"?(dot)(?P<yes_dot>\d*(\d*[eE][+-]?\d+)?)"
    r"|"
    r"(?P<no_dot>((?<=\d)[eE][+-]?\d+)?)"
    r")"
    r")"
    r"|"
    r"("
    r"(?P<comma>,)?"
    r"(?(comma)(?P<yes_comma>\d+(\d+[eE][+-]?\d+)?)"
    r"|"
    r"(?P<no_comma>((?<=\d)[eE][+-]?\d+)?)"
    r")"
    r")"
    r")"
    r"$"
)

PATTERN_NUMBER_2: Pattern[str] = regex.compile(
    r"[+-]?(?:[1-9]|[1-9]\d{0,2})(?:\,\d{3})+\.\d*"
)

PATTERN_NUMBER_3: Pattern[str] = regex.compile(
    r"[+-]?(?:[1-9]|[1-9]\d{0,2})(?:\.\d{3})+\,\d*"
)

##############################################
# Regular expressions for url, email, and ip #
##############################################

PATTERN_URL: Pattern[str] = regex.compile(
    r"("
    r"(https?|ftp):\/\/(?!\-)"
    r")?"
    r"("
    r"((?:[\p{L}\p{N}-]+\.)+([a-z]{2,}|local)(\.[a-z]{2,3})?)"
    r"|"
    r"localhost(\:\d{1,5})?"
    r"|"
    r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\:\d{1,5})?)"
    r")"
    r"(\/[\p{L}\p{N}_\/()~?=&%\-\#\.:]*)?"
    r"(\.[a-z]+)?"
)

PATTERN_EMAIL: Pattern[str] = regex.compile(
    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
)

PATTERN_IPV4: Pattern[str] = regex.compile(r"(?:\d{1,3}\.){3}\d{1,3}")

#################################################
# Regular expressions related to time notations #
#################################################

PATTERN_TIME_HHMMSSZZ: Pattern[str] = regex.compile(
    r"(0[0-9]|1[0-9]|2[0-3])"
    r":"
    r"([0-5][0-9])"
    r":"
    r"([0-5][0-9])"
    r"[+-]"
    r"([0-1][0-9])"
    r":"
    r"([0-5][0-9])"
)

PATTERN_TIME_HHMMSS: Pattern[str] = regex.compile(
    r"(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])"
)

PATTERN_TIME_HHMM_1: Pattern[str] = regex.compile(
    r"(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])"
)

PATTERN_TIME_HHMM_2: Pattern[str] = regex.compile(
    r"(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])"
)

PATTERN_TIME_HH: Pattern[str] = regex.compile(
    r"(0[0-9]|1[0-9]|2[0-3])([0-5][0-9])"
)

PATTERN_TIME_HMM: Pattern[str] = regex.compile(
    r"([0-9]|1[0-9]|2[0-3]):([0-5][0-9])"
)

###############################
# Regular expression for date #
###############################

# Regex for various date formats. See
# https://github.com/alan-turing-institute/CleverCSV/blob/master/notes/date_regex/dateregex_annotated.txt
# for an explanation.
PATTERN_DATE: Pattern[str] = regex.compile(
    r"("
    r"(0[1-9]|1[0-2])"
    r"("
    r"(0[1-9]|[12]\d|3[01])"
    r"([12]\d{3}|\d{2})"
    r"|"
    r"(?P<sep1>[-\/. ])"
    r"(0?[1-9]|[12]\d|3[01])"
    r"(?P=sep1)"
    r"([12]\d{3}|\d{2})"
    r")"
    r"|"
    r"(0[1-9]|[12]\d|3[01])"
    r"("
    r"(0[1-9]|1[0-2])"
    r"([12]\d{3}|\d{2})"
    r"|"
    r"(?P<sep2>[-\/. ])"
    r"(0?[1-9]|1[0-2])"
    r"(?P=sep2)"
    r"([12]\d{3}|\d{2})"
    r")"
    r"|"
    r"([12]\d{3}|\d{2})"
    r"("
    r"(?P<sep3>[-\/. ])"
    r"(0?[1-9]|1[0-2])"
    r"(?P=sep3)"
    r"(0?[1-9]|[12]\d|3[01])"
    r"|"
    r"年(0?[1-9]|1[0-2])月(0?[1-9]|[12]\d|3[01])日"
    r"|"
    r"년(0?[1-9]|1[0-2])월(0?[1-9]|[12]\d|3[01])일"
    r"|"
    r"(0[1-9]|1[0-2])"
    r"(0[1-9]|[12]\d|3[01])"
    r")"
    r"|"
    r"("
    r"([1-9]|1[0-2])"
    r"(?P<sep4>[-\/. ])"
    r"(0?[1-9]|[12]\d|3[01])"
    r"(?P=sep4)([12]\d{3}|\d{2})"
    r"|"
    r"([1-9]|[12]\d|3[01])"
    r"(?P<sep5>[-\/. ])"
    r"(0?[1-9]|1[0-2])"
    r"(?P=sep5)([12]\d{3}|\d{2})"
    r")"
    r")"
)

#############################################
# Regular expressions for alphanumeric text #
#############################################

# Used this site: https://unicode-search.net/unicode-namesearch.pl
# Specials allowed in unicode_alphanum regex if is_quoted = False
SPECIALS_ALLOWED: List[str] = [
    "-",
    "_",
    # Periods
    "\u002e",
    "\u06d4",
    "\u3002",
    "\ufe52",
    "\uff0e",
    "\uff61",
    # Parentheses
    "\u0028",
    "\u0029",
    "\u27ee",
    "\u27ef",
    "\uff08",
    "\uff09",
    # Question marks
    "\u003F",
    "\u00BF",
    "\u037E",
    "\u055E",
    "\u061F",
    "\u1367",
    "\u1945",
    "\u2047",
    "\u2048",
    "\u2049",
    "\u2CFA",
    "\u2CFB",
    "\u2E2E",
    "\uA60F",
    "\uA6F7",
    "\uFE16",
    "\uFE56",
    "\uFF1F",
    chr(69955),  # chakma question mark
    chr(125279),  # adlam initial question mark
    # Exclamation marks
    "\u0021",
    "\u00A1",
    "\u01C3",
    "\u055C",
    "\u07F9",
    "\u109F",
    "\u1944",
    "\u203C",
    "\u2048",
    "\u2049",
    "\uAA77",
    "\uFE15",
    "\uFE57",
    "\uFF01",
    chr(125278),  # adlam initial exclamation mark
]

# Additional specials allowed in unicode_alphanum_quoted regex
QUOTED_SPECIALS_ALLOWED: List[str] = [
    ",",
    "\u060C",
    "\u1363",
    "\u1802",
    "\u1808",
    "\uFF0C",
    "\uFE50",
]

ALPHANUM_SPECIALS: str = regex.escape(r"".join(SPECIALS_ALLOWED))

# Regex for alphanumeric text
PATTERN_ALPHANUM: Pattern[str] = regex.compile(
    r"("
    r"\p{N}?\p{L}+"
    r"["
    r"\p{N}\p{L}\ " + ALPHANUM_SPECIALS + r"]*"
    r"|"
    r"\p{L}?"
    r"["
    r"\p{N}\p{L}\ " + ALPHANUM_SPECIALS + r"]+"
    r")"
)

ALPANUM_QUOTED_SPECIALS: str = regex.escape(
    r"".join(SPECIALS_ALLOWED) + r"".join(QUOTED_SPECIALS_ALLOWED)
)
# Regex for alphanumeric text in quoted strings
PATTERN_ALPHANUM_QUOTED: Pattern[str] = regex.compile(
    r"("
    r"\p{N}?\p{L}+"
    r"["
    r"\p{N}\p{L}\ " + ALPANUM_QUOTED_SPECIALS + r"]*"
    r"|"
    r"\p{L}?"
    r"["
    r"\p{N}\p{L}\ " + ALPANUM_QUOTED_SPECIALS + r"]+"
    r")"
)

###################################
# Regular expression for currency #
###################################

PATTERN_CURRENCY: Pattern[str] = regex.compile(r"\p{Sc}\s?(.*)")

#####################################
# Regular expression for unix paths #
#####################################

PATTERN_UNIX_PATH: Pattern[str] = regex.compile(
    r"[~.]?(?:\/[a-zA-Z0-9\.\-\_]+)+\/?"
)

################################################
# Map of regular expresions for type detection #
################################################

DEFAULT_TYPE_REGEXES: Dict[str, Pattern[str]] = {
    "number_1": PATTERN_NUMBER_1,
    "number_2": PATTERN_NUMBER_2,
    "number_3": PATTERN_NUMBER_3,
    "url": PATTERN_URL,
    "email": PATTERN_EMAIL,
    "ipv4": PATTERN_IPV4,
    "unicode_alphanum": PATTERN_ALPHANUM,
    "unicode_alphanum_quoted": PATTERN_ALPHANUM_QUOTED,
    "time_hhmmss": PATTERN_TIME_HHMMSS,
    "time_hhmm": PATTERN_TIME_HHMM_1,
    "time_HHMM": PATTERN_TIME_HHMM_2,
    "time_HH": PATTERN_TIME_HH,
    "time_hmm": PATTERN_TIME_HMM,
    "time_hhmmsszz": PATTERN_TIME_HHMMSSZZ,
    "currency": PATTERN_CURRENCY,
    "unix_path": PATTERN_UNIX_PATH,
    "date": PATTERN_DATE,
}
