"""Functions and classes related to processing/manipulating strings"""
def remove_prefix(text, prefix):
    """Note that this method can just be replaced by str.removeprefix()
    if the project ever moves to Python 3.9+"""
    if text and text.startswith(prefix):
        return text[len(prefix):]
    return text

def standardize_characters(word):
    return word.lower().replace(' ', '_')\
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
