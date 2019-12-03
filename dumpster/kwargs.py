from dumpster.inspector import CodeInspector
import pickle
import sys
from types import ModuleType


def is_primitive(obj):
    return not hasattr(obj, "__dict__")


def save_kwargs_state(kwargs):
    passed = {}
    for k, v in kwargs.items():
        if is_primitive(v):
            passed[k] = v
            continue
        ci = CodeInspector(str(v))
        if ci.register(type(v)):
            passed[k] = {"CI-CLASS": ci.state_blob,
                         "value": pickle.dumps(v),
                         "module": v.__module__}
        else:  # Built in object, Pickle can load this.
            passed[k] = v
    return passed


def make_subpackages(module):
    """
    foo.bar.ham
    >>>
        foo
        foo.bar
        foo.bar.ham

    Parameters
    ----------
    module : str

    Returns
    -------
    out : list[str]
    """
    p = module.split('.')
    out = []
    for i in range(1, len(p) + 1):
        out.append('.'.join(p[:i]))
    return out


def load_kwargs_state(kwargs):
    """
    If model kwargs contained class instances.
    They are tried to be recovered by recreating
    the source modules.

    Python base types are left unmodified.

    Parameters
    ----------
    kwargs : dict

    Returns
    -------
    kwargs : dict

    """
    module_state = ModuleType('mod')
    parsed_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, dict):
            if "CI-CLASS" in v:
                ci = CodeInspector(v['module'])
                ci.load_blob(v["CI-CLASS"])
                module_state.__dict__.update(ci.module.__dict__)

                for mod in make_subpackages(v['module']):
                    sys.modules[mod] = module_state

                parsed_kwargs[k] = pickle.loads(v["value"])
            else:
                parsed_kwargs[k] = v
        else:
            parsed_kwargs[k] = v
    return parsed_kwargs
