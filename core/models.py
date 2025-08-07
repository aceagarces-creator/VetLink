from django.db import models

from .zona_geografica_models import Comuna, Provincia, Region
from .nacionalidad_models import Nacionalidad

from .tutor_models import Tutor, TutorNacionalidad

from .mascota_models import Mascota
from .clasificacion_models import Especie, Raza

from .clinicaVeterinaria_models import ClinicaVeterinaria, ClinicaServicio
from .servicio_models import Servicio, ServicioDetalle

from .personal_models import PersonalClinica, PersonalNacionalidad, PersonalEspecialidad
from .especialidad_models import Especialidad

from .atencionClinica_models import AtencionClinica, AtencionInsumo, DocumentoAdjunto
from .receta_models import Receta, RecetaItem

from .insumoClinico_models import InsumoClinico

from .usuario_models import Usuario


