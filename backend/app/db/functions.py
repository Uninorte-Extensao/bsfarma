"""
Compatibilidade de funções de banco entre PostgreSQL e SQLite.

Os models geram a chave primária no próprio banco, com
`server_default=func.gen_random_uuid()` — uma função nativa do PostgreSQL.
A suíte de testes, porém, roda em SQLite em memória (ver tests/conftest.py),
onde essa função não existe: sem o registro abaixo, todo INSERT falha com
"sqlite3.OperationalError: unknown function: gen_random_uuid()".

Registrar `gen_random_uuid` como GenericFunction do SQLAlchemy cria um ponto
único onde a expressão pode ser traduzida por dialeto. No PostgreSQL a
renderização continua sendo exatamente `gen_random_uuid()`, então o schema em
produção não muda — a tradução só existe para o SQLite.
"""

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import GenericFunction


class gen_random_uuid(GenericFunction):
    """
    Função `gen_random_uuid()` do PostgreSQL (nativa a partir do PG 13).

    Declarada aqui apenas para que o SQLAlchemy a reconheça como uma função
    conhecida e permita registrar uma tradução por dialeto.
    """

    type = UUID(as_uuid=False)
    name = "gen_random_uuid"
    inherit_cache = True


# UUID v4 montado em SQL puro, porque o SQLite não tem gerador de UUID.
#
#   randomblob(n) -> n bytes aleatórios; hex() -> 2 caracteres por byte.
#
# Os nibbles de versão ('4') e de variante ('8'|'9'|'a'|'b') são fixados nas
# posições que a RFC 4122 exige, de modo que o valor gerado é um UUID v4 válido.
# O resultado tem 32 caracteres, sem hifens — que é exatamente como o
# SQLAlchemy persiste o tipo UUID nos bancos sem suporte nativo (CHAR(32)).
#
# A expressão inteira vai entre parênteses porque o SQLite exige isso de
# qualquer DEFAULT que não seja um literal constante.
_SQLITE_UUID_V4 = (
    "(lower("
    "hex(randomblob(4))"
    " || hex(randomblob(2))"
    " || '4' || substr(hex(randomblob(2)), 2)"
    " || substr('89ab', abs(random()) % 4 + 1, 1) || substr(hex(randomblob(2)), 2)"
    " || hex(randomblob(6))"
    "))"
)


@compiles(gen_random_uuid, "sqlite")
def _compila_gen_random_uuid_no_sqlite(element, compiler, **kw) -> str:
    return _SQLITE_UUID_V4
