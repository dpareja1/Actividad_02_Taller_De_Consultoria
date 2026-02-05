# TechLogistics S.A.S – Decisión Ética en Curaduría de Datos

## Resumen Ejecutivo

El procesamiento aplicado sigue el principio: **"Preservar la integridad del hecho económico y operativo, corrigiendo inconsistencias técnicas mediante métodos estadísticos robustos (Mediana/Moda) para evitar sesgos por valores atípicos."**

---

## 1. FEEDBACK (Clientes)

### 1.1 Qué se ELIMINÓ
**Decisión:** Eliminar registros 100% duplicados basados en `Transaccion_ID`.

**Justificación:**
- Un registro de feedback duplicado para una misma transacción infla el NPS.

---

### 1.2 Qué se IMPUTÓ (Edades fuera de rango)

**Registros identificados:** Edades no numéricas o fuera del rango lógico (ej: 195 años).

**Decisión:** **IMPUTAR con MEDIANA (35 años)**.

**Justificación:**
- Usar la mediana (35) sitúa al cliente en el segmento demográfico más representativo de la empresa.

---

### 1.3 Qué se NORMALIZÓ (Escala NPS)

**Registros identificados:** Valores en escala -100 a 100 o nulos.

**Decisión:** **REESCALAR a 1-10 e IMPUTAR nulos con 5.0**.

**Justificación:**
- La inconsistencia de escalas impide el cálculo de KPIs globales.
- Se mapean valores negativos a la zona baja (1-4) y positivos a la zona alta (6-10). Los nulos se tratan como "Neutros" (5.0).

---

## 2. INVENTARIO (Maestro de Productos)

### 2.1 Qué se ELIMINÓ
**Nada.** Se preserva el catálogo completo para asegurar que no existan sin referencia de producto.

---

### 2.2 Qué se IMPUTÓ

#### **2.2.1 Lead_Time_Dias**

**Registros identificados:** Strings como "25-30 días", "Inmediato", "nan".

**Decisión:** **EXTRACCIÓN NUMÉRICA + MEDIANA por Categoría**.

**Justificación:**
- Se extrae el valor máximo (ej: "25-30" -> 30) para un análisis de riesgo conservador.
- Los nulos se imputan por **Categoría**.

---

#### **2.2.2 Costo_Unitario_USD (Outliers)**

**Registros identificados:** Valores extremos detectados por **Método IQR** (ej: $0.01 o $850k).

**Decisión:** **REEMPLAZAR con MEDIANA por Categoría**.

**Justificación:**
- Un costo de $0.01 arruina el cálculo de margen real.
- La mediana por categoría es el estimador más fiel al valor de mercado.

---

#### **2.2.3 Stock_Actual (Valores Negativos)**

**Registros identificados:** Unidades menores a cero.

**Decisión:** **CONVERTIR A POSITIVOS (valor absoluto)**.

**Justificación:**
- Físicamente no existe el "stock negativo".

---

## 3. TRANSACCIONES (Ventas y Logística)

### 3.1 Qué se ELIMINÓ
**Nada.** Las transacciones son el registro histórico de ingresos.

---

### 3.2 Qué se IMPUTÓ

#### **3.2.1 Cantidad_Vendida (Negativos)**

**Registros identificados:** Valores < 0.

**Decisión:** **CONVERTIR A POSITIVOS (valor absoluto)**.

**Justificación:**
- Lo mas probable es que representes errores en el ingreso del dato.

---

#### **3.2.2 Tiempo_Entrega (Outliers de Sistema)**

**Registros identificados:** Valores de "999" días o nulos.

**Decisión:** **REEMPLAZAR con NaN e IMPUTAR con Mediana por Ruta**.

**Justificación:**
- "999" puede ser un error de software.

---

#### **3.2.3 Costos de Envío (Nulos)**

**Registros identificados:** Valores faltantes en envíos online.

**Decisión:** **IMPUTACIÓN CON MEDIANA POR RUTA**.

---
