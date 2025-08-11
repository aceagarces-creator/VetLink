from django.db import models

# Importaciones de modelos organizados por funcionalidad

# Modelos de tutor y zona geográfica
from .tutor_models import Tutor
from .zona_geografica_models import Region, Provincia, Comuna

# Modelos de mascota
from .mascota_models import Mascota

# Modelos de clasificación
from .clasificacion_models import Especie, Raza

# Modelos de clínica veterinaria
from .clinicaVeterinaria_models import ClinicaVeterinaria

# Modelos de nacionalidad
from .nacionalidad_models import Nacionalidad

# Modelos de servicio
from .servicio_models import Servicio, ServicioDetalle

# Modelos de personal
from .personal_models import PersonalClinica

# Modelos de especialidad
from .especialidad_models import Especialidad

# Modelos de usuario
from .usuario_models import Usuario

# Modelos de atención clínica
from .atencionClinica_models import AtencionClinica, DocumentoAdjunto

# Modelos de receta
from .receta_models import Receta

# Modelos de insumo clínico
from .insumoClinico_models import InsumoClinico


