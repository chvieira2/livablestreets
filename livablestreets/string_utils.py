"""Functions and classes related to processing/manipulating strings"""

import re


def remove_prefix(text, prefix):
    """Note that this method can just be replaced by str.removeprefix()
    if the project ever moves to Python 3.9+"""
    if text and text.startswith(prefix):
        return text[len(prefix):]
    return text

def german_characters(word):
    word = word.replace('_', ' ')\
            .replace('ae','ä').replace('oe','ö').replace('ue','ü')
    if word != 'Düsseldorf':
        word = word.replace('ss','ß')
    return word


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

    if word.lower() == 'salt lake city':
        return 'Salt Lake City'

    elif len(word.split(' ')) == 3:
        word = word.split(' ')
        word[0], word[2] = word[0].capitalize(), word[2].capitalize()
        return ' '.join(word)

    # Automatically capitalize city names with single word, 2 words, or above 3 words capitalize first and last
    else:# len(word.split(' ')) != 3:
        word = word.split(' ')
        word[0] = word[0].capitalize()
        word[-1] = word[-1].capitalize()
        return ' '.join(word)

def simplify_address(address):
    street_houseN = address.split(',')[0]
    street = re.findall('\D+', street_houseN) # \D matches non-digits
    try:
        street = street[0].strip()
        street = ' '.join([word.capitalize().strip() for word in street.split(' ')])
    except IndexError:
        street = ''
    try:
        houseN = re.findall('\d+', street_houseN)[0]
    except IndexError:
        houseN = ''
    city_neigh = address.split(',')[1].split(' ')
    city = city_neigh[1].capitalize() # [0] is a initial space in the addess name]
    neigh = ' '.join([n.capitalize() for n in city_neigh[2:]])
    final_address = ' '.join([street, houseN]) + ', ' + ', '.join([neigh, city])
    final_address = final_address.replace('str ', 'straße ').replace(' ,', ',')
    # print(f'Simplified address: "{address}" to "{final_address}"')
    return final_address.strip().replace('  ', ' ')

if __name__ == "__main__":

    simplify_address('darsr xsdd 44, trzc dhhgfhg')
