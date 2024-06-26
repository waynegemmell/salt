"""
Management of Microsoft SQLServer Databases
===========================================

The mssql_role module is used to create
and manage SQL Server Roles

.. code-block:: yaml

    yolo:
      mssql_role.present
"""


def __virtual__():
    """
    Only load if the mssql module is present
    """
    if "mssql.version" in __salt__:
        return True
    return (False, "mssql module could not be loaded")


def present(name, owner=None, grants=None, **kwargs):
    """
    Ensure that the named database is present with the specified options

    name
        The name of the database to manage
    owner
        Adds owner using AUTHORIZATION option
    Grants
        Can only be a list of strings
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if __salt__["mssql.role_exists"](name, **kwargs):
        ret["comment"] = (
            "Role {} is already present (Not going to try to set its grants)".format(
                name
            )
        )
        return ret
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = f"Role {name} is set to be added"
        return ret

    role_created = __salt__["mssql.role_create"](
        name, owner=owner, grants=grants, **kwargs
    )
    if (
        role_created is not True
    ):  # Non-empty strings are also evaluated to True, so we cannot use if not role_created:
        ret["result"] = False
        ret["comment"] += f"Role {name} failed to be created: {role_created}"
        return ret
    ret["comment"] += f"Role {name} has been added"
    ret["changes"][name] = "Present"
    return ret


def absent(name, **kwargs):
    """
    Ensure that the named database is absent

    name
        The name of the database to remove
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if not __salt__["mssql.role_exists"](name):
        ret["comment"] = f"Role {name} is not present"
        return ret
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = f"Role {name} is set to be removed"
        return ret
    if __salt__["mssql.role_remove"](name, **kwargs):
        ret["comment"] = f"Role {name} has been removed"
        ret["changes"][name] = "Absent"
        return ret
    # else:
    ret["result"] = False
    ret["comment"] = f"Role {name} failed to be removed"
    return ret
