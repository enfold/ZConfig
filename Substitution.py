"""Substitution support for ZConfig values."""

try:
    False
except NameError:
    False = 0

class SubstitutionSyntaxError(Exception):
    """Raised when interpolation source text contains syntactical errors."""

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


def substitute(s, mapping):
    """Interpolate variables from `section` into `s`."""
    if "$" in s:
        accum = []
        _interp(accum, s, mapping)
        s = ''.join(accum)
    return s


def isname(s):
    """Return True iff s is a valid substitution name."""
    m = _name_match(s)
    if m:
        return m.group() == s
    else:
        return False


def _interp(accum, rest, mapping):
    while 1:
        s, name, rest = _split(rest)
        if s:
            accum.append(s)
        if name:
            v = mapping.get(name, "")
            accum.append(v)
        if not rest:
            return


def _split(s):
    # Return a triple:  prefix, name, suffix
    # - prefix is text that can be used literally in the result (may be '')
    # - name is a referenced name, or None
    # - suffix is trailling text that may contain additional references
    #   (may be '' or None)
    if "$" in s:
        i = s.find("$")
        c = s[i+1:i+2]
        if c == "":
            return s, None, None
        if c == "$":
            return s[:i+1], None, s[i+2:]
        prefix = s[:i]
        if c == "{":
            m = _name_match(s, i + 2)
            if not m:
                raise SubstitutionSyntaxError("'${' not followed by name")
            name = m.group(0)
            i = m.end() + 1
            if not s.startswith("}", i - 1):
                raise SubstitutionSyntaxError(
                    "'${%s' not followed by '}'" % name)
        else:
            m = _name_match(s, i+1)
            if not m:
                return prefix + "$", None, s[i+1:]
            name = m.group(0)
            i = m.end()
        return prefix, name.lower(), s[i:]
    else:
        return s, None, None


import re
_name_match = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*").match
del re
