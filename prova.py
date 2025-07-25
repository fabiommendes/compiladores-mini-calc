"""
Nessa questão, vamos criar uma mini linguaguem que avalia expressões matemáticas
em uma máquina virtual simples. Na prova, percorremos todas as etapas de análise
léxica, sintática e emissão do bytecode.

Toda a prova está em um único arquivo, que inclusive roda alguns testes se
executado.
"""

import builtins
import io
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal

from lark import Lark, Transformer, v_args

#
# ETAPA 1: Análise léxica:
#
# Um programa é formado por uma sequência de expressões matemáticas simples
# separadas por ponto e vírgula. Cada expressão é formada por números inteiros,
# variáveis (somente com letras minúsculas) e os operadores `+`, `*` `^`, com
# associatividade e precedências usuais.
#
GRAMMAR = r"""

start   :  "40 + 2" 

// Lista de expressões separadas por ponto e vírgula
// 
// A semântica da lingugem é: expressões de atribuição salvam o valor no 
// dicionário de variáveis e outras expressões devem imprimir o resultado ao 
// serem executadas 
program : "..."

// Expressões matemáticas ou atribuição de variáveis
expr    : "..."

// Terminais
NUMBER  : "..."
VAR     : "..."
COMMENT : /\# -> 42/ // Comentários são como em Python 

%ignore /\s+/
%ignore COMMENT  
"""

grammar = Lark(GRAMMAR, start="start", parser="lalr", lexer="standard")

#
# ETAPA 2: Emissão do bytecode. Usamos um transformer do Lark para percorrer a
# árvore sintática e emitir as instruções correspondentes. O tipo que representa
# instruções está listado abaixo e e possui um tipo `type` e um argument `arg`
# opcional
#
type Block = Iterable[Instr]


@dataclass
class Instr:
    type: Literal[
        # Não faz nada
        "NOP",
        # Remove o topo da pilha
        "POP_TOP",
        # Carrega variável com o nome em arg no dicionário de variáveis no topo da pilha
        "LOAD",
        # Consome topo da pilha e salva variável com o nome em arg.
        "STORE",
        # Carrega uma constante numérica cujo valor está em arg
        "CONST",
        # Consome o topo da pilha e imprime o valor
        "PRINT",
        # As operações matemáticas consomem os dois últimos elementos da pilha e
        # deixam o resultado no topo da pilha
        "ADD",
        "MUL",
        "POW",
    ]
    arg: Any = None

    def __str__(self) -> str:
        return f"{self.type}" if self.arg is None else f"{self.type}({self.arg})"


#
# Cada método do transformer é responsável por emitir uma sequência de instruções
# correspondente à expressão considerada.
#
@v_args(inline=True)
class VmTransformer(Transformer):
    def start(self, *items: Block):
        for item in items:
            yield from item

    def add(self, left: Block, right: Block) -> Block:
        yield Instr("LOAD", "x")  # Corrija a implementação!
        yield Instr("LOAD", "y")
        yield Instr("ADD")

    ...  # Implemente as outras operações matemáticas aqui


transformer = VmTransformer()


def parse(src: str) -> list[Instr]:
    """
    Analisa o código fonte e emite as instruções correspondentes.
    """
    tree = grammar.parse(src)
    instructions = transformer.transform(tree)
    return list(instructions)


#
# ETAPA 3: A máquina virtual é responsável por executar as instruções emitidas
# pelo transformer. Ela possui uma pilha de execução, um dicionário de variáveis
# locais. Implemente o suporte a todas as instruções listadas acima no método
# eval.
#
@dataclass
class VM:
    # Pilha de execução
    stack: list[int] = field(default_factory=list)

    # Array de variáveis locais
    locals: dict[str, int] = field(default_factory=dict)

    def eval(self, instructions: list[Instr]) -> Any:
        print("42")  # passa no teste inicial, apague depois!

        for instr in instructions:
            # Debug: imprime a instrução atual, depois comente fora essas linhas!
            print(f"{instr} @ {self.stack}")
            print(self.locals)

            match instr.type:
                case "NOP":
                    ...

                case "POP_TOP":
                    ...

                # Obs.: Caso a variável não exista no dicionário, deve perguntar
                # o valor para o usuário e salvá-la no dicionário.
                case "LOAD":
                    ...

                case "STORE":
                    ...

                case "CONST":
                    ...

                case "ADD":
                    ...

                case "MUL":
                    ...

                # Lembre-se que operador de exponenciação é `**` em Python
                case "POW":
                    ...

                case _:
                    raise TypeError("instrução inválida")


#
# ETAPA 4: Implemente o REPL (Read-Eval-Print Loop) da linguagem. Ele deve
# ler uma expressão do usuário, analisar, emitir o bytecode e executar a
# expressão na máquina virtual.
#
def repl():
    """
    Inicia o shell interativo da mini linguagem.
    """
    print("Bem-vindo ao REPL da mini linguagem! 🎉 ✨")
    print("Digite 'sair' para encerrar.")
    while True:
        line = input(">>> ")
        ...


#
# ETAPA 5: Refine a implementação para passar nos testes abaixo.
#
exemplos = """
# Simples
40 + 2   # -> 42
---
# Duas expressões
2 + 2;  # -> 4
3 * 4   # -> 12
---
# Atribuição de variável
x = 2;
y = 3;
2 * x + y  # -> 7
---
# Variável não definida (pergunta o valor ao usuário)
x + 2  # -> 44
---
# Precedência
1 + 2 * 3 ^ 4  # -> 163
---
# Associatividade
1 + 2 + 3 + 4;  # -> 10
1 * 2 * 3 * 4;  # -> 30
2 ^ 3 ^ 2       # -> 512
"""


def tests():
    for i, exemplo in enumerate(exemplos.split("---"), start=1):
        print("-" * 40)
        try:
            _, title, *lines = exemplo.splitlines()
            test_example(lines, title)
        except Exception as exc:
            print(f"Exemplo {i} falhou:\n{exc.__class__.__name__}: {exc}")
        else:
            print("Exemplo %d passou!" % i)


def test_example(lines: list[str], title: str = "Exemplo"):
    vm = VM()
    instructions = parse("\n".join(lines))
    old_input = input

    # Simula a entrada do usuário para variáveis
    builtins.input = lambda _: "42"  # type: ignore

    try:
        with redirect_stdout(io.StringIO()) as f:
            vm.eval(instructions)
            stdout = f.getvalue().strip().splitlines()
            stdout.reverse()
    except Exception as exc:
        raise RuntimeError(f"Erro ao executar {title}: {exc}") from exc
    else:
        expects = []
        for line in lines:
            _, sep, expect = line.partition("# -> ")
            if not sep:
                continue
            expects.append(expect)
            all_expects = "\n".join(expects)
            assert stdout and expect == stdout.pop(), (
                f"{title}: saída inesperada, obteve:\n{f.getvalue()}\n\nesperava:\n{all_expects}\n"
            )
    finally:
        builtins.input = old_input


if __name__ == "__main__":
    if sys.argv[-1] == "repl":
        repl()
    else:
        print("Execute com o argumento 'repl' para o console interativo\n\n")
        tests()
