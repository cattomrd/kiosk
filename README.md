URL Slider con FastAPI
Una aplicación web desarrollada con FastAPI para crear presentaciones de URLs con temporizadores y fechas de caducidad.

Características
Panel de administración para gestionar slides
Configuración de tiempo de visualización para cada slide
Fechas de caducidad para slides
Visualización automática de slides con controles de navegación
Sistema de autenticación para proteger el panel de administración
Requisitos
Python 3.7+
Dependencias (ver requirements.txt)
Instalación
Clonar el repositorio:
bash
git clone https://github.com/tuusuario/url-slider.git
cd url-slider
Crear y activar un entorno virtual:
bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instalar dependencias:
bash
pip install -r requirements.txt
Archivo requirements.txt:
fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
jinja2>=3.1.2
Configuración
Editar el archivo app/dependencies.py para cambiar la clave secreta (SECRET_KEY).
Editar el archivo app/main.py para cambiar la contraseña del usuario administrador predeterminado.
Ejecución
Iniciar el servidor:
bash
uvicorn app.main:app --reload
Acceder a la aplicación:
Panel de administración: http://localhost:8000/admin
Visualizador de slides: http://localhost:8000/
Iniciar sesión con las credenciales predeterminadas:
Usuario: admin
Contraseña: adminpassword
Uso
Panel de Administración
Iniciar sesión en http://localhost:8000/login
Agregar nuevos slides desde el panel
Configurar para cada slide:
URL de destino
Título descriptivo
Duración de visualización en segundos
Fecha de caducidad (opcional)
Estado (activo/inactivo)
Visualizador de Slides
Acceder a http://localhost:8000/
Los slides se mostrarán automáticamente según la duración configurada
Controles disponibles:
Botones de navegación en la parte inferior
Teclas de flecha izquierda/derecha para navegar
Barra espaciadora para pausar/reanudar
Personalización
Editar estilos en app/static/css/styles.css
Modificar plantillas en app/templates/
Seguridad
La aplicación utiliza:
OAuth2 con JWT para autenticación
Contraseñas hasheadas con bcrypt
Protección de rutas de administración
Licencia
Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.


