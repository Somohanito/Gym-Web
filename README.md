## 🚀 GymWeb SaaS

**GymWeb** es una plataforma modular para la administración integral de gimnasios, desarrollada con arquitectura backend robusta para automatizar el control de accesos por códigos QR en tiempo real, gestión financiera, membresías y seguimiento de entrenamientos personalizados.

---

## 🛠️ Stack Tecnológico

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,sqlite,postgresql,html,css,js,git,github,vscode&perline=5" />
</p>

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Bcrypt, Flask-Migrate
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Jinja2 Templates, Bootstrap 5
- **Bases de Datos:** SQLite (Desarrollo local), PostgreSQL (Producción)

---

## 📸 Módulos y Funcionalidades del Sistema

### 1. Panel de Administración General
Vista centralizada para administrar alumnos inscritos, filtrar membresías generales o personalizadas, dar de alta nuevos usuarios y supervisar pagos.

<p align="center">
  <img src="assets/dashboard_admin.jpg" alt="Dashboard Admin" width="90%"/>
</p>

---

### 2. Control de Acceso Automático por Código QR (Kiosco)
Módulo en tiempo real con escáner de códigos QR y bitácora de entradas, incluyendo gráficas dinámicas de afluencia por hora y días de la semana.

<p align="center">
  <img src="assets/dashboard_QR.jpg" alt="Control de Acceso QR" width="90%"/>
</p>

---

### 3. Gestión de Ingresos y Reportes Contables
Panel financiero que calcula ingresos históricos totales, divididos por método de pago (Efectivo vs. Transferencia) con exportación de reportes a Excel.

<p align="center">
  <img src="assets/dashboard_ingresos.jpg" alt="Módulo de Ingresos" width="90%"/>
</p>

---

### 4. Gestión de Alumnos y Filtrado por Membresía
Alternancia fluida entre membresías generales y personalizadas, mostrando el coach asignado, datos de contacto, vencimientos y acciones rápidas de edición o control.

<p align="center">
  <img src="assets/dashboard_personalizado.jpg" alt="Membresías Personalizadas" width="90%"/>
</p>

---

### 5. Alumnos con Membresía Vencida
Sistema automatizado de alertas para identificar socios con pagos atrasados.

<p align="center">
  <img src="assets/dashboard_vencidos.jpg" alt="Alumnos Vencidos" width="90%"/>
</p>

---

### 6. Panel de Gestión de Usuarios (Personal)
Control de roles (`ADMIN` y `COACH`) con opciones de seguridad y códigos QR maestros de autorización presencial.

<p align="center">
  <img src="assets/dashboard_usuarios.jpg" alt="Gestión de Usuarios" width="90%"/>
</p>

<p align="center">
  <img src="assets/dashboard_QR_Maestro.jpg" alt="QR Maestro" width="70%"/>
</p>

---

### 7. Panel de Entrenadores (Coaches)
Supervisión de rendimiento semanal, cumplimiento de rutinas y asignación de planes de entrenamiento o dietas.

<p align="center">
  <img src="assets/dashboard_coach.jpg" alt="Panel de Entrenadores" width="90%"/>
</p>

---

### 8. Portal del Alumno (Gamificación y Rachas)
Panel del socio para consultar estado de membresía, código QR personal, rutina semanal y sistema de rachas con notificaciones al completar entrenamientos.

<p align="center">
  <img src="assets/dashboard_alumno.jpg" alt="Dashboard Alumno" width="90%"/>
</p>

<p align="center">
  <img src="assets/dashboard_racha.jpg" alt="Entrenamiento Completado" width="70%"/>
</p>

---

## ⚙️ Instalación y Configuración Local

```bash
# 1. Clona el repositorio
git clone [https://github.com/Somohanito/Gym-Web.git](https://github.com/Somohanito/Gym-Web.git)
cd Gym-Web

# 2. Crea y activa un entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Ejecuta la aplicación
python app.py
