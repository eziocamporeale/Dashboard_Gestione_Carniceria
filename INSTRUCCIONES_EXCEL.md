# 📊 Instrucciones para Integración de Datos Excel

## 🎯 Objetivo
Integrar los datos históricos del Excel de gestión de la carnicería en la sección **Balance y Previsiones** del dashboard.

## 📋 Estructura del Excel Analizada

Basándome en el Excel proporcionado, he identificado la siguiente estructura:

### 📅 Hojas Mensuales
- **Noviembre 2024**: Datos desde el 22/11/2024
- **Diciembre 2024**: Datos del mes de diciembre
- **Enero 2025**: Datos del mes de enero
- **Febrero 2025**: Datos del mes de febrero
- **Marzo 2025**: Datos del mes de marzo
- **Abril 2025**: Datos del mes de abril
- **Mayo 2025**: Datos del mes de mayo
- **Junio 2025**: Datos del mes de junio

### 📊 Columnas Identificadas
- **NºMov**: Número de movimiento/operación
- **Fecha**: Fecha de la operación
- **Base I**: Base imponible de ventas
- **IGIC**: Impuesto IGIC
- **COBRO**: Monto cobrado
- **Nombre**: Nombre del cliente/proveedor
- **Beneficio**: Beneficio de la operación
- **Parte Pro**: Parte proporcional
- **Total**: Total de la operación
- **Fondo**: Fondo de reserva
- **Stock**: Stock disponible
- **Hacienda**: Impuestos
- **Efectivo**: Efectivo disponible

## 🔧 Funcionalidades Implementadas

### 1. **Procesador de Excel** (`components/excel_processor.py`)
- Carga y procesa todas las hojas del Excel
- Convierte tipos de datos automáticamente
- Extrae información de ventas, gastos y transacciones
- Calcula tendencias y estadísticas

### 2. **Analizador de Carnicería** (`components/carniceria_analyzer.py`)
- Analiza específicamente los datos de la carnicería
- Extrae ventas diarias y totales mensuales
- Analiza pagos a proveedores
- Calcula márgenes de ganancia
- Genera previsiones basadas en datos históricos

### 3. **Sección Balance y Previsiones** (actualizada en `app_es.py`)
- **Resumen General**: KPIs principales y tendencias
- **Análisis Mensual**: Evolución detallada por mes
- **Previsiones**: Proyecciones basadas en datos históricos
- **Cargar Datos**: Interfaz para subir el Excel

## 📈 Análisis Disponibles

### 📊 Resumen General
- **Total Ventas**: Suma de todas las ventas históricas
- **Total Gastos**: Suma de todos los gastos
- **Ganancia Total**: Beneficio neto total
- **Transacciones**: Número total de operaciones
- **Tendencias**: Análisis de crecimiento/decrecimiento

### 📈 Análisis Mensual
- **Evolución de Ventas**: Gráfico de tendencia mensual
- **Margen de Ganancia**: Análisis de rentabilidad por mes
- **Detalle Mensual**: Tabla con todos los datos por mes

### 🔮 Previsiones
- **Ventas Previstas**: Proyección para el próximo mes
- **Gastos Previstos**: Estimación de gastos futuros
- **Ganancia Prevista**: Beneficio proyectado
- **Nivel de Confianza**: Evaluación de la precisión de las previsiones

### 🚚 Análisis de Proveedores
- **Top Proveedores**: Ranking de proveedores por monto
- **Distribución de Pagos**: Análisis de gastos por proveedor
- **Tendencias de Compras**: Evolución de compras por proveedor

## 🚀 Cómo Usar

### 1. **Cargar Datos**
1. Ve a **💰 Balance y Previsiones**
2. Selecciona la pestaña **📁 Cargar Datos**
3. Sube tu archivo Excel con los datos históricos
4. El sistema procesará automáticamente todos los datos

### 2. **Ver Análisis**
1. **📊 Resumen General**: KPIs principales y tendencias
2. **📈 Análisis Mensual**: Gráficos y tablas detalladas
3. **🔮 Previsiones**: Proyecciones futuras
4. **📁 Cargar Datos**: Interfaz de carga de archivos

### 3. **Interpretar Resultados**
- **Tendencias**: 📈 = Creciente, 📉 = Decreciente, ➡️ = Estable
- **Márgenes**: Porcentaje de ganancia sobre ventas
- **Previsiones**: Basadas en promedio de últimos 3 meses

## 🔍 Datos Procesados del Excel

### 📅 Período Analizado
- **Inicio**: Noviembre 2024
- **Fin**: Junio 2025
- **Duración**: 8 meses de datos históricos

### 💰 Ventas Identificadas
- **Ventas Diarias**: Totales por día
- **Ventas por Proveedor**: Pagos a proveedores
- **Base Imponible**: Ventas sin impuestos
- **IGIC**: Impuestos aplicados
- **Cobros**: Montos efectivamente cobrados

### 🏪 Proveedores Identificados
- **VARA DEL REY**: Proveedor principal
- **VECCHIA AVENIDA DE GALDAR**: Proveedor secundario
- **JOCAMAK**: Proveedor de equipos
- **ECOGOURMET CANARIAS**: Proveedor de productos
- **GALACANARIA**: Proveedor local
- **CENTRAL UNIFORMES**: Proveedor de uniformes
- **MAKRO**: Proveedor mayorista
- **CANPAPLAS**: Proveedor de envases
- **EMMA ACOSTA ESTEVEZ**: Proveedor de servicios
- **CUCHILLOS**: Proveedor de utensilios

## 📊 Métricas Calculadas

### 📈 Tendencias
- **Tendencia de Ventas**: Análisis de crecimiento mensual
- **Tendencia de Gastos**: Evolución de costos operativos
- **Tendencia de Ganancias**: Análisis de rentabilidad
- **Tasa de Crecimiento**: Porcentaje de crecimiento anual

### 💰 Rentabilidad
- **Margen de Ganancia**: Porcentaje de beneficio sobre ventas
- **Consistencia de Ganancias**: Estabilidad de los márgenes
- **Punto de Equilibrio**: Nivel de ventas para cubrir gastos
- **ROI**: Retorno sobre inversión

### 🔮 Previsiones
- **Modelo de Promedio Móvil**: Basado en últimos 3 meses
- **Nivel de Confianza**: Evaluación de precisión
- **Suposiciones**: Condiciones del modelo predictivo
- **Escenarios**: Optimista, realista, pesimista

## 🛠️ Configuración Técnica

### 📁 Archivos Creados
- `components/excel_processor.py`: Procesador general de Excel
- `components/carniceria_analyzer.py`: Analizador específico de carnicería
- `test_excel_integration.py`: Tests de integración
- `INSTRUCCIONES_EXCEL.md`: Este archivo de instrucciones

### 🔧 Dependencias
- `pandas`: Procesamiento de datos
- `numpy`: Cálculos numéricos
- `plotly`: Visualizaciones interactivas
- `streamlit`: Interfaz de usuario

### 🧪 Tests
Ejecuta los tests para verificar la integración:
```bash
python3 test_excel_integration.py
```

## 📝 Notas Importantes

### ⚠️ Limitaciones
- El análisis se basa en los datos disponibles en el Excel
- Las previsiones son estimaciones basadas en tendencias históricas
- Los datos deben estar en el formato esperado

### 🔄 Actualizaciones
- Los datos se procesan en tiempo real al cargar el archivo
- No se almacenan datos del Excel en la base de datos
- Cada carga genera un análisis nuevo

### 📊 Calidad de Datos
- El sistema maneja datos faltantes automáticamente
- Convierte tipos de datos automáticamente
- Valida la estructura de las hojas

## 🎯 Próximos Pasos

### 🔮 Mejoras Futuras
1. **Análisis Estacional**: Identificar patrones por temporada
2. **Análisis de Productos**: Rentabilidad por tipo de carne
3. **Análisis de Clientes**: Segmentación y comportamiento
4. **Alertas Automáticas**: Notificaciones de tendencias
5. **Exportación de Reportes**: Generar PDFs con análisis

### 📈 Funcionalidades Adicionales
1. **Comparativas Año Anterior**: Análisis interanual
2. **Análisis de Competencia**: Benchmarking del sector
3. **Optimización de Stock**: Análisis de rotación
4. **Análisis de Precios**: Elasticidad de precios
5. **Análisis de Costos**: Desglose detallado de gastos

---

*Instrucciones creadas por Ezio Camporeale - Dashboard Gestión Carnicería v1.0.0*
