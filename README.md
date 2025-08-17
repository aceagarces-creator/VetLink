# VetLink 🐾

**Sistema Integrado de Gestión Veterinaria**

VetLink es una plataforma web integral, desarrollada en Django, que permite gestionar toda la información relacionada con mascotas, sus tutores y atenciones médicas. El sistema mantiene un registro centralizado permitiendo acceder, registrar y compartir el historial médico veterinario entre distintos establecimientos, de forma segura y con autorización del tutor.  

## 📋 Descripción

VetLink es una aplicación web diseñada específicamente para clínicas veterinarias que necesitan digitalizar y centralizar la gestión de sus pacientes. La plataforma facilita el registro y seguimiento de mascotas, la gestión de tutores y el control de atenciones médicas, proporcionando una solución integral para la administración clínica veterinaria.

## ✨ Características Principales

### 🏥 Gestión de Atención Médica
- Registro completo de atenciones médicas
- Historial clínico detallado por mascota
- Gestión de diagnósticos y tratamientos
- Documentos adjuntos (imágenes, archivos)
- Generación de recetas médicas

### 👥 Gestión de Tutores
- Registro de tutores con datos personales completos
- Búsqueda por RUT para identificación rápida
- Gestión de información de contacto y datos demográficos
- Historial de mascotas asociadas

### 🐕 Gestión de Mascotas
- Registro de mascotas con datos completos
- Fichas clínicas detalladas
- Historial médico completo
- Seguimiento de tratamientos
- Registro de consentimiento de interoperabilidad

### 🏢 Gestión Clínica
- Administración de clínicas veterinarias
- Gestión de personal médico
- Control de especialidades
- Gestión de servicios ofrecidos

## 🏗️ Arquitectura

### Tecnologías Utilizadas
- **Backend**: Django 5.2.4 (Python)
- **Base de Datos**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework CSS**: Bootstrap (implícito en el diseño)
- **Iconos**: Font Awesome

### Estructura del Proyecto
```
VetLink/
├── core/                    # Modelos principales y lógica de negocio
│   ├── models.py           # Importaciones centralizadas
│   ├── *_models.py         # Modelos organizados por funcionalidad
│   └── views.py            # Vistas principales
├── tutores/                # Aplicación de gestión de tutores
├── mascotas/               # Aplicación de gestión de mascotas
├── atencion_medica/        # Aplicación de atención médica
├── templates/              # Plantillas HTML base
├── media/                  # Archivos multimedia
├── ui_designs/             # Diseños de interfaz
└── vetlink_project/        # Configuración del proyecto Django
```

### Modelos Principales
- **Tutor**: Gestión de propietarios de mascotas
- **Mascota**: Información de pacientes animales
- **AtencionClinica**: Registro de consultas médicas
- **ClinicaVeterinaria**: Administración de clínicas
- **PersonalClinica**: Gestión del personal médico
- **Receta**: Prescripciones médicas

## 📋 Requisitos

### Requisitos del Sistema
- Python 3.8 o superior
- PostgreSQL 12 o superior
- Navegador web moderno

### Dependencias de Python
- Django 5.2.4
- psycopg2-binary (para PostgreSQL)
- Pillow (para manejo de imágenes)

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/vetlink.git
cd vetlink
```

### 2. Crear Entorno Virtual
```bash
python -m venv env
# En Windows:
env\Scripts\activate
# En macOS/Linux:
source env/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
```bash
# Crear base de datos PostgreSQL
createdb vetlink_db

# Aplicar migraciones
python manage.py migrate
```

### 5. Crear Superusuario (Opcional)
```bash
python manage.py createsuperuser
```

### 6. Ejecutar el Servidor
```bash
python manage.py runserver
```

El proyecto estará disponible en `http://localhost:8000`

## 💻 Uso

### Acceso al Sistema
1. Abrir el navegador y dirigirse a `http://localhost:8000`
2. Se mostrará la página principal con los módulos disponibles

### Módulos Disponibles

#### Gestión de Tutores
- **Registrar Tutor**: Crear nuevo registro de tutor
- **Consultar Tutor**: Buscar tutor existente por RUT con sus respectivas mascotas

#### Gestión de Mascotas
- **Registrar Mascota**: Crear nueva ficha de mascota
- **Consultar Ficha Clínica**: Ver ficha clínica con su historial médico completo

#### Atención Médica
- **Registrar Atención Médica**: Crear nueva consulta médica

### Funcionalidades Principales
- **Búsqueda Rápida**: Localizar tutores y mascotas por identificadores únicos
- **Historial Completo**: Acceso a todo el historial médico de cada mascota
- **Documentación**: Adjuntar archivos e imágenes a las atenciones
- **Reportes**: Generación de recetas y documentos médicos

## 📄 Licencia

Este proyecto está bajo "Todos los derechos reservados". Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Desarrollado como Proyecto de Título**

- **Universidad**: UNAB (Universidad Andrés Bello)
- **Carrera**: Ingeniería en Computación e Informática
- **Año**: 2025

### Contacto
- **Email**: [a.ceagarces@uandresbello.edu]
- **GitHub**: [@aceagarces-creator]

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

## 📞 Soporte

Si tienes alguna pregunta o necesitas ayuda, por favor:
1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con tu consulta

---

**VetLink** - Conectando el cuidado veterinario con la tecnología moderna 🐾
