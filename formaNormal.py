import re


class Nodo:
    def __init__(self, valor, izquierda=None, derecha=None):
        self.valor = valor
        self.izquierda = izquierda
        self.derecha = derecha

    def mostrar(self, nivel=0):
        print("   " * nivel + str(self.valor))
        if self.izquierda:
            self.izquierda.mostrar(nivel + 1)
        if self.derecha:
            self.derecha.mostrar(nivel + 1)
#Operadores
op = [
    '\\neg',
    '\\land',
    '\\lor',
    '\\rightarrow',
    '\\leftrightarrow',
]
PRIORIDAD = {
    '\\neg': 4,
    '\\land': 3,
    '\\lor': 2,
    '\\rightarrow': 1,
    '\\leftrightarrow': 0,
}

TOKEN_REGEX = r'(\\neg|\\land|\\lor|\\rightarrow|\\leftrightarrow|\(|\)|[A-Za-z])'
#Tokenización del string en formato latex
def tokenizar(expr):
    return re.findall(TOKEN_REGEX, expr)

#Algoritmo Shunting yard para expresión infija a postfija
def a_postfijo(tokens):
    output = []
    stack = []
    for token in tokens:
        if token.isalpha():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif token in PRIORIDAD:
            while (stack and stack[-1] in PRIORIDAD and
                   PRIORIDAD[stack[-1]] >= PRIORIDAD[token]):
                output.append(stack.pop())
            stack.append(token)
    while stack:
        output.append(stack.pop())
    return output

#Construye el arbol a partir del stack del shunting yard
def construir_arbol(postfijo):
    stack = []
    for token in postfijo:
        if token.isalpha():
            stack.append(Nodo(token))
        elif token == '\\neg':
            hijo = stack.pop()
            stack.append(Nodo(token, izquierda=hijo))
        else:
            der = stack.pop()
            izq = stack.pop()
            stack.append(Nodo(token, izq, der))
    return stack[0]

#Crea la arbol binario
def latex_a_arbol(expr):
    tokens = tokenizar(expr)
    postfijo = a_postfijo(tokens)
    return construir_arbol(postfijo)

#Eliminación de la implicación
def eliminar_implicaciones(nodo):
    if nodo is None:
        return None
    nodo.izquierda = eliminar_implicaciones(nodo.izquierda)
    nodo.derecha = eliminar_implicaciones(nodo.derecha)

    if nodo.valor == '\\rightarrow':
        return Nodo('\\lor', Nodo('\\neg', izquierda=nodo.izquierda), nodo.derecha)

    return nodo
def eliminar_bicondicionales(nodo):
    if nodo is None:
        return None
    nodo.izquierda = eliminar_bicondicionales(nodo.izquierda)
    nodo.derecha = eliminar_bicondicionales(nodo.derecha)

    if nodo.valor == '\\leftrightarrow':
        izq = Nodo('\\rightarrow', nodo.izquierda, nodo.derecha)
        der = Nodo('\\rightarrow', nodo.derecha, nodo.izquierda)
        return Nodo('\\land', izq, der)

    return nodo
# Ley de Morgan
def empujar_negaciones(nodo):
    if nodo is None:
        return None
    if nodo.valor == '\\neg':
        hijo = empujar_negaciones(nodo.izquierda)
        if hijo.valor == '\\neg':
            return empujar_negaciones(hijo.izquierda)
        elif hijo.valor == '\\land':
            return Nodo('\\lor',
                        empujar_negaciones(Nodo('\\neg', izquierda=hijo.izquierda)),
                        empujar_negaciones(Nodo('\\neg', izquierda=hijo.derecha)))
        elif hijo.valor == '\\lor':
            return Nodo('\\land',
                        empujar_negaciones(Nodo('\\neg', izquierda=hijo.izquierda)),
                        empujar_negaciones(Nodo('\\neg', izquierda=hijo.derecha)))
        else:
            return Nodo('\\neg', izquierda=hijo)
    nodo.izquierda = empujar_negaciones(nodo.izquierda)
    nodo.derecha = empujar_negaciones(nodo.derecha)
    return nodo

# Distribuye el y sobre el o (Distributiva)
def distribuir_y_sobre_o(nodo):
    if nodo is None:
        return None

    nodo.izquierda = distribuir_y_sobre_o(nodo.izquierda)
    nodo.derecha = distribuir_y_sobre_o(nodo.derecha)

    if nodo.valor == '\\land':
        A = nodo.izquierda
        B = nodo.derecha

        if A and A.valor == '\\lor':
            return Nodo('\\lor',
                        distribuir_y_sobre_o(Nodo('\\land', A.izquierda, B)),
                        distribuir_y_sobre_o(Nodo('\\land', A.derecha, B)))
        if B and B.valor == '\\lor':
            return Nodo('\\lor',
                        distribuir_y_sobre_o(Nodo('\\land', A, B.izquierda)),
                        distribuir_y_sobre_o(Nodo('\\land', A, B.derecha)))
    return nodo

#Verifica la satisfacibilidad de la formula
def esSatisfacible(nodo):
    if nodo==None:
        return False
    else:return True

#Convierte a fnd el arbol
def convertir_a_fnd(arbol, original):
    exps = []
    exps.append(("Latex original", arbol_a_latex(arbol)))
    exps.append(("Notación logica",arbol_a_cadena(arbol)))
    arbol = eliminar_bicondicionales(arbol)
    exps.append(("E↔",arbol_a_cadena(arbol)))
    arbol = eliminar_implicaciones(arbol)
    exps.append(("E→",arbol_a_cadena(arbol)))
    arbol = empujar_negaciones(arbol)
    exps.append(("Ley de Morgan",arbol_a_cadena(arbol)))
    arbol = distribuir_y_sobre_o(arbol)
    exps.append(("Distributiva",arbol_a_cadena(arbol)))
    arbol = quitar_redundancias(arbol)
    exps.append(("Idempotencia disyunción y conjunción",arbol_a_cadena(arbol)))
    arbol=quitar_falsos(arbol)
    if esSatisfacible(arbol):
        exps.append(("Eliminación de la contradicción",arbol_a_cadena(arbol)))
        exps.append(("FND Latex", arbol_a_latex(arbol)))  
    else:
        exps.append(("Eliminación de la contradicción","No es satisfacible"))
        exps.append(("FND Latex", "No es satisfacible"))  
      
    
    return exps

#Convierte el arbol a cadena en notación logica
def arbol_a_cadena(nodo):
    if nodo is None:
        return ""
    simbolos = {
        '\\neg': '¬',
        '\\land': '∧',
        '\\lor': '∨',
        '\\rightarrow': '→',
        '\\leftrightarrow': '↔',
    }
    if nodo.valor == '\\neg':
        return f"{simbolos[nodo.valor]}{arbol_a_cadena(nodo.izquierda)}"
    elif nodo.valor in simbolos:
        izq = arbol_a_cadena(nodo.izquierda)
        der = arbol_a_cadena(nodo.derecha)
        return f"({izq} {simbolos[nodo.valor]} {der})"
    else:
        return nodo.valor

#Quita los las contradicciones de la formula
def quitar_falsos(nodo):
    if nodo is None:
        return None

    if nodo.valor == '\\lor':
        # Recorremos las disyunciones y filtramos las que no son contradictorias
        elementos = recolectar_operaciones('\\lor', nodo)
        nuevas_clausulas = []
        for conj in elementos:
            clausula = quitar_contradicciones_en_and(conj)
            if clausula:  # Solo si no es una cláusula completamente falsa
                nuevas_clausulas.append(clausula)

        return reconstruir_operacion('\\lor', nuevas_clausulas)

    return nodo

#Funcion auxiliar, Quita las contradicciones en and
def quitar_contradicciones_en_and(nodo):
    if nodo.valor != '\\land':
        return nodo

    elementos = recolectar_operaciones('\\land', nodo)

    vistos = set()
    negados = set()
    resultado = []

    for e in elementos:
        if e.valor == '\\neg' and e.izquierda:
            nombre = arbol_a_cadena(e.izquierda)
            if nombre in vistos:
                return None  # Contradicción encontrada
            negados.add(nombre)
            resultado.append(e)
        else:
            nombre = arbol_a_cadena(e)
            if nombre in negados:
                return None  # Contradicción encontrada
            vistos.add(nombre)
            resultado.append(e)

    return reconstruir_operacion('\\land', resultado)

#Imprime el arbol en formato latex
def arbol_a_latex(nodo):
    if nodo is None:
        return ""
    if nodo.valor == '\\neg':
        return f"\\neg {arbol_a_latex(nodo.izquierda)}"
    elif nodo.valor in ['\\land', '\\lor', '\\rightarrow', '\\leftrightarrow']:
        izq = arbol_a_latex(nodo.izquierda)
        der = arbol_a_latex(nodo.derecha)
        return f"({izq} {nodo.valor} {der})"
    else:
        return nodo.valor

#Quita las redundancias    
def quitar_redundancias(nodo):
    if nodo is None:
        return None

    nodo.izquierda = quitar_redundancias(nodo.izquierda)
    nodo.derecha = quitar_redundancias(nodo.derecha)

    if nodo.valor in ['\\land', '\\lor']:
        # Si ambos hijos son iguales, quita la redundancia
        if arbol_a_cadena(nodo.izquierda) == arbol_a_cadena(nodo.derecha):
            return nodo.izquierda

        # Si ambos lados son del mismo tipo de operación, podemos combinar
        elementos = recolectar_operaciones(nodo.valor, nodo)
        # Elimina duplicados convertidos en cadena y vuelve a armar el árbol
        únicos = []
        vistos = set()
        for e in elementos:
            cad = arbol_a_cadena(e)
            if cad not in vistos:
                únicos.append(e)
                vistos.add(cad)

        return reconstruir_operacion(nodo.valor, únicos)

    return nodo

#Funcion Auxiliar, recolecta las operaciones
def recolectar_operaciones(operador, nodo):
    if nodo is None:
        return []
    if nodo.valor == operador:
        return recolectar_operaciones(operador, nodo.izquierda) + recolectar_operaciones(operador, nodo.derecha)
    return [nodo]

#Recontruye la operacion
def reconstruir_operacion(operador, elementos):
    if not elementos:
        return None
    if len(elementos) == 1:
        return elementos[0]
    # Armar árbol binario izquierdo
    actual = Nodo(operador, elementos[0], elementos[1])
    for e in elementos[2:]:
        actual = Nodo(operador, actual, e)
    return actual    
def forma_normal(expresion):
    if expresion[0] == "(" and expresion[-1] == ")":
        expresion = expresion[1:-1]
    arbol = latex_a_arbol(expresion)

    fnd = convertir_a_fnd(arbol, expresion)
    return fnd

#Prueba
#expresion = "(A \\leftrightarrow B) \\land C"
#x = forma_normal(expresion)
#print("Fórmula en Forma Normal Disyuntiva:")