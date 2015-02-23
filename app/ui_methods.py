# Just for ordinalizing the number of district
def ordinal(numb):
    if type(numb) is str:
        numb = int(float(numb))

    if numb < 20: #determining suffix for < 20
        if numb == 1: 
            suffix = 'st'
        elif numb == 2:
            suffix = 'nd'
        elif numb == 3:
            suffix = 'rd'
        else:
            suffix = 'th'  
    else:   #determining suffix for > 20
        tens = str(numb)
        tens = tens[-2]
        unit = str(numb)
        unit = unit[-1]
        if tens == "1":
           suffix = "th"
        else:
            if unit == "1": 
                suffix = 'st'
            elif unit == "2":
                suffix = 'nd'
            elif unit == "3":
                suffix = 'rd'
            else:
                suffix = 'th'
    return str(numb)+ suffix


def list_to_comma_delimited_string(list_arg):
    """
    Takes a list and turns into comma-delimited string.
    Used for turning Group.invited_emails into correct form for template display.

    Args: 
      list: A list, ex: ["alex@usv.com", "bob@usv.com"] or Group.users

    Returns
      A string , ex: "alex@usv.com, bob@usv.com"
      """
    long_string = ""
    for item in list_arg:
        long_string += str(item) + ", "

    long_string = long_string[0:-2] # Remove last ", "
    return long_string

def get_domain(email):
        """
        Returns just the domain name of an email address
        Ex: reply.craigslist.com from foo@reply.craigslist.com
        """
        return email.split('@')[1]

def email_obscure(email):
    """
    Obscures an email address

    Args: 
      email: A string, ex: testcase@alexanderpease.com

    Returns
      A string , ex: t*******@alexanderpease.com
      """
    first_letter = email[0]
    string_split = email.split('@')
    obscured = ""
    while len(obscured) < len(string_split[0])-1:
      obscured = obscured + "*"

    return first_letter + obscured + "@" + string_split[1]

def truncate(string, length=40, ellipses=True):
    """ Truncates strings for formatting """
    if len(string)>length:
        string = string[0:length]
        if ellipses:
            string = string + "..."
    return string


def encode(text):
    """
    For printing unicode characters
    """
    return text.encode('utf-8')


def clean_name(name):
    """
    Same as JS in search.html. Turns "Ali, Nora [dfgdg]" into "Nora Ali"

    Returns a string
    """
    name = name.title()
    # Change "last, first" to "first last"
    if ', ' in name:
        char_index = name.index(', ')
        name = name[char_index+2:] + ' ' +  name[0:char_index]
    if '[' in name and ']' in name:
        if ' [' in name:
            char_index = name.index(' [')
        else:
            char_index = name.index('[')
        char_index2 = name.index(']')
        name = name[0:char_index] + name[char_index2+1:]
    if '<' in name and '>' in name:
        if ' <' in name:
            char_index = name.index(' <')
        else:
            char_index = name.index('<')
        char_index2 = name.index('>')
        name = name[0:char_index] + name[char_index2+1:]

    return name