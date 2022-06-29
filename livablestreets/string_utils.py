"""Functions and classes related to processing/manipulating strings"""
def remove_prefix(text, prefix):
    """Note that this method can just be replaced by str.removeprefix()
    if the project ever moves to Python 3.9+"""
    if text and text.startswith(prefix):
        return text[len(prefix):]
    return text

def standardize_characters(word, separator = '_'):
    return word.lower().replace(' ', separator)\
            .replace('ã','a').replace('õ','o')\
            .replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')\
            .replace('ç','c')\
            .replace('à','a').replace('è','e').replace('ì','i').replace('ò','o').replace('ù','u')\
            .replace('â','a').replace('ê','e').replace('î','i').replace('ô','o').replace('û','u')\
            .replace('ä','ae').replace('ë','e').replace('ï','i').replace('ö','oe').replace('ü','ue')\
            .replace('ß','ss').replace('ñ','n')\
            .replace('ī','i').replace('å','a').replace('æ','ae').replace('ø','o').replace('ÿ','y')\
            .replace('š','s').replace('ý','y')\
            .replace('ş','s').replace('ğ','g')

def capitalize_city_name(word):
    '''Automatically capitalize cities with 3 strings in name where the second string is not capitalized, like Rio de Janeiro or Frankfurt am Main
    '''

    if len(word.split(' ')) == 3:
        word = word.split(' ')
        word[0], word[2] = word[0].capitalize(), word[2].capitalize()
        return ' '.join(word)

    # Automatically capitalize city names
    elif len(word.split(' ')) != 3:
        word = word.split(' ')
        word = [tag.capitalize() for tag in word]
        return ' '.join(word)

    else:
        return word.capitalize()
