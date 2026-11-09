import pytest

from app.core.config import Settings
from app.core.config import settings as configuracao_atual


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("http://localhost:4200", ["http://localhost:4200"]),
        ("https://bsfarma.com.br, https://www.bsfarma.com.br/", ["https://bsfarma.com.br", "https://www.bsfarma.com.br"]),
        ("", []),
        (" , ", []),
    ],
)
def test_cors_origins_lista_separa_por_virgula_e_normaliza(valor, esperado):
    configuracao = Settings(database_url="x", secret_key="x", cors_origins=valor)
    assert configuracao.cors_origins_lista == esperado


def test_cors_origins_sem_variavel_mantem_origem_de_desenvolvimento(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    configuracao = Settings(_env_file=None, database_url="x", secret_key="x")
    assert configuracao.cors_origins_lista == ["http://localhost:4200"]


async def test_preflight_de_origem_configurada_e_aceito_e_de_outra_e_recusado(client):
    origem_permitida = configuracao_atual.cors_origins_lista[0]
    cabecalhos = {"Access-Control-Request-Method": "GET"}

    permitida = await client.options("/health", headers={**cabecalhos, "Origin": origem_permitida})
    recusada = await client.options("/health", headers={**cabecalhos, "Origin": "https://site-desconhecido.example"})

    assert permitida.status_code == 200
    assert permitida.headers["access-control-allow-origin"] == origem_permitida
    assert recusada.status_code == 400
    assert "access-control-allow-origin" not in recusada.headers
