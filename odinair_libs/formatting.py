import collections
from typing import Iterable, Tuple, Dict, Union, List

__all__ = ("difference", "normalize", "tick", "chunks", "flatten", "trim_to", "simple_table")


def simple_table(l1: List[str], l2: List):
    # this is actually just two space-separated joined lists, not even a proper table lol
    if len(l1) != len(l2):
        raise ValueError('length of l1 and l2 are not equal')
    max_len = max([len(x) for x in l1])
    return ["{}{}{}".format(x, ' ' * ((max_len - len(x)) + 2), l2[l1.index(x)]) for x in l1]


def trim_to(text: str, max_len: int):
    if len(text) <= max_len:
        return text
    return "{}\N{HORIZONTAL ELLIPSIS}".format(text[:max_len - 1])


def flatten(d, parent_key='', *, sep='_'):  # https://stackoverflow.com/a/6027615
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def tick(text: str):
    return "\N{WHITE HEAVY CHECK MARK} {}".format(text)


def difference(list1: Iterable, list2: Iterable, *, check_val: bool = False, return_dict: bool = False)\
        -> Tuple[Union[Iterable, Dict], Union[Iterable, Dict]]:
    """Returns a tuple of added or removed items based on the Iterable items passed in

    Parameters
    -----------
    list1: Iterable
        The first list to check
    list2: Iterable
        The second list to check
    check_val: bool
        Whether or not to check values. If this is True, this assumes the lists contain tuple-like or are dicts
    return_dict: bool
        If this is True, this returns a dict of both item keys and values instead of lists of added and removed keys

    Returns
    --------
    dict
        Returned if ``return_dict`` is True
    list
        Returned if ``return_dict`` is False
    """
    if check_val:
        # Only include items that evaluate to True
        list1 = [x for x, val in list1 if val]
        list2 = [x for x, val in list2 if val]

    added = [x for x in list2 if x not in list1]
    removed = [x for x in list1 if x not in list2]

    if return_dict:
        added = {x: list2[x] for x in added}
        removed = {x: list1[x] for x in removed}
    return added, removed


def normalize(text, *, title_case: bool = True, underscores: bool = True, **kwargs):
    """Attempts to normalize a string

    Parameters
    -----------
    text: Any
        The string or object to attempt to normalize
    title_case: bool
        Returns the formatted string as a Title Case string. Any substitutions specified as keyword arguments are done
        before the string is title cased.
    underscores: bool
        Whether or not underscores are replaced with spaces
    """
    text = str(text)
    if underscores:
        text = text.replace("_", " ")
    for item in kwargs:
        text = text.replace(item, kwargs[item])
    if title_case:
        text = text.title()
    return text


def chunks(l, n):  # https://stackoverflow.com/a/312464
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
