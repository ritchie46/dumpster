import re


def clean_source(src):
    """
    Make source found by introspection executable.

    Parameters
    ----------
    src : str
        Python source code

    Returns
    -------
    src : str
        Cleaned Python source code
    """
    m = re.match(r"^\s+", src)

    # remove indentation if needed
    if m:
        # number of leading spaces
        n = len(m.group(0))
        lines = src.splitlines()
        src = ""
        for line in lines:
            src += line[n:] + "\n"

    return src


def get_class_name(src):
    g = re.match(r"^class (\w+)\(", src)
    return g.group(1)
