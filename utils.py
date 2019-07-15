"""Utils."""
import models

from slugify import slugify


def slugcheck(form):
    """Check if slug is already taken and append -n if so."""
    n = 1
    slug = slugify(form.title.data)
    slugtaken = models.Entries.select().where(models.Entries.slug**slug)
    while slugtaken:
        slug = slugify(form.title.data) + '-' + str(n)
        n += 1
        slugtaken = (models.Entries.select()
                     .where(models.Entries.slug**slug))
    return slug


def empty(item):
    """Filter out empty items from a set."""
    return item != ''


def tagger(tagstring):
    """Return ordered list from comma sepatared string."""
    """With duplicates and empty items removed."""
    tags = tagstring.replace(' ', '').lower()
    tags = tags.split(',')
    return set(filter(empty, tags))
