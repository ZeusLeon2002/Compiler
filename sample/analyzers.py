def block_comment(code, position, line_count):
    token = code[position]
    position += 1
    if code[position] == '*':
        token += code[position]
        position += 1
        result = "Block comment"
        while position < len(code):
            if code[position] == '*' and code[position + 1] == '/':
                token += code[position] + code[position + 1]
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
                position += 1
                line_count += 1
                break
            else:
                token += code[position]
                position += 1
    return position, result, token, line_count

def preprocessor(code, position, line_count, dictionary):
    token = code[position]
    position += 1
    if code[position].isalpha():
        token += code[position]
        position += 1
        while position < len(code):
            if code[position] == '\n':
                position += 1
                line_count += 1  
                break
            elif code[position].isspace():
                token += code[position]
                position += 1   
                break
            else:
                token += code[position]
                position += 1
        if token in dictionary["preprocessor_directives"]:
            result = "Preprocessor directive"
        else:
            result = "Unknown preprocessor directive"              
    return position, result, token, line_count

def keyword_or_identifier(code, position, line_count, dictionary):
    token = code[position]
    position += 1
    while position < len(code):
        if code[position].isalnum() or code[position] == "_":
            token += code[position]
            position += 1
        elif code[position] == '\n':
            position += 1
            line_count += 1
            break    
        elif code[position].isspace():
            position += 1
            break
    for category, keywords in dictionary["keywords"].items():
        if token in keywords:
            result = "Keyword of " + category
        else:
            result = "Identifier"    
    return position, result, token, line_count