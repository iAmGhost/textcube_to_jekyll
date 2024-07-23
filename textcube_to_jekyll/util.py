import unicodedata
import re


def convert_ttml(content: str):
    from textcube_to_jekyll.template import get_template

    moreless_template = get_template('moreless.html')
    match = re.match(r'\[#M_(?P<open_text>.+?)\|(?P<close_text>.+?)\|(?P<content>.+?)_M#\]', content)

    content = moreless_template.render(
        open_text=match.group('open_text'),
        close_text=match.group('close_text'),
        content=match.group('content'),
    )


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')