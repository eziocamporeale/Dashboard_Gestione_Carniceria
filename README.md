# 🥩 Dashboard Gestión Carnicería

**Sistema completo de gestión para carnicerías con base de datos Supabase y deployment en Streamlit Cloud.**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

## 📋 **Características Principales**

### 🛒 **Gestión de Ventas**
- Dashboard completo con métricas en tiempo real
- Registro de nuevas ventas con formulario intuitivo
- Reportes avanzados con filtros por fecha
- Gestión del equipo de ventas y rendimiento
- Objetivos y metas con proyecciones

### 📊 **Analytics y Reportes**
- Estadísticas de ventas, inventario y finanzas
- Gráficos interactivos con Plotly
- Exportación a Excel y PDF
- Análisis de tendencias y proyecciones
- Reportes personalizables

### 👥 **Gestión de Personal**
- Lista completa de empleados
- Gestión de turnos y horarios
- Estadísticas de rendimiento
- Sistema de roles y permisos
- Formularios de alta/baja/modificación

### 🏢 **Gestión de Proveedores**
- Base de datos de proveedores
- Seguimiento de transacciones
- Estadísticas de compras
- Gestión de contactos y direcciones
- Sistema de pedidos

### 📈 **Gestión de Inventario**
- Control de stock en tiempo real
- Alertas de productos con stock bajo
- Productos próximos a vencer
- Categorización y unidades de medida
- Gestión de precios y costos

### 📊 **Integración Excel**
- Importación automática de datos Excel
- Procesamiento y análisis de datos
- Almacenamiento en base de datos
- Exportación de reportes
- Sincronización bidireccional

## 🚀 **Tecnologías Utilizadas**

- **Frontend:** Streamlit (Python)
- **Backend:** Supabase (PostgreSQL)
- **Base de datos:** PostgreSQL con Row Level Security
- **Visualización:** Plotly, Pandas
- **Autenticación:** Sistema seguro integrado
- **Deployment:** Streamlit Cloud

## 🔐 **Seguridad Implementada**

- **Row Level Security (RLS)** en Supabase
- **Autenticación segura** con roles de usuario
- **Encriptación** de datos en reposo
- **Conexiones SSL/TLS** para todas las comunicaciones
- **Variables de entorno** para credenciales sensibles
- **Backup automático** diario

## 📦 **Instalación y Configuración**

### **Requisitos**
```bash
Python 3.8+
pip install -r requirements_supabase.txt
```

### **Configuración Local**
```bash
# 1. Clonar repositorio
git clone https://github.com/eziocamporeale/Dashboard_Gestione_Carniceria.git
cd Dashboard_Gestione_Carniceria

# 2. Instalar dependencias
pip install -r requirements_supabase.txt

# 3. Configurar variables de entorno
cp env_template.txt .env
# Editar .env con tus credenciales

# 4. Probar conexión
python test_supabase_connection.py

# 5. Ejecutar aplicación
streamlit run app_es.py
```

### **Deployment en Streamlit Cloud**
Ver [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) para instrucciones completas.

## 🗄️ **Configuración de Base de Datos**

### **Supabase Setup**
1. Crear proyecto en [Supabase](https://supabase.com)
2. Ejecutar script SQL: `database/supabase_schema.sql`
3. Configurar Row Level Security
4. Configurar variables de entorno

### **Estructura de Base de Datos**
- **users** - Usuarios del sistema
- **products** - Productos e inventario
- **sales** - Ventas realizadas
- **customers** - Clientes
- **suppliers** - Proveedores
- **employees** - Empleados
- **excel_data** - Datos importados de Excel

## 📊 **Funcionalidades por Módulo**

### **🏠 Dashboard Principal**
- Métricas en tiempo real
- Gráficos de tendencias
- Alertas y notificaciones
- Resumen ejecutivo

### **🛒 Gestión de Ventas**
- Registro de ventas
- Análisis de productos más vendidos
- Reportes por período
- Gestión de clientes

### **📦 Gestión de Inventario**
- Control de stock
- Alertas de reposición
- Gestión de categorías
- Precios y costos

### **👥 Gestión de Personal**
- Base de datos de empleados
- Gestión de turnos
- Evaluaciones de rendimiento
- Sistema de roles

### **🏢 Gestión de Proveedores**
- Base de datos de proveedores
- Seguimiento de compras
- Gestión de contactos
- Estadísticas de proveedores

### **📊 Analytics y Reportes**
- Reportes de ventas
- Análisis financiero
- Reportes de inventario
- Análisis de clientes

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**
```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-api-key
USE_SUPABASE=true
APP_ENVIRONMENT=production
```

### **Configuración de Seguridad**
- Configurar RLS en Supabase
- Definir políticas de acceso
- Configurar autenticación
- Establecer roles de usuario

## 📈 **Monitoreo y Mantenimiento**

### **Métricas Importantes**
- Uptime de la aplicación
- Performance de la base de datos
- Uso de memoria
- Errores y logs

### **Backup y Recovery**
- Backup automático en Supabase
- Versionado en GitHub
- Rollback rápido si es necesario

## 🤝 **Contribución**

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 **Autor**

**Ezio Camporeale**
- GitHub: [@eziocamporeale](https://github.com/eziocamporeale)
- Email: [tu-email@example.com]

## 🙏 **Agradecimientos**

- [Streamlit](https://streamlit.io) por el framework
- [Supabase](https://supabase.com) por la base de datos
- [Plotly](https://plotly.com) por las visualizaciones
- Comunidad de desarrolladores

---

## 📞 **Soporte**

Para soporte técnico o preguntas:
- Crear issue en GitHub
- Contactar al autor
- Revisar documentación

**¡Sistema listo para producción!** 🚀