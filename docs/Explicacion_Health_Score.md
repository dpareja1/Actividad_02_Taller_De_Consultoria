# 📊 Guía Rápida: Health Score de Datos (TechLogistics)

## 1. ¿Qué mide esta métrica?
El **Health Score** es la nota de "salud" de la información. Dice qué tan confiable es un reporte antes de usarlo para tomar decisiones.

**La fórmula aplicada es:**
> **Health Score = 100 × (1 - (0.7 × % Nulos + 0.3 × % Duplicados))**

* **70% del peso:** Penaliza la falta de información (celdas vacías).
* **30% del peso:** Penaliza la repetición de datos (registros duplicados).

---

## 2. Niveles de Confianza

| Score | Calidad | ¿Es confiable? |
| :--- | :--- | :--- |
| **90% - 100%** | ⭐ **Excelente** | Sí, los datos son sólidos y coherentes. |
| **80% - 89%** | ⚠️ **Aceptable** | Sí, pero requiere supervisión humana. |
| **Bajo 70%** | ❌ **Riesgoso** | No, puede llevar a conclusiones erróneas. |

---

## 3. Resultado de la Auditoría Real (TechLogistics)

Tras procesar los datos actuales, estos son los niveles de confianza alcanzados:

### 📈 Módulo Inventario
* **Antes:** 98.24% | **Después:** **98.93%**
* **Mejora:** +0.69

### 📈 Módulo Transacciones
* **Antes:** 100.0% | **Después:** **100.0%**
* **Mejora:** 0.0

### 📈 Módulo Feedback
* **Antes:** 96.93% | **Después:** **97.70%**
* **Mejora:** +0.77

---

## 4. Conceptos Clave en el Dashboard

1.  **Health Score Inicial:** La calidad de los datos tal cual vienen del sistema operativo.
2.  **Health Score Final:** La calidad real después de nuestra limpieza técnica y ética.
3.  **Celdas Vacías:** Datos que faltaban y que el sistema gestionó para no romper los cálculos.

---