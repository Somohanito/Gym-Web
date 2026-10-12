<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,4,10,20,35&height=220&section=header&text=GymWeb%20SaaS&fontSize=42&fontColor=00f2fe&animation=fadeIn&fontAlignY=38&desc=Modular%20Gym%20Administration%20Platform&descSize=16&descAlignY=62" />
</p>

<p align="center">
  <a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=20&duration=3000&pause=1000&color=00f2fe&center=true&vCenter=true&width=650&height=40&lines=Real-Time+QR+Access+Control;Automated+Memberships+%26+Financials;Coach-Student+Workout+Tracking" alt="Typing SVG" /></a>
</p>

---

## 🚀 Sobre el Proyecto

**GymWeb** es una plataforma SaaS modular diseñada para la administración integral de gimnasios y centros de acondicionamiento físico. Permite automatizar el control de accesos por códigos QR en tiempo real, la gestión financiera, el seguimiento de membresías y la asignación personalizada de rutinas y dietas por parte de entrenadores.

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
El administrador cuenta con una vista centralizada para gestionar alumnos inscritos, filtrar membresías generales o personalizadas, dar de alta nuevos usuarios y monitorear el estatus de pagos.

<p align="center">
  <img src="assets/dashboard_admin.jpg" alt="Dashboard Admin" width="90%"/>
</p>

---

### 2. Control de Acceso Automático por Código QR (Kiosco)
Módulo en tiempo real equipado con escáner de códigos QR y bitácora de entradas diarias. Incluye gráficas dinámicas de horas con mayor afluencia y días más concurridos de la semana.

<p align="center">
  <img src="assets/dashboard_QR.jpg" alt="Control de Acceso QR" width="90%"/>
</p>

---

### 3. Gestión de Ingresos y Reportes Contables
Panel financiero que calcula en tiempo real el total histórico de ingresos, dividiéndolos por método de pago (Efectivo vs. Transferencia) e incluye exportación de reportes completos a formato tabular/Excel.

<p align="center">
  <img src="assets/dashboard_ingresos.jpg" alt="Módulo de Ingresos" width="90%"/>
</p>

---

### 4. Gestión de Alumnos y Filtrado por Membresía
Permite alternar de manera fluida entre membresías generales y personalizadas, mostrando el coach asignado, teléfonos de contacto, fechas de vencimiento y acciones rápidas (generar QR, editar o eliminar).

<p align="center">
  <img src="assets/dashboard_personalizado.jpg" alt="Membresías Personalizadas" width="90%"/>
</p>

---

### 5. Alumnos con Membresía Vencida
Control automatizado de alertas para identificar de inmediato a los socios con pagos atrasados y tomar acciones comerciales.

<p align="center">
  <img src="assets/dashboard_vencidos.jpg" alt="Alumnos Vencidos" width="90%"/>
</p>

---

### 6. Panel de Gestión de Usuarios (Personal)
Control de roles jerárquicos (`ADMIN` y `COACH`) con opciones de seguridad avanzadas y códigos QR maestros de autorización presencial.

<p align="center">
  <img src="assets/dashboard_usuarios.jpg" alt="Gestión de Usuarios" width="90%"/>
</p>

<p align="center">
  <img src="assets/dashboard_QR_Maestro.jpg" alt="QR Maestro" width="70%"/>
</p>

---

### 7. Panel de Entrenadores (Coaches)
Los instructores pueden supervisar el rendimiento semanal, el cumplimiento de rutinas en porcentaje y asignar planes de entrenamiento o dietas personalizadas.

<p align="center">
  <img src="assets/dashboard_coach.jpg" alt="Panel de Entrenadores" width="90%"/>
</p>

---

### 8. Portal del Alumno (Gamificación y Rachas)
Cada socio cuenta con su propio panel donde visualiza el estatus de su membresía, su código QR personal de acceso, su rutina semanal de ejercicios/alimentación y un sistema de rachas con notificaciones de celebración al completar entrenamientos.

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