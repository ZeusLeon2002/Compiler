import json

def get_dictionary():
    with open("docs/dictionary.json", "r") as f:
        dictionary = json.load(f)
    return dictionary

dictionary = get_dictionary()

def block_comment(code, position, line_count):
    token = ""

    if position < len(code) and code[position+1] == '*':
        token += code[position:position+2]
        position += 2
        
        while position < len(code):
            
            if code[position:position+2] == "*/":
                token += code[position:position+2]
                position += 2
                break
            
            if code[position] == '\n':
                token += "\n"
                position += 1
                line_count += 1
                
            else:
                token += code[position]
                position += 1  
                
        token_data = {
            "token": token,
            "type": "comments",
            "category": "multi_line",
            "subcategory": None,
            "line": line_count
        }
            
    elif position < len(code) and code[position+1] == '/':        
        token += code[position:position+2]
        position += 2
        
        while position < len(code):
            
            if code[position] == '\n':
                break
            
            else:
                token += code[position]
                position += 1
                
        token_data = {
            "token": token,
            "type": "comments",
            "category": "single_line",
            "subcategory": None,
            "line": line_count
        }      
         
    else:
        return False, position, line_count, token_data
        
    return True, position, line_count, token_data

def preprocessor(code, position, line_count, error_count):

    token = code[position]
    position += 1
    error = False

    while position < len(code):

        if code[position] == '\n':
            break

        elif code[position].isspace():
            break

        elif code[position] == '#':
            token += 1
            position += 1
            break
            
        elif code[position].isalpha():
            token += code[position]
            position += 1

        else:
            token += code[position]
            position += 1
            error = True

    if error:
        result = "Invalid preprocessor directive"
        category = "invalid"
        error_count += 1
        
    elif token == "##":
        result = "token_pasting"
        category = "preprocessor_operators"

    elif token in dictionary["preprocessor_directive"]:
        result = "preprocessor_directive"
        category = "directive"

    else:
        result = "Invalid preprocessor directive"
        category = "invalid"
        error_count += 1

    token_data = {
        "token": token,
        "type": result,
        "category": category,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, error_count, token_data

def keyword_or_identifier(code, position, line_count):
    token = code[position]
    position += 1
    
    while position < len(code):

        if code[position].isalnum() or code[position] == "_":
            token += code[position]
            position += 1
            result = "identifier"
            category = None

        elif code[position:position+2] == ".h":
            token += code[position:position+2]
            position += 2
            result = "library"
            category = None
            break
            
        else:
            result = "identifier"
            category = None
            break

    for category_name, keywords in dictionary["keywords"].items():

        if token in keywords:
            result = "keyword"
            category = category_name
            break

    for category_name, library in dictionary["standard_library"].items():
    
        if token in library:
            result = "library function"
            category = category_name + " library"
            break
                    
    token_data = {
        "token": token,
        "type": result,
        "category": category,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, token_data

def char(code, position, line_count, error_count):
    token = code[position]
    position += 1
    error = False

    if position >= len(code):
        error = True
    elif code[position] == '\\':
        token += code[position]
        position += 1

        if position >= len(code):
            error = True
        else:
            token += code[position]
            position += 1
    else:
        token += code[position]
        position += 1

    if not error:
        if position >= len(code) or code[position] != "'":
            error = True
        else:
            token += code[position]
            position += 1

    if error:
        result = "invalid_char"
        category = "invalid"
        error_count += 1
    else:
        result = "char"
        category = "character"

    token_data = {
        "token": token,
        "type": result,
        "category": category,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, error_count, token_data

def number(code, position, line_count, error_count):

    token = ""
    error = False
    result = "natural_number"

    while position < len(code) and code[position].isdigit():
        token += code[position]
        position += 1

    if position < len(code) and code[position] == '.':
        result = "real_number"
        token += code[position]
        position += 1

        if position >= len(code) or not code[position].isdigit():
            error = True

        while position < len(code) and code[position].isdigit():
            token += code[position]
            position += 1

    # Detectar un segundo punto
    if position < len(code) and code[position] == '.':
        error = True

        while position < len(code) and code[position] == '.':
            token += code[position]
            position += 1

    if error:
        result = "invalid_number"
        error_count += 1

    token_data = {
        "token": token,
        "type": "number",
        "category": result,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, error_count, token_data

def strings(code, position, line_count, error_count):

    token = code[position]
    position += 1
    error = False

    while position < len(code):

        if code[position] == '"':
            token += code[position]
            position += 1
            break

        elif code[position] == '\n':
            error = True
            break

        else:
            token += code[position]
            position += 1

    else:
        error = True

    if error:
        result = "invalid_string"
        error_count += 1
    else:
        result = "string"

    token_data = {
        "token": token,
        "type": result,
        "category": "string",
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, error_count, token_data

def found_operator(code, position, line_count, error_count):

    token = None
    category = None

    for category_name, operators in dictionary["operators"].items():

        if code[position:position+3] in operators:
            token = code[position:position+3]
            category = category_name
            position += 3
            break

    if token is None:

        for category_name, operators in dictionary["operators"].items():

            if code[position:position+2] in operators:
                token = code[position:position+2]
                category = category_name
                position += 2
                break

    if token is None:

        for category_name, operators in dictionary["operators"].items():

            if code[position] in operators:
                token = code[position]
                category = category_name
                position += 1
                break

    if token is None:

        token = code[position]
        position += 1
        result = "invalid_operator"
        error_count += 1
        category = None

    else:
        result = "operator"

    token_data = {
        "token": token,
        "type": result,
        "category": category,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, error_count, token_data
        
def found_symbol(code, position, line_count, error_count):

    token = None
    category = None

    for category_name, symbols in dictionary["symbols"].items():

        if code[position:position+3] in symbols:
            token = code[position:position+3]
            category = category_name
            position += 3
            break

    if token is None:

        for category_name, symbols in dictionary["symbols"].items():

            if code[position:position+2] in symbols:
                token = code[position:position+2]
                category = category_name
                position += 2
                break

    if token is None:

        for category_name, symbols in dictionary["symbols"].items():

            if code[position] in symbols:
                token = code[position]
                category = category_name
                position += 1
                break

    if token is None:

        token = code[position]
        position += 1
        result = "invalid_symbol"
        error_count += 1

    else:
        result = "symbol"

    token_data = {
        "token": token,
        "type": result,
        "category": category,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, error_count, token_data

def is_operator_or_symbol(code, position):
    character = code[position]

    # Revisar operadores
    for operators in dictionary["operators"].values():
        if character in operators:
            return "operator"

    # Revisar símbolos
    for symbols in dictionary["symbols"].values():
        if character in symbols:
            return "symbol"

    return None