"""Units Util Module."""
import re
import math
import copy

# Constant maps name to symbol
NAME_TO_SYMBOL = {}
NAME_TO_SYMBOL['minute'] = 'min'
NAME_TO_SYMBOL['hour'] = 'h'
NAME_TO_SYMBOL['day'] = 'd'
NAME_TO_SYMBOL['degree'] = '\xc2\xb0'
NAME_TO_SYMBOL['second'] = '"'
NAME_TO_SYMBOL['hectare'] = 'ha'
NAME_TO_SYMBOL['litre'] = 'l'
NAME_TO_SYMBOL['tonne'] = 't'

# Constant maps symbol to si units
# Naming collisions for d with day, degree, second, rad
# Naming collisions for h with ha, hectare

UNIT_SYMBOL_TO_SI_CONVERSION = {}
UNIT_SYMBOL_TO_SI_CONVERSION["min"] = {'type': 'time', 'si_name': 's', "factor": 60.0}
UNIT_SYMBOL_TO_SI_CONVERSION["h"] = {'type': 'time', 'si_name': 's', "factor": 3600.0}
UNIT_SYMBOL_TO_SI_CONVERSION["d"] = {'type': 'time', 'si_name': 's', "factor": 86400.0}
UNIT_SYMBOL_TO_SI_CONVERSION['\xc2\xb0'] = {'type': 'Plane angle ', 'si_name': 'rad', "factor": (math.pi/180)}
UNIT_SYMBOL_TO_SI_CONVERSION["'"] = {'type': 'Plane angle', 'si_name': 'rad', "factor": (math.pi/10800)}
UNIT_SYMBOL_TO_SI_CONVERSION['"'] = {'type': 'Plane angle', 'si_name': 'rad', "factor": (math.pi/648000)}
UNIT_SYMBOL_TO_SI_CONVERSION['ha'] = {'type': 'area', 'si_name': 'm*m', "factor": math.pow(10, 4)}
UNIT_SYMBOL_TO_SI_CONVERSION['l'] = {'type': 'volume', 'si_name': 'm*m*m', "factor": math.pow(10, -3)}
UNIT_SYMBOL_TO_SI_CONVERSION['t'] = {'type': 'mass', 'si_name': 'kg', "factor": math.pow(10, 3)}
SI_UNITS = set(('s', 'rad', 'm', 'kg'))


def check_valid_units_string(none_si_units):
    """"Check to see if input units is valid.

    :param none_si_units: Pre converted units string.
    :returns: Boolean if string is valid.
    """
    valid_paranthesis = check_paransthesis(none_si_units)
    valid_operators = check_valid_operators(none_si_units)
    valid_name_symbols = check_valid_name_symbol(none_si_units)
    return valid_paranthesis and valid_operators and valid_name_symbols


def check_valid_operators(none_si_units):
    """Check operators are valid according to symbol and position.

    :param none_si_units: Pre converted units string.
    :returns: boolean stating if operators contained are valid.
    """

    # List of invalids and valids
    INVALID_OPERATORS = ['+', '-', '^', '!', '%', 'log', '=', '|']
    VALID_OPERATORS = ['/', '*']

    # Check if invalids in units string
    only_valid_operators = True
    for opt in INVALID_OPERATORS:
        if opt in none_si_units:
            only_valid_operators = False

    # Check for trailing or beginning operators
    only_valid_operators = none_si_units[0] not in VALID_OPERATORS
    only_valid_operators = none_si_units[-1] not in VALID_OPERATORS
    return only_valid_operators


def check_paransthesis(none_si_units):
    """Check paranthesis are valid according to placement.

    :param none_si_units: Pre converted units string.
    :returns: boolean if paranthesis in string are valid.
    """

    # Check paranthesis count
    valid_paranthesis_count = none_si_units.count(")") == none_si_units.count("(")
    # Check paranthesis aren't empty
    no_empty_paranthesis = "()" not in none_si_units

    # Check paranthesis palacement relative to operator
    invalid_operator_paran = ["(/", "/)", "(*", "*)"]
    valid_operator_paranthesis_position = all(placement not in none_si_units for placement in invalid_operator_paran)

    # Check no name or symbol next to paranthesis e.g. "(, )second
    valid_name_symbol_paran_palacement = True
    names = NAME_TO_SYMBOL.keys()
    for name in names:
        name_parans = [name + "(", ")" + name]
        if any(name_paran in none_si_units for name_paran in name_parans):
            valid_name_symbol_paran_palacement = False

    symbols = UNIT_SYMBOL_TO_SI_CONVERSION.keys()
    for symbol in symbols:
        symbol_parans = [symbol + "(", ")" + symbol]
        if any(symbol_paran in none_si_units for symbol_paran in symbol_parans):
            valid_name_symbol_paran_palacement = False

    return valid_paranthesis_count and no_empty_paranthesis and valid_operator_paranthesis_position and valid_name_symbol_paran_palacement


def convert_to_si(none_si_units):
    """Converts input to SI units.

    :param none_si_units: Pre converted units string.
    :returns: returns Dictionary of unit_name and multiplication_factor
    """
    # Get si units name
    unit_name = convert_none_si_to_si(none_si_units)
    # Get array of string with nested arrays for parantheses
    unit_operator_array = get_nested_arrays_accodring_to_parans(none_si_units)

    # Seperate numbers from string and get multiplication_factor
    number_unit_array = seperate_numbers_from_array(unit_operator_array)
    multiplication_factor = get_multiplicitive_factor(number_unit_array)

    if multiplication_factor == "Invalid Query parameter":
        return {'status': 400, 'error': multiplication_factor}
    else:
        return {'unit_name': unit_name, 'multiplication_factor': multiplication_factor}


def get_nested_arrays_accodring_to_parans(none_si_units, i=0):
    """Nest arrays according to parantheses.

    :param none_si_units: Pre converted units
    :returns: Array of strings and nested arrays according to parantheses
    :example: '(min*min)/(L*(rad*ha))' => [['min', '*', 'min'], '/', ['l', '*', ['rad', '*', 'ha']]]
    """
    if len(none_si_units) < i:
        return

    # Loop and recurse to nest parantheses in arrays
    current_string = ""
    unit_operator_array = []
    while i < len(none_si_units):
        char = none_si_units[i]
        if char == "(":  # Start nested Array
            current_string = add_current_string_to_unit_array(current_string, unit_operator_array)
            sub_array, i = (get_nested_arrays_accodring_to_parans(none_si_units, i=i + 1))
            unit_operator_array.append(sub_array)
        elif char == ")":  # End nested array
            current_string = add_current_string_to_unit_array(current_string, unit_operator_array)
            return [unit_operator_array, i]
        elif char in ['*', '/']:  # Append current_string and then operator
            current_string = add_current_string_to_unit_array(current_string, unit_operator_array)
            unit_operator_array.append(none_si_units[i])
        else:
            current_string += none_si_units[i]
        i += 1

    # Add current_string if not empty
    add_current_string_to_unit_array(current_string, unit_operator_array)
    return unit_operator_array


def add_current_string_to_unit_array(current_string, array):
    """Append array if current_string is not empty."""
    if current_string is not "":
        array.append(current_string)

    return ""


def get_multiplicitive_factor(unit_operator_array):
    """Return multiplication_factor to si."""
    product = 1.0
    current_operator = "*"
    for el in unit_operator_array:
        factor = 1.0
        if type(el) is list:
            factor = get_multiplicitive_factor(el)
        elif type(el) is float:
            factor = el
        elif el in ['*', '/']:
            current_operator = el
        else:
            if el not in SI_UNITS:
                symbol = get_unit_symbol(el)
                try:
                    factor = UNIT_SYMBOL_TO_SI_CONVERSION[symbol]['factor']
                except:
                    return "Invalid Query parameter"
            else:
                factor = 1.0

        product = implement_current_operator(current_operator, factor, product)

    return round(product, 14)  # return product rounded to 14 decimal places


def implement_current_operator(operator, factor, product):
    """Multiply product according to operator."""
    if operator == '/':
        product *= math.pow(factor, -1)
    else:
        product *= factor

    return product


def get_unit_symbol(el):
    """Return if element is symbol."""
    if el in NAME_TO_SYMBOL:
        return NAME_TO_SYMBOL[el]
    elif el in UNIT_SYMBOL_TO_SI_CONVERSION:
        return el


def seperate_numbers_from_array(unit_operator_array):
    """Seperate the numerical values from a string.

    :example: ['100min'] => [100, '*', 'min']
    """
    number_unit_array = []
    for idx, el in enumerate(unit_operator_array):
        if type(el) is list:
            sub_array = seperate_numbers_from_array(el)
            number_unit_array.append(sub_array)
        elif any(char.isdigit() for char in el):
            # Extract numbers from string element
            num = re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", el)[0]

            # Remove number and append number_unit_array
            no_number_string = el.replace(num, "")
            number_unit_array.append(float(num))

            # Only add string and * if needed
            if idx < len(unit_operator_array) - 1 and unit_operator_array[idx + 1] is not '*':
                number_unit_array.append("*")
            if no_number_string is not "":
                number_unit_array.append(no_number_string)
        else:
            number_unit_array.append(el)

    return number_unit_array


def convert_none_si_to_si(none_si_units):
    """Converts input string to SI symbols.

    :param none_si_units: Pre converted units
    :returns: string of si units
    """

    # Replace string with none si symbol representation
    names = NAME_TO_SYMBOL.keys()
    for name in names:
        if name in none_si_units:
            none_si_units = none_si_units.replace(name, NAME_TO_SYMBOL[name])

    # Replace symbol with si unit representation and save to new string
    si_units = copy.copy(none_si_units)
    symbols = UNIT_SYMBOL_TO_SI_CONVERSION.keys()
    for symbol in symbols:
        if symbol in si_units and symbol not in ['d', 'h']:
            si_units = si_units.replace(symbol, UNIT_SYMBOL_TO_SI_CONVERSION[symbol]['si_name'])

    # Remove numbers from string
    numbers = re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", none_si_units)
    for num in numbers:
        string_num_variations = [num + '/', num + '*', '*' + num, '/' + num, num]
        for variation in string_num_variations:
            if variation in si_units:
                si_units = si_units.replace(variation, "")

    if 'd' in si_units:
        d_collisions = ['rad', 'degree']
        si_units = check_collision('d', d_collisions, si_units)

    if 'h' in si_units:
        h_collisions = ['ha', 'hour']
        si_units = check_collision('h', h_collisions, si_units)

    return si_units


def check_collision(symbol, collisions, si_units):
    """Check if any collision string are in si_units string."""
    if not any(collision in si_units for collision in collisions):
        UNIT_SYMBOL_TO_SI_CONVERSION[symbol]['si_name']
        si_units = si_units.replace(symbol, UNIT_SYMBOL_TO_SI_CONVERSION[symbol]['si_name'])
        return si_units
    else:
        return si_units


def check_valid_name_symbol(none_si_units):
    """Check units are valid according to symbol and name.

    :param none_si_units: Pre converted units string.
    :returns: boolean stating if name/symbol in valid position
    :example: invalid example=> minminrad
              valid min*min*rad
    """
    # varaibles
    none_si_units_copy = copy.copy(none_si_units)
    valid_name_symbol_palacement = True

    # map names to symbols to avoid collisions
    names = NAME_TO_SYMBOL.keys()
    for name in names:
        if name in none_si_units_copy and name not in ['d', 'h']:
            none_si_units_copy = none_si_units_copy.replace(name, NAME_TO_SYMBOL[name])

    symbols = UNIT_SYMBOL_TO_SI_CONVERSION.keys()

    # Check if symbol in string has operator infront or behind it
    for symbol in symbols:
        if symbol == none_si_units_copy:
            valid_name_symbol_palacement = True
        elif symbol in none_si_units_copy and symbol not in ['d', 'h']:
            symbol_variations = [symbol + "*", "*" + symbol, symbol + "/", "/" + symbol]
            if not any(symbol_variation in none_si_units_copy for symbol_variation in symbol_variations):
                valid_name_symbol_palacement = False

    # Check if string contains any symbols
    valid_name_symbol_palacement = any(symbol in none_si_units_copy for symbol in symbols)
    return valid_name_symbol_palacement


none_si_units = '(min*min)/(l*(rad*ha))'
print "check_valid_units_string: ", check_valid_units_string(none_si_units) is True  # True
print 'convert_none_si_to_si:', convert_none_si_to_si(none_si_units) == '(s*s)/(m*m*m*(rad*m*m))'  # True
print 'convert_none_si_to_si:', convert_none_si_to_si(none_si_units) == '(s*s)/(m*m*m*(rad*m*m))'  # True
print 'get_nested_arrays_accodring_to_parans:', get_nested_arrays_accodring_to_parans(none_si_units) == [['min', '*', 'min'], '/', ['l', '*', ['rad', '*', 'ha']]]  # True
print 'get_multiplicitive_factor:', get_multiplicitive_factor(get_nested_arrays_accodring_to_parans(none_si_units)) == 360  # True
