from app.db.base import Base  # noqa: F401
 
# 2. Sem dependências entre si
from app.usuario.model     import Usuario      # noqa: F401
from app.medicamentos.model import Medicamento  # noqa: F401
from app.paciente.model    import Paciente     # noqa: F401
 
# 3. Depende de Medicamento e Usuario
from app.lote.model import Lote  # noqa: F401
 
# 4. Depende de Lote
from app.movimentacao.model import Movimentacao  # noqa: F401
 
# 5. Depende de Lote e Medicamento
from app.alertas.model import Alertas, TipoAlerta, StatusAlerta