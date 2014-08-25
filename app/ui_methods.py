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