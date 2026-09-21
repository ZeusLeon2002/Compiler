def block_comment(code, position, line_count, dictionary):
    token = code[position]
    position += 1
    if code[position] == '*':
        token += code[position]
        position += 1
        result = "Block comment"
        while position < len(code):
            if code[position:position+2] == "*/":
                token += code[position:position+2]
                position += 2
                break
            if code[position] == '\n':
                token += "\\n"
                position += 1
                line_count += 1
            else:
                token += code[position]
                position += 1  
    elif code[position] == '/':
        token += code[position]
        position += 1
        result = "Line comment"
        while position < len(code):
            if code[position] == '\n':
                break
            else:
                token += code[position]
                position += 1
    else:
        is_operator(code, position, dictionary)
    return position, result, token, line_count

def preprocessor(code, position, line_count, dictionary, error_count):
    token = code[position]
    position += 1
    error = False
    while position < len(code):
        if code[position] == '\n':
            position += 1
            line_count += 1  
            break
        elif code[position].isspace():
            token += code[position]
            position += 1   
            break
        elif code[position].isalpha():
            token += code[position]
            position += 1
        else:
            token += code[position]
            position += 1
            error = True
    if error is True:
        result = "Invalid preprocessor directive"
        error_count += 1    
    else:       
        if token in dictionary["preprocessor_directive"]:
            result = "Preprocessor directive"
        else:
            result = "Unknown preprocessor directive"
            error_count += 1                   
    return position, result, token, line_count, error_count

def keyword_or_identifier(code, position, line_count, dictionary, error_count):
    token = code[position]
    position += 1
    error = False
    while position < len(code):
        if code[position].isalpha() or code[position].isdigit() or code[position] == "_":
            token += code[position]
            position += 1 
        elif code[position] == '\n':
            line_count += 1
            position += 1
            break    
        elif code[position] == ' ' or code[position] == '\t':
            position += 1
            break
        else:
            token += code[position]
            error = True
            position += 1
    if error is False:    
        for category, keywords in dictionary["keywords"].items():
            if token in keywords:
                result = "Keyword of " + category
                break
            else:
                result = "Identifier"
    else:
        result = "Invalid identifier"
        error_count += 1
    return position, result, token, line_count, error_count

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
                    line_count += 1
                    break
                elif code[position] == ' ' or code[position] == '\t':
                    position += 1
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
    result = "String"
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


def is_operator(code, position, dictionary):
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
        
def found_symbol(code, position, dictionary, error_count, line_count):
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