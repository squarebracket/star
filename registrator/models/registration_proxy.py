from registrator.models.registration_entry import RegistrationEntry


class RegistrationProxy(RegistrationEntry):
    """
    Proxy class which handles actually doing the registration in a system
    of a :model:`registrator.RegistrationEntry`
    """

    # I guess functions for registration in Concordia's system would go here?

    class Meta:
        proxy = True

