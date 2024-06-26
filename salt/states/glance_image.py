"""
Management of OpenStack Glance Images
========================================

.. versionadded:: 2018.3.0

:depends: shade
:configuration: see :py:mod:`salt.modules.glanceng` for setup instructions

Example States

.. code-block:: yaml

    create image:
      glance_image.present:
        - name: cirros
        - filename: cirros.raw
        - image_format: raw

    delete image:
      glance_image.absent:
        - name: cirros
"""

__virtualname__ = "glance_image"


def __virtual__():
    if "glanceng.image_get" in __salt__:
        return __virtualname__
    return (
        False,
        "The glanceng execution module failed to load: shade python module is not"
        " available",
    )


def present(name, auth=None, **kwargs):
    """
    Ensure image exists and is up-to-date

    name
        Name of the image

    enabled
        Boolean to control if image is enabled

    description
        An arbitrary description of the image
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    kwargs = __utils__["args.clean_kwargs"](**kwargs)

    __salt__["glanceng.setup_clouds"](auth)

    image = __salt__["glanceng.image_get"](name=name)

    if not image:
        if __opts__["test"]:
            ret["result"] = None
            ret["changes"] = kwargs
            ret["comment"] = f"Image {name} will be created."
            return ret

        kwargs["name"] = name
        image = __salt__["glanceng.image_create"](**kwargs)
        ret["changes"] = image
        ret["comment"] = "Created image"
        return ret

    # TODO(SamYaple): Compare and update image properties here
    return ret


def absent(name, auth=None):
    """
    Ensure image does not exist

    name
        Name of the image
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    __salt__["glanceng.setup_clouds"](auth)

    image = __salt__["glanceng.image_get"](name=name)

    if image:
        if __opts__["test"]:
            ret["result"] = None
            ret["changes"] = {"name": name}
            ret["comment"] = f"Image {name} will be deleted."
            return ret

        __salt__["glanceng.image_delete"](name=image)
        ret["changes"]["id"] = image.id
        ret["comment"] = "Deleted image"

    return ret
