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
    g = re.match(r"^class (\w+)", src)
    return g.group(1)


def split_imports_and_logic(src):
    logic = []
    imports = []
    c = re.compile('\simport\s')
    for line in src.splitlines():
        g = c.search(line)
        if g:
            imports.append(line)
        else:
            logic.append(line)
    return '\n'.join(imports), '\n'.join(logic)


def filter_lines_containing(src, name):
    lines = []
    for line in src.splitlines():
        if name in line:
            continue
        lines.append(line)
    return '\n'.join(lines)

