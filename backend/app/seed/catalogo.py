from dataclasses import dataclass

from app.usuario.model import PerfilUsuario


@dataclass(frozen=True)
class UsuarioDemo:
    login: str
    nome: str
    perfil: PerfilUsuario
    variavel_senha: str


@dataclass(frozen=True)
class MedicamentoDemo:
    chave: str
    embalagem: int
    validade_meses: int
    campos: dict


@dataclass(frozen=True)
class Uso:
    medicamento: str
    quantidades: tuple[tuple[int, float], ...]
    intervalo: int
    eventual: bool = False
    sazonal: bool = False


@dataclass(frozen=True)
class PerfilClinico:
    condicao: str
    pacientes: int
    esquemas: tuple[tuple[tuple[Uso, ...], float], ...]


@dataclass(frozen=True)
class LoteAvulso:
    medicamento: str
    chegada: int
    validade: int
    sobra_dias: int


@dataclass(frozen=True)
class Desabastecimento:
    medicamento: str
    desde: int
    fator: float


USUARIOS = (
    UsuarioDemo("gestor", "Helena Duarte", PerfilUsuario.GESTOR, "SEED_SENHA_GESTOR"),
    UsuarioDemo("farmaceut", "Rafael Monteiro", PerfilUsuario.FARMACEUTICO, "SEED_SENHA_FARMACEUTICO"),
    UsuarioDemo("atendente", "Camila Rocha", PerfilUsuario.ATENDENTE, "SEED_SENHA_ATENDENTE"),
)


def _med(chave, embalagem, validade_meses, **campos) -> MedicamentoDemo:
    campos.setdefault("restricao_hospitalar", False)
    return MedicamentoDemo(chave, embalagem, validade_meses, campos)


MEDICAMENTOS = (
    _med("losartana", 500, 24,
         nome_generico="Losartana Potássica", nome_comercial="Cozaar", concentracao="50 MG",
         forma_farmaceutica="Comprimido revestido", via_administracao="Oral",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="C1F - Antagonistas Da Angiotensina Ii",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("anlodipino", 500, 24,
         nome_generico="Besilato De Anlodipino", nome_comercial="Norvasc", concentracao="5 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Pfizer Brasil Ltda", classe_terapeutica="C1B - Antagonistas Do Cálcio",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("hidroclorotiazida", 500, 24,
         nome_generico="Hidroclorotiazida", nome_comercial="Hidroclorotiazida", concentracao="25 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Medquímica Indústria Farmacêutica", classe_terapeutica="C3A - Diuréticos Tiazídicos",
         tipo_produto="Genérico", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("enalapril", 500, 24,
         nome_generico="Maleato De Enalapril", nome_comercial="Renitec", concentracao="10 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="C1E - Inibidores Da Eca",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("captopril", 500, 24,
         nome_generico="Captopril", nome_comercial="Capoten", concentracao="25 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Bristol-Myers Squibb", classe_terapeutica="C1E - Inibidores Da Eca",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("atenolol", 500, 24,
         nome_generico="Atenolol", nome_comercial="Atenolol", concentracao="25 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Eurofarma Laboratorios S.A.", classe_terapeutica="C1D - Betabloqueadores",
         tipo_produto="Genérico", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("furosemida", 200, 24,
         nome_generico="Furosemida", nome_comercial="Lasix", concentracao="40 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Sanofi-Aventis Farmacêutica Ltda", classe_terapeutica="C3B - Diuréticos De Alça",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Hipertensão"),
    _med("metformina_500", 500, 24,
         nome_generico="Cloridrato De Metformina", nome_comercial="Glifage", concentracao="500 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Merck S.A.", classe_terapeutica="A10K - Biguanidas",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Diabetes"),
    _med("metformina_850", 500, 24,
         nome_generico="Cloridrato De Metformina", nome_comercial="Glifage", concentracao="850 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Merck S.A.", classe_terapeutica="A10K - Biguanidas",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Diabetes"),
    _med("glibenclamida", 500, 24,
         nome_generico="Glibenclamida", nome_comercial="Daonil", concentracao="5 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Sanofi-Aventis Farmacêutica Ltda", classe_terapeutica="A10J - Sulfonilureias",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Diabetes"),
    _med("insulina_nph", 10, 24,
         nome_generico="Insulina Humana", nome_comercial="Humulin N", concentracao="100 UI/ML",
         forma_farmaceutica="Suspensão injetável", via_administracao="Parenteral",
         fabricante="Eli Lilly Do Brasil Ltda", classe_terapeutica="A10A - Insulinas",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Diabetes"),
    _med("insulina_regular", 10, 24,
         nome_generico="Insulina Humana", nome_comercial="Humulin R", concentracao="100 UI/ML",
         forma_farmaceutica="Solução injetável", via_administracao="Parenteral",
         fabricante="Eli Lilly Do Brasil Ltda", classe_terapeutica="A10A - Insulinas",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Diabetes"),
    _med("dapagliflozina", 100, 24,
         nome_generico="Dapagliflozina", nome_comercial="Forxiga", concentracao="10 MG",
         forma_farmaceutica="Comprimido revestido", via_administracao="Oral",
         fabricante="Astrazeneca Do Brasil Ltda", classe_terapeutica="A10N - Inibidores De Sglt-2",
         tipo_produto="Referência", tarja="Tarja Vermelha",
         indicacao_farmacia_popular="Diabetes + Doença Cardiovascular"),
    _med("sinvastatina_20", 500, 24,
         nome_generico="Sinvastatina", nome_comercial="Zocor", concentracao="20 MG",
         forma_farmaceutica="Comprimido revestido", via_administracao="Oral",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="C4A - Inibidores Da Hmg-Coa Redutase",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Dislipidemia"),
    _med("sinvastatina_40", 200, 24,
         nome_generico="Sinvastatina", nome_comercial="Zocor", concentracao="40 MG",
         forma_farmaceutica="Comprimido revestido", via_administracao="Oral",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="C4A - Inibidores Da Hmg-Coa Redutase",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Dislipidemia"),
    _med("salbutamol", 20, 24,
         nome_generico="Sulfato De Salbutamol", nome_comercial="Aerolin", concentracao="100 MCG",
         forma_farmaceutica="Aerossol para inalação", via_administracao="Inalatória",
         fabricante="Glaxosmithkline Brasil Ltda", classe_terapeutica="R3A - Broncodilatadores Beta-2",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Asma"),
    _med("beclometasona_50", 20, 24,
         nome_generico="Dipropionato De Beclometasona", nome_comercial="Clenil", concentracao="50 MCG",
         forma_farmaceutica="Aerossol para inalação", via_administracao="Inalatória",
         fabricante="Chiesi Farmaceutici", classe_terapeutica="R3B - Glicocorticóides Inalatórios",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Asma"),
    _med("beclometasona_200", 20, 24,
         nome_generico="Dipropionato De Beclometasona", nome_comercial="Clenil", concentracao="200 MCG",
         forma_farmaceutica="Aerossol para inalação", via_administracao="Inalatória",
         fabricante="Chiesi Farmaceutici", classe_terapeutica="R3B - Glicocorticóides Inalatórios",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Asma"),
    _med("budesonida", 20, 24,
         nome_generico="Budesonida", nome_comercial="Rhinocort", concentracao="50 MCG",
         forma_farmaceutica="Suspensão para inalação nasal", via_administracao="Inalatória",
         fabricante="Astrazeneca Do Brasil Ltda", classe_terapeutica="R1A - Corticosteróides Nasais",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Rinite"),
    _med("levonorgestrel", 50, 36,
         nome_generico="Levonorgestrel;Etinilestradiol", nome_comercial="Microvlar",
         concentracao="0,15 MG + 0,03 MG", forma_farmaceutica="Comprimido revestido",
         via_administracao="Oral", fabricante="Bayer S.A.",
         classe_terapeutica="G3B - Anticoncepcionais Orais Combinados",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Anticoncepção"),
    _med("medroxiprogesterona", 20, 36,
         nome_generico="Acetato De Medroxiprogesterona", nome_comercial="Depo-Provera",
         concentracao="150 MG", forma_farmaceutica="Suspensão injetável",
         via_administracao="Parenteral", fabricante="Pfizer Brasil Ltda",
         classe_terapeutica="G3A - Progestágenos",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Anticoncepção"),
    _med("noretisterona", 50, 36,
         nome_generico="Noretisterona", nome_comercial="Norestin", concentracao="0,35 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Libbs Farmacêutica Ltda", classe_terapeutica="G3A - Progestágenos",
         tipo_produto="Similar", tarja="Tarja Vermelha", indicacao_farmacia_popular="Anticoncepção"),
    _med("alendronato", 100, 24,
         nome_generico="Alendronato De Sódio", nome_comercial="Fosamax", concentracao="70 MG",
         forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="M5B - Bisfosfonatos",
         tipo_produto="Referência", tarja="- (*)", indicacao_farmacia_popular="Osteoporose"),
    _med("levodopa", 200, 24,
         nome_generico="Carbidopa (Port. 344/98 Lista C 1);Levodopa", nome_comercial="Sinemet",
         concentracao="25 MG + 250 MG", forma_farmaceutica="Comprimido", via_administracao="Oral",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="N4A - Dopaminérgicos",
         tipo_produto="Referência", tarja="Tarja Vermelha",
         indicacao_farmacia_popular="Doença de Parkinson"),
    _med("timolol", 10, 24,
         nome_generico="Maleato De Timolol", nome_comercial="Timoptol", concentracao="5 MG/ML",
         forma_farmaceutica="Solução oftálmica", via_administracao="Oftálmica",
         fabricante="Merck Sharp & Dohme", classe_terapeutica="S1E - Betabloqueadores Oftálmicos",
         tipo_produto="Referência", tarja="Tarja Vermelha", indicacao_farmacia_popular="Glaucoma"),
)


LOSARTANA = Uso("losartana", ((30, 0.55), (60, 0.45)), 30)
ANLODIPINO = Uso("anlodipino", ((30, 0.7), (60, 0.3)), 30)
HIDROCLOROTIAZIDA = Uso("hidroclorotiazida", ((30, 1.0),), 30)
ENALAPRIL = Uso("enalapril", ((60, 1.0),), 30)
CAPTOPRIL = Uso("captopril", ((60, 0.5), (90, 0.5)), 30)
ATENOLOL = Uso("atenolol", ((30, 0.6), (60, 0.4)), 30)
FUROSEMIDA = Uso("furosemida", ((30, 1.0),), 30)
METFORMINA_500 = Uso("metformina_500", ((60, 0.4), (90, 0.35), (120, 0.25)), 30)
METFORMINA_850 = Uso("metformina_850", ((60, 0.6), (90, 0.4)), 30)
GLIBENCLAMIDA = Uso("glibenclamida", ((30, 0.5), (60, 0.5)), 30)
INSULINA_NPH = Uso("insulina_nph", ((1, 0.4), (2, 0.5), (3, 0.1)), 30)
INSULINA_REGULAR = Uso("insulina_regular", ((1, 1.0),), 30)
DAPAGLIFLOZINA = Uso("dapagliflozina", ((30, 1.0),), 30)
SINVASTATINA_20 = Uso("sinvastatina_20", ((30, 1.0),), 30)
SINVASTATINA_40 = Uso("sinvastatina_40", ((30, 1.0),), 30)
SALBUTAMOL = Uso("salbutamol", ((1, 0.9), (2, 0.1)), 75, eventual=True, sazonal=True)
BECLOMETASONA_50 = Uso("beclometasona_50", ((1, 1.0),), 30)
BECLOMETASONA_200 = Uso("beclometasona_200", ((1, 1.0),), 30)
BUDESONIDA = Uso("budesonida", ((1, 1.0),), 45, eventual=True, sazonal=True)
LEVONORGESTREL = Uso("levonorgestrel", ((1, 0.7), (3, 0.3)), 28)
MEDROXIPROGESTERONA = Uso("medroxiprogesterona", ((1, 1.0),), 90)
NORETISTERONA = Uso("noretisterona", ((1, 0.8), (3, 0.2)), 28)
ALENDRONATO = Uso("alendronato", ((4, 1.0),), 28)
LEVODOPA = Uso("levodopa", ((90, 0.5), (120, 0.5)), 30)
TIMOLOL = Uso("timolol", ((1, 1.0),), 30)


HAS = "Hipertensão arterial sistêmica (I10)"
DM2 = "Diabetes mellitus tipo 2 (E11)"

PERFIS_CLINICOS = (
    PerfilClinico(HAS, 40, (
        ((LOSARTANA,), 0.30),
        ((LOSARTANA, HIDROCLOROTIAZIDA), 0.20),
        ((ANLODIPINO,), 0.12),
        ((ENALAPRIL, HIDROCLOROTIAZIDA), 0.12),
        ((CAPTOPRIL,), 0.08),
        ((ATENOLOL, HIDROCLOROTIAZIDA), 0.08),
        ((LOSARTANA, ANLODIPINO), 0.10),
    )),
    PerfilClinico("Hipertensão arterial sistêmica (I10) + Insuficiência cardíaca (I50)", 5, (
        ((ENALAPRIL, FUROSEMIDA), 0.6),
        ((CAPTOPRIL, FUROSEMIDA), 0.4),
    )),
    PerfilClinico(DM2, 18, (
        ((METFORMINA_500,), 0.40),
        ((METFORMINA_850,), 0.25),
        ((METFORMINA_850, GLIBENCLAMIDA), 0.25),
        ((METFORMINA_500, GLIBENCLAMIDA), 0.10),
    )),
    PerfilClinico(f"{HAS} + {DM2}", 20, (
        ((LOSARTANA, METFORMINA_850), 0.40),
        ((LOSARTANA, METFORMINA_500, GLIBENCLAMIDA), 0.20),
        ((ENALAPRIL, METFORMINA_850), 0.20),
        ((ANLODIPINO, METFORMINA_500), 0.20),
    )),
    PerfilClinico(f"{HAS} + Hipercolesterolemia (E78.0)", 14, (
        ((LOSARTANA, SINVASTATINA_20), 0.5),
        ((ANLODIPINO, SINVASTATINA_40), 0.25),
        ((ATENOLOL, SINVASTATINA_20), 0.25),
    )),
    PerfilClinico(f"{DM2} + Doença cardiovascular aterosclerótica (I25)", 6, (
        ((METFORMINA_850, DAPAGLIFLOZINA, SINVASTATINA_40), 1.0),
    )),
    PerfilClinico("Diabetes mellitus tipo 1 (E10)", 6, (
        ((INSULINA_NPH, INSULINA_REGULAR), 0.7),
        ((INSULINA_NPH,), 0.3),
    )),
    PerfilClinico(f"{DM2} insulinodependente (E11.9)", 6, (
        ((INSULINA_NPH, METFORMINA_850), 1.0),
    )),
    PerfilClinico("Dislipidemia mista (E78.2)", 8, (
        ((SINVASTATINA_20,), 0.6),
        ((SINVASTATINA_40,), 0.4),
    )),
    PerfilClinico("Asma persistente (J45)", 12, (
        ((BECLOMETASONA_50, SALBUTAMOL), 0.5),
        ((BECLOMETASONA_200, SALBUTAMOL), 0.3),
        ((SALBUTAMOL,), 0.2),
    )),
    PerfilClinico("Rinite alérgica perene (J30.3)", 8, (
        ((BUDESONIDA,), 1.0),
    )),
    PerfilClinico("Planejamento familiar — anticoncepção hormonal (Z30.0)", 18, (
        ((LEVONORGESTREL,), 0.55),
        ((MEDROXIPROGESTERONA,), 0.30),
        ((NORETISTERONA,), 0.15),
    )),
    PerfilClinico("Osteoporose pós-menopáusica (M81.0)", 6, (
        ((ALENDRONATO,), 1.0),
    )),
    PerfilClinico("Doença de Parkinson (G20)", 3, (
        ((LEVODOPA,), 1.0),
    )),
    PerfilClinico("Glaucoma primário de ângulo aberto (H40.1)", 4, (
        ((TIMOLOL,), 1.0),
    )),
)


LOTES_AVULSOS = (
    LoteAvulso("captopril", -80, 9, 18),
    LoteAvulso("glibenclamida", -70, 17, 20),
    LoteAvulso("beclometasona_50", -95, 24, 40),
    LoteAvulso("sinvastatina_40", -60, 28, 15),
    LoteAvulso("furosemida", -210, -38, 35),
    LoteAvulso("medroxiprogesterona", -240, -65, 60),
    LoteAvulso("salbutamol", -150, 95, 330),
    LoteAvulso("levonorgestrel", -120, 70, 240),
)

DESABASTECIMENTOS = (
    Desabastecimento("losartana", -130, 0.3),
    Desabastecimento("insulina_nph", -100, 0.25),
    Desabastecimento("timolol", -150, 0.0),
)
