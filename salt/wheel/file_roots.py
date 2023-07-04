"""
Read in files from the file_root and save files to the file root
"""


import os

import salt.utils.files
import salt.utils.path


def find(path, saltenv="base"):
    """
    Return a dict of the files located with the given path and environment
    """
    # Return a list of paths + text or bin
    ret = []
    if saltenv not in __opts__["file_roots"]:
        return ret
    for root in __opts__["file_roots"][saltenv]:
        full = os.path.join(root, path)
        if not salt.utils.verify.clean_path(root, full, subdir=True):
            continue
        if os.path.isfile(full):
            # Add it to the dict
            with salt.utils.files.fopen(full, "rb") as fp_:
                if salt.utils.files.is_text(fp_):
                    ret.append({full: "txt"})
                else:
                    ret.append({full: "bin"})
    return ret


def list_env(saltenv="base"):
    """
    Return all of the file paths found in an environment
    """
    ret = {}
    if saltenv not in __opts__["file_roots"]:
        return ret
    for f_root in __opts__["file_roots"][saltenv]:
        ret[f_root] = {}
        for root, dirs, files in salt.utils.path.os_walk(f_root):
            sub = ret[f_root]
            if root != f_root:
                # grab subroot ref
                sroot = root
                above = []
                # Populate the above dict
                while not os.path.samefile(sroot, f_root):
                    base = os.path.basename(sroot)
                    if base:
                        above.insert(0, base)
                    sroot = os.path.dirname(sroot)
                for aroot in above:
                    sub = sub[aroot]
            for dir_ in dirs:
                sub[dir_] = {}
            for fn_ in files:
                sub[fn_] = "f"
    return ret


def list_roots():
    """
    Return all of the files names in all available environments
    """
    ret = {}
    for saltenv in __opts__["file_roots"]:
        ret[saltenv] = []
        ret[saltenv].append(list_env(saltenv))
    return ret


def read(path, saltenv="base"):
    """
    Read the contents of a text file, if the file is binary then ignore it
    """
    # Return a dict of paths + content
    ret = []
    files = find(path, saltenv)
    for fn_ in files:
        full = next(iter(fn_.keys()))
        form = fn_[full]
        if form == "txt":
            with salt.utils.files.fopen(full, "rb") as fp_:
                ret.append({full: salt.utils.stringutils.to_unicode(fp_.read())})
    return ret


def write(data, path, saltenv="base", index=0):
    """
    Write the named file, by default the first file found is written, but the
    index of the file can be specified to write to a lower priority file root
    """
    if saltenv not in __opts__["file_roots"]:
        return f"Named environment {saltenv} is not present"
    if len(__opts__["file_roots"][saltenv]) <= index:
        return "Specified index {} in environment {} is not present".format(
            index, saltenv
        )
    if os.path.isabs(path):
        return "The path passed in {} is not relative to the environment {}".format(
            path, saltenv
        )
    root = __opts__["file_roots"][saltenv][index]
    dest = os.path.join(root, path)
    if not salt.utils.verify.clean_path(root, dest, subdir=True):
        return f"Invalid path: {path}"
    dest_dir = os.path.dirname(dest)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    with salt.utils.files.fopen(dest, "w+") as fp_:
        fp_.write(salt.utils.stringutils.to_str(data))
    return f"Wrote data to file {dest}"
