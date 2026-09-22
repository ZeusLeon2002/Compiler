import json

def get_dictionary():
    with open("docs/dictionary.json", "r") as f:
        dictionary = json.load(f)
    return dictionary

dictionary = get_dictionary()

def block_comment(code, position, line_count):
    
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

        else:
            break

    result = "identifier"
    category = None

    for category_name, keywords in dictionary["keywords"].items():

        if token in keywords:
            result = "keyword"
            category = category_name
            break

    token_data = {
        "token": token,
        "type": result,
        "category": category,
        "subcategory": None,
        "line": line_count
    }

    return position, line_count, token_data

def number(code, position, line_count, error_count):
    token = code[position]
    position += 1
    result = "Natural number"
    error = False
    while position < len(code):
        if code[position].isdigit():
            token += code[position]
            position += 1
        elif code[position] == '.':
            token += code[position]
            position += 1
            result = "Real number"
            while position < len(code):
                if code[position].isdigit():
                    token += code[position]
                    position += 1
                elif code[position] == '.':
                    token += code[position]
                    position += 1
                    error = True
                elif code[position] == '\n':
                    break
                elif code[position] == ' ' or code[position] == '\t':
                    break
                else:
                    error = True
                    break
        elif code[position] == '\n':
            position += 1
            line_count += 1
            break
        elif code[position] == ' ' or code[position] == '\t':
            position += 1
            break    
        else:
            token += code[position]
            position += 1
            error = True
    if error is True:
        error_count += 1
        result = "Invalid number"        
            
    return position, result, token, line_count, error_count

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
            line_count += 1
            position += 1
            error = True
            break
        
        else:
            token += code[position]
            position += 1
            
    if error is True:
        result = "Invalid string"
        error_count += 1
        
    return position, result, token, line_count, error_count


def is_operator(code, position):
    for category, symbols in dictionary["operators"].items():
        if code[position] in symbols:
            return True
        else:
            is_symbol(code, position, dictionary)
            
def is_symbol(code, position, dictionary):
    for category, symbols in dictionary["symbols"].items():
        if code[position] in symbols:
            return True
    return False

def found_operator(code, position, dictionary, line_count, error_count):
    token = code[position]
    position += 1
    error = False
    while position < len(code):
        if code[position] == '\n':
            line_count += 1
            position += 1
            break
        elif code[position] == ' ' or code[position] == '\t':
            position += 1
            break
        else:
            token += code[position]
            position += 1
    for category, operators in dictionary["operators"].items():
        if token in operators:
            result = category + " operator"
            break
        else:
            result = "Invalid entry"
            error = True
    if error is True:
        error_count += 1        
    return result,position, token, line_count, error_count
        
def found_symbol(code, position, error_count, line_count):
    token = code[position]
    position += 1
    error = False
    while position < len(code):
        if code[position] == '\n':
            line_count += 1
            position += 1
            break
        elif code[position] == ' ' or code[position] == '\t':
            position += 1
            break
        else:
            token += code[position]
            position += 1
    for category, symbols in dictionary["symbols"].items():
        if token in symbols:
            result = category + " symbols"
            break
        else:
            result = "Invalid entry"
            error = True
    if error is True:
        error_count += 1    
    return result,position, token, line_count, error_count