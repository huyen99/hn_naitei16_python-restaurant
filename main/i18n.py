'''
Fake file to translate messages from django.contrib.auth.
'''

def _(text):
    return text

def fake():
    min_length = 8
    _(u"Enter the same password as before, for verification.")
    _(u"Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    _(u"The password is too similar to the %(verbose_name)s.")
    _(u"Your password can’t be too similar to your other personal information.")
    _(u"This password is too common.")
    _(u"Your password can’t be a commonly used password.")
    _(u"This password is entirely numeric.")
    _(u"Your password can’t be entirely numeric.")
    _(u"Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.")
    ngettext(
        "Your password must contain at least %(min_length)d character.",
        "Your password must contain at least %(min_length)d characters.",
        min_length
    )
    ngettext(
        "This password is too short. It must contain at least %(min_length)d character.",
        "This password is too short. It must contain at least %(min_length)d characters.",
        min_length
    )
    _(u"The two password fields didn’t match.")
