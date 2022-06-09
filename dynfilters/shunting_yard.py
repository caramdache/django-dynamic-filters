from django.db.models import Q

# Function that returns value of
# expression after evaluation.
# Adapted from https://www.geeksforgeeks.org/expression-evaluation/
def evaluate(tokens):
    # Function to find precedence 
    # of operators.
    def precedence(op): 
        if op == ' ': return 3 # no-op
        if op == '&': return 2 # AND
        if op == '|': return 1 # OR
        return 0
     
    # Function to perform arithmetic 
    # operations.
    def popAndApplyOp():
        op = ops.pop()

        # no-op
        if op == ' ': return Q()

        b = values.pop()
        a = values.pop()

        # AND | OR
        if op == '&': return a & b
        if op == '|':  return a | b

    # stack to store Q objects.
    values = []

    # stack to store operators.
    ops = []

    for token in tokens:

        # Current token is an opening 
        # brace, push it to 'ops'
        if token.op == '(':
            ops.append(token.op)

        # Current token is a term, push 
        # it to stack for Q objects.
        elif token.op == "-" or token.op == '!':
            values.append(token.as_q())
          
        # Closing brace encountered, 
        # solve entire brace.
        elif token.op == ')':
            while ops and ops[-1] != '(':
                values.append(popAndApplyOp())
            
            # pop opening brace.
            ops.pop()
        
        # Current token is an operator.
        else:
            # While top of 'ops' has same or 
            # greater precedence to current 
            # token, which is an operator.
            # Apply operator on top of 'ops' 
            # to top two elements in values stack.
            while (ops and
                precedence(ops[-1]) >=
                precedence(token.op)):
                        
                values.append(popAndApplyOp())
            
            # Push current token to 'ops'.
            ops.append(token.op)
        
    # Entire expression has been parsed 
    # at this point, apply remaining ops 
    # to remaining values.
    while ops:            
        values.append(popAndApplyOp())

    # Top of 'values' contains result, 
    # return it.
    return values[-1]
