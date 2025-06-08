import ply.yacc as yacc
from lexer import tokens

def p_query(p):
    '''query : select_query
             | insert_query
             | update_query
             | delete_query'''
    p[0] = p[1]

def p_select_query(p):
    '''select_query : SELECT select_columns FROM IDENTIFIER where_clause_opt order_by_opt'''
    p[0] = {
        'type': 'select',
        'columns': p[2],
        'table': p[4],
        'where': p[5],
        'order_by': p[6]
    }

def p_select_columns(p):
    '''select_columns : column_list
                     | COUNT LPAREN TIMES RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ['COUNT(*)']

def p_insert_query(p):
    '''insert_query : INSERT INTO IDENTIFIER LPAREN column_list RPAREN VALUES LPAREN value_list RPAREN
                    | INSERT INTO IDENTIFIER VALUES LPAREN value_list RPAREN'''
    if len(p) == 11:
        p[0] = {
            'type': 'insert',
            'table': p[3],
            'columns': p[5],
            'values': p[9]
        }
    else:
        p[0] = {
            'type': 'insert',
            'table': p[3],
            'columns': None,
            'values': p[6]
        }

def p_update_query(p):
    '''update_query : UPDATE IDENTIFIER SET set_list where_clause_opt'''
    p[0] = {
        'type': 'update',
        'table': p[2],
        'set': p[4],
        'where': p[5]
    }

def p_delete_query(p):
    '''delete_query : DELETE FROM IDENTIFIER where_clause_opt'''
    p[0] = {
        'type': 'delete',
        'table': p[3],
        'where': p[4]
    }

def p_set_list(p):
    '''set_list : set_item
               | set_item COMMA set_list'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {**p[1], **p[3]}

def p_set_item(p):
    '''set_item : IDENTIFIER EQ value'''
    p[0] = {p[1]: p[3]}

def p_value_list(p):
    '''value_list : value
                 | value COMMA value_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_column_list(p):
    '''column_list : TIMES
                  | IDENTIFIER
                  | IDENTIFIER COMMA column_list'''
    if len(p) == 2:
        p[0] = ['*'] if p[1] == '*' else [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_where_clause_opt(p):
    '''where_clause_opt : WHERE condition
                        | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_order_by_opt(p):
    '''order_by_opt : ORDER BY order_list
                    | empty'''
    p[0] = p[3] if len(p) == 4 else None

def p_order_list(p):
    '''order_list : order_item
                 | order_item COMMA order_list'''
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

def p_order_item(p):
    '''order_item : IDENTIFIER asc_desc'''
    p[0] = {
        'column': p[1],
        'direction': p[2]
    }

def p_asc_desc(p):
    '''asc_desc : ASC
                | DESC
                | empty'''
    p[0] = p[1] if len(p) > 1 and p[1] is not None else 'ASC'

def p_condition(p):
    '''condition : simple_condition
                | LPAREN condition RPAREN
                | condition AND condition
                | condition OR condition
                | NOT condition'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] == '(':
        p[0] = p[2]
    elif p[2] == 'AND':
        p[0] = {
            'operator': 'AND',
            'left': p[1],
            'right': p[3]
        }
    elif p[2] == 'OR':
        p[0] = {
            'operator': 'OR',
            'left': p[1],
            'right': p[3]
        }
    elif p[1] == 'NOT':
        p[0] = {
            'operator': 'NOT',
            'condition': p[2]
        }

def p_simple_condition(p):
    '''simple_condition : IDENTIFIER operator value'''
    p[0] = {
        'column': p[1],
        'operator': p[2],
        'value': p[3]
    }

def p_operator(p):
    '''operator : EQ
                | NEQ
                | GT
                | LT
                | GE
                | LE'''
    p[0] = p[1]

def p_value(p):
    '''value : NUMBER
             | STRING_LITERAL'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Erro de sintaxe na linha {p.lineno}, token={p.type}, valor={p.value}")
    else:
        print("Erro de sintaxe: fim inesperado da entrada")

parser = yacc.yacc(debug=False)