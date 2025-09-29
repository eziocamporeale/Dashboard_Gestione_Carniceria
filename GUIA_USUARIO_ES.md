# 🥩 Guía de Usuario - Dashboard Gestión Carnicería

## 📋 Índice
1. [Introducción](#introducción)
2. [Instalación y Configuración](#instalación-y-configuración)
3. [Primer Acceso](#primer-acceso)
4. [Navegación](#navegación)
5. [Funcionalidades Principales](#funcionalidades-principales)
6. [Gestión de Productos](#gestión-de-productos)
7. [Gestión de Clientes](#gestión-de-clientes)
8. [Gestión de Ventas](#gestión-de-ventas)
9. [Balance y Previsiones](#balance-y-previsiones)
10. [Analytics y Reportes](#analytics-y-reportes)
11. [Configuración](#configuración)
12. [FAQ](#faq)

---

## 🎯 Introducción

La **Dashboard Gestión Carnicería** es un sistema completo para la gestión de una carnicería, desarrollado por Ezio Camporeale. El sistema ofrece funcionalidades avanzadas para:

- **Gestión de Inventario**: Control completo de carnes, productos frescos y congelados
- **Gestión de Ventas**: Seguimiento de órdenes, facturación y pagos
- **Gestión de Clientes**: Base de datos de clientes con preferencias e historial de compras
- **Gestión de Proveedores**: Control de proveedores, órdenes y pagos
- **Analytics**: Reportes completos sobre ventas, ganancias y rendimiento
- **Gestión de Personal**: Control de empleados, turnos y productividad
- **Balance y Previsiones**: Análisis financiero con datos históricos

---

## 🚀 Instalación y Configuración

### Requisitos del Sistema
- **Python 3.8+**
- **Streamlit**
- **SQLite** (incluido con Python)

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Inicialización de Base de Datos
```bash
python3 database/init_database.py
```

### Inicio de Aplicación
```bash
streamlit run app_es.py
```

La aplicación estará disponible en: **http://localhost:8501**

---

## 🔐 Primer Acceso

### Credenciales por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`

⚠️ **IMPORTANTE**: ¡Cambia la contraseña después del primer acceso!

### Cambio de Contraseña
1. Accede al sistema
2. Ve a **⚙️ Configuración**
3. Selecciona **🔑 Cambio de Contraseña**
4. Ingresa contraseña actual y nueva contraseña
5. Confirma el cambio

---

## 🧭 Navegación

### Sidebar Principal
La sidebar contiene:
- **👤 Información de Usuario**: Nombre, rol, permisos
- **🧭 Menú de Navegación**: Secciones principales
- **⚡ Acciones Rápidas**: Operaciones frecuentes
- **ℹ️ Información del Sistema**: Versión y estado

### Secciones Disponibles
- **🏠 Dashboard**: Resumen general y KPIs
- **📦 Inventario**: Gestión de productos y stock
- **🛒 Ventas**: Sistema de ventas y POS
- **👥 Clientes**: Base de datos de clientes y CRM
- **🚚 Proveedores**: Gestión de proveedores
- **👨‍💼 Personal**: Gestión de empleados
- **📊 Analytics**: Reportes y estadísticas
- **💰 Balance y Previsiones**: Análisis financiero
- **⚙️ Configuración**: Configuraciones del sistema

---

## 🏠 Funcionalidades Principales

### Dashboard Principal
El dashboard muestra:

#### KPIs Principales
- **💰 Ventas Hoy**: Monto y número de transacciones
- **📋 Órdenes Hoy**: Número de órdenes y valor
- **👥 Clientes Totales**: Número de clientes activos
- **📦 Productos Totales**: Productos en catálogo

#### Alertas y Notificaciones
- **⚠️ Alertas de Stock**: Productos con stock bajo
- **📅 Vencimientos Próximos**: Productos próximos a vencer

#### Gráficos Interactivos
- **📈 Ventas Últimos 7 Días**: Tendencia de ventas
- **🏆 Productos Más Vendidos**: Top 5 productos

---

## 📦 Gestión de Productos

### Resumen de Productos
Visualiza todos los productos con:
- Nombre y código del producto
- Categoría y precio
- Stock actual y mínimo
- Estado del producto

### Agregar Nuevo Producto
1. Ve a **📦 Inventario** → **➕ Nuevo Producto**
2. Completa los campos obligatorios:
   - **Nombre del Producto** (obligatorio)
   - **Categoría** (obligatorio)
   - **Unidad de Medida** (obligatorio)
   - **Precio de Venta** (obligatorio)
3. Opcionalmente completa:
   - Código del producto
   - Código de barras
   - Descripción
   - Marca y origen
   - Precio de costo
   - Stock mínimo/máximo
   - Días de conservación
   - Control de temperatura
4. Haz clic en **➕ Agregar Producto**

### Gestión de Stock
- **📊 Stock**: Visualiza y gestiona inventario
- **⚠️ Alertas**: Productos con stock bajo o próximos a vencer

### Categorías de Productos Predefinidas
- **🥩 Carne Bovina**: Vaca, ternero, buey, novilla
- **🐷 Carne Porcina**: Cerdo, jabalí, lechón
- **🐔 Aves**: Pollo, pavo, pato, conejo
- **🥓 Embutidos**: Jamón, salame, mortadela, panceta
- **🥬 Productos Frescos**: Verduras, quesos, lácteos
- **❄️ Congelados**: Carne, pescado, verduras congeladas

---

## 👥 Gestión de Clientes

### Base de Datos de Clientes
Gestiona tus clientes con:
- **Datos Personales**: Nombre, apellido, contactos
- **Dirección**: Para entregas
- **Preferencias**: Cortes preferidos, días de compra
- **Alergias**: Información importante
- **Historial de Compras**: Análisis de comportamiento

### Agregar Nuevo Cliente
1. Ve a **👥 Clientes** → **➕ Nuevo Cliente**
2. Completa los datos:
   - Nombre y apellido (obligatorios)
   - Email y teléfono
   - Dirección completa
   - Tipo de cliente (individual/empresa)
   - Preferencias y alergias
3. Haz clic en **➕ Agregar Cliente**

### Programas de Fidelidad
- **Puntos**: Sistema de puntos por compras
- **Descuentos**: Promociones personalizadas
- **Comunicaciones**: SMS/Email promocionales

---

## 🛒 Gestión de Ventas

### Sistema POS
- **Registro de Ventas**: Rápido e intuitivo
- **Gestión de Pagos**: Efectivo, tarjetas, transferencias
- **Descuentos**: Aplicación de descuentos automáticos
- **Facturación**: Emisión de facturas

### Órdenes de Clientes
- **Órdenes Personalizadas**: Gestión de órdenes especiales
- **Entregas**: Programación de entregas
- **Seguimiento**: Estado de órdenes en tiempo real

### Métodos de Pago
- **💰 Efectivo**: Pago inmediato
- **💳 Tarjeta**: Pago con tarjeta
- **🏦 Transferencia**: Pago bancario
- **📄 Cheque**: Pago con cheque
- **📅 Cuotas**: Pago en cuotas

---

## 💰 Balance y Previsiones

### Análisis Financiero
Esta sección integra los datos históricos de tu Excel para proporcionar:

- **📊 Datos Históricos**: Desde la apertura hasta la fecha actual
- **📈 Análisis de Tendencias**: Comparativas mensuales y anuales
- **🔮 Previsiones**: Basadas en datos reales y patrones históricos
- **📅 Comparativas**: Año anterior vs año actual
- **🌡️ Análisis de Estacionalidad**: Patrones por temporada

### Carga de Datos Excel
1. Ve a **💰 Balance y Previsiones**
2. Haz clic en **📁 Cargar Archivo Excel**
3. Selecciona tu archivo con datos históricos
4. El sistema procesará e integrará los datos automáticamente

### Reportes Disponibles
- **Balance General**: Estado financiero completo
- **Flujo de Caja**: Entradas y salidas de dinero
- **Análisis de Rentabilidad**: Por producto y categoría
- **Previsiones de Ventas**: Proyecciones futuras
- **Análisis de Costos**: Control de gastos operativos

---

## 📊 Analytics y Reportes

### Reportes Disponibles
- **📈 Ventas**: Análisis por período, producto, cliente
- **💰 Ganancias**: Margenes, costos, ROI por producto
- **📦 Inventario**: Rotación de stock, desperdicios
- **👥 Clientes**: Análisis de comportamiento, segmentación
- **👨‍💼 Personal**: Productividad, eficiencia

### Exportación de Datos
- **📊 Excel**: Reportes detallados en Excel
- **📄 PDF**: Reportes formateados en PDF
- **📄 CSV**: Datos para análisis externos

### Gráficos Interactivos
- **Tendencias de Ventas**: Evolución en el tiempo
- **Productos Top**: Más vendidos
- **Análisis de Clientes**: Segmentación
- **Rendimiento**: KPIs empresariales

---

## ⚙️ Configuración

### Configuraciones Empresariales
- **Nombre de Empresa**: Carnicería [Tu Nombre]
- **Dirección**: Dirección completa
- **Contactos**: Teléfono y email
- **Moneda**: Peso Argentino (ARS)

### Configuraciones del Sistema
- **IVA**: Alícuota de IVA (21%)
- **Stock**: Umbrales de stock bajo
- **Vencimientos**: Días de aviso para vencimientos
- **Backups**: Configuración de backups automáticos

### Gestión de Usuarios
- **Roles**: Admin, Gerente, Vendedor, Almacenero, Visualizador
- **Permisos**: Control granular de accesos
- **Seguridad**: Contraseñas y sesiones

---

## ❓ FAQ

### Preguntas Frecuentes

**P: ¿Cómo cambio la contraseña de admin?**
R: Ve a Configuración → Cambio de Contraseña e ingresa la nueva contraseña.

**P: ¿Cómo agrego un nuevo producto?**
R: Ve a Inventario → Nuevo Producto y completa el formulario.

**P: ¿Cómo visualizo las ventas de hoy?**
R: El dashboard principal muestra automáticamente las ventas del día.

**P: ¿Cómo exporto los datos?**
R: Cada sección tiene botones de descarga para Excel y CSV.

**P: ¿Cómo gestiono el stock bajo?**
R: El sistema muestra automáticamente alertas para productos con stock bajo.

**P: ¿Cómo agrego un nuevo cliente?**
R: Ve a Clientes → Nuevo Cliente y completa los datos personales.

**P: ¿Cómo funciona el sistema de permisos?**
R: Cada usuario tiene un rol con permisos específicos para acceder a las funciones.

**P: ¿Cómo hago backup de los datos?**
R: El sistema hace backups automáticos, pero puedes crear manuales en Configuración.

**P: ¿Cómo contacto soporte técnico?**
R: Contacta a Ezio Camporeale para soporte técnico.

---

## 🆘 Soporte Técnico

### Contactos
- **Desarrollador**: Ezio Camporeale
- **Email**: ezio.camporeale@example.com
- **Versión**: 1.0.0

### Logs y Debugging
- Los logs se guardan en `logs/carniceria.log`
- Para problemas, revisa los logs para detalles
- La base de datos está en `data/carniceria.db`

### Actualizaciones
- Revisa regularmente las actualizaciones
- Siempre haz backup de los datos antes de actualizaciones
- Sigue las instrucciones de migración

---

## 📝 Changelog

### Versión 1.0.0 (21/09/2024)
- ✅ Sistema de autenticación completo
- ✅ Gestión de productos e inventario
- ✅ Dashboard con KPIs principales
- ✅ Gestión básica de clientes
- ✅ Sistema de permisos granular
- ✅ Base de datos SQLite optimizada
- ✅ Interfaz moderna y responsive
- ✅ Traducción completa al español argentino
- ✅ Sección Balance y Previsiones para datos Excel

---

*Guía creada por Ezio Camporeale - Dashboard Gestión Carnicería v1.0.0*
