# ASTC OPTIMIZER
> v1.2.0

*https://github.com/Ari-Aguilar/astc-optimizer*


Un script de Python con **interfaz de consola interactiva** que convierte automáticamente\
archivos PNG a formato ASTC comprimido para mejorar el rendimiento y reducir\
el tamaño de tus mods de [Funkin](https://github.com/FunkinCrew/funkin).

## ⚠️ Advertencias Importantes

> **🔴 ESTE SCRIPT ELIMINA TUS ARCHIVOS PNG ORIGINALES**

- Los archivos PNG serán reemplazados permanentemente por archivos `.astc` comprimidos
- **HAZ UNA COPIA DE SEGURIDAD** de tu mod antes de ejecutar este script (o usa la opción de backup integrada, ver abajo 👇)
- Esta acción es **IRREVERSIBLE** salvo que hayas creado un backup - no podrás recuperar los PNG originales de otra forma
- **NO ME HAGO RESPONSABLE POR PÉRDIDAS DE DATOS**

> **📉 Sobre la calidad**

- La compresión ASTC reduce la calidad visual de las imágenes
- Pueden verse pixeladas o con artefactos de compresión
- Es el compromiso necesario para obtener mejor rendimiento

---

## ✨ Novedades de esta versión

- 🖥️ **Interfaz de consola interactiva**: menús navegables con flechas (↑↓), ya no hace falta escribir comandos ni recordar flags
- 🤖 **Auto-instalación del encoder**: si no tienes `astcenc` instalado, el script puede descargarlo y configurarlo automáticamente por ti
- 💾 **Backup integrado**: opción de crear una carpeta `backup-old` con copia de tus PNG originales antes de convertir, respetando la estructura de carpetas
- 🔁 **Restaurar desde backup**: recupera tus PNG originales en cualquier momento desde el menú principal
- 🚫 **Exclusión de carpetas de íconos**: opción para ignorar carpetas `icon`/`icons` durante el escaneo
- 📂 **Cambio de carpeta sin reiniciar**: navega a otra ubicación del disco desde el propio programa
- 📊 **Barra de progreso** durante la conversión
- 📝 **Log de errores** (`optimizer-logError.txt`) con las fallas agrupadas por sección

---

## 📋 Requisitos Previos

### Opción A: Instalación automática (recomendada)

Si no tienes ASTC Encoder instalado, el script te lo ofrecerá automáticamente la primera vez que lo ejecutes: descarga la última versión desde GitHub, prueba los binarios compatibles con tu sistema y deja todo listo para usar. Solo necesitas conexión a internet.

### Opción B: Instalación manual

1. Descarga [ASTC Encoder](https://github.com/ARM-software/astc-encoder/releases) desde las releases oficiales
2. Descomprime el archivo descargado
3. Encontrarás varios ejecutables en la carpeta `bin/` (por ejemplo `astcenc-avx2`, `astcenc-sse4.1` ⭐ **recomendado por compatibilidad**, `astcenc-sse2`)
4. Renombra el ejecutable elegido a `astcenc` (o `astcenc.exe` en Windows)
5. Colócalo junto al script `png_to_astc.py`, o cópialo a una carpeta que esté en tu PATH

#### Verificar la instalación

Abre una terminal/CMD y ejecuta:

```bash
astcenc -version
```

Si ves algo como `astcenc v5.3.0, 64-bit sse4.1+popcnt`, ¡estás listo! ✅

---

## 🚀 Uso del Script

### Instalación

1. Descarga `png_to_astc.py` y colócalo en la carpeta raíz de tu mod:

```
tu_mod/
├── png_to_astc.py  ← Aquí
├── shared/
│   └── images/
│       └── logoMod.png
├── images/
│   └── title.png
└── _polymod_meta.json
```

2. Dale permisos de ejecución (solo en Linux/MacOS):

```bash
chmod +x png_to_astc.py
```

### Ejecución

Abre una terminal/CMD dentro de la carpeta de tu mod y ejecuta:

```bash
python png_to_astc.py
```

Todo el flujo ahora se maneja desde el menú interactivo, sin necesidad de pasar argumentos por línea de comandos. Usa las flechas ↑↓ para moverte, **Enter** para confirmar y **Esc** para retroceder al paso anterior.

### Menú Principal

Al iniciar, verás cuatro opciones:

```
🔥  Iniciar Optimización
🔁  Restaurar desde Backup (RESTORE)
📂  Moverme a otra localización
🚪  Salir
```

### Flujo de Optimización

Al elegir **Iniciar Optimización**, el script te guía paso a paso:

1. **Escaneo**: busca recursivamente todos los `.png` en la carpeta actual y subcarpetas
2. **Ignorar íconos**: pregunta si quieres excluir carpetas llamadas `icon`/`icons`
3. **Backup**: pregunta si quieres crear una copia de seguridad (`backup-old`) antes de convertir
4. **Tamaño de bloque**: elige entre `4x4`, `6x6`, `8x8` o `12x12`
5. **Calidad**: elige entre `veryfast`, `fast`, `medium`, `thorough` o `exhaustive`
6. **Conversión**: el script convierte y elimina los PNG automáticamente, mostrando una barra de progreso

Al terminar, se muestra un resumen con la cantidad de archivos convertidos y fallidos, y puedes elegir moverte a otra carpeta o salir.

### Restaurar desde Backup

Si creaste un backup durante la conversión, puedes recuperar tus PNG originales en cualquier momento desde **Restaurar desde Backup (RESTORE)** en el menú principal. El script buscará la carpeta `backup-old` en la ruta actual y reemplazará cada `.astc` encontrado por su versión PNG original.

### Cambiar de Carpeta

Puedes moverte a otra ubicación del disco sin salir ni reiniciar el script, usando la opción **Moverme a otra localización** del menú principal.

---

## 📊 Tamaños de Bloque y Calidad

### Tamaños de Bloque

| Tamaño | Calidad | Compresión | Uso Recomendado |
|--------|---------|------------|-----------------|
| 4x4    | ⭐⭐⭐⭐⭐ | 🔵🔵 | Texturas importantes, UI |
| 6x6    | ⭐⭐⭐⭐ | 🔵🔵🔵 | Balance general (predeterminado) |
| 8x8    | ⭐⭐⭐ | 🔵🔵🔵🔵 | Texturas de fondo, efectos |
| 12x12  | ⭐⭐ | 🔵🔵🔵🔵🔵 | Máxima compresión |

### Niveles de Calidad

- `veryfast` - Conversión rápida, menor calidad final
- `fast` - Rápido con calidad aceptable
- `medium` - Balance entre velocidad y calidad
- `thorough` - **Recomendado** - Buena calidad, velocidad aceptable
- `exhaustive` - Mejor calidad posible, muy lento

---

## ❓ Solución de Problemas

### Error: "No se detectó el ejecutable del compresor"

- Acepta la instalación automática cuando el script te la ofrezca, o
- Verifica que ejecutaste `astcenc -version` correctamente de forma manual
- Asegúrate de haber colocado el ejecutable junto al script o en el PATH
- En Windows, reinicia la terminal después de agregar al PATH

### Error: "Host does not support AVX2"

Tu CPU no soporta AVX2. Si instalaste manualmente, usa `astcenc-sse4.1` o `astcenc-sse2` en su lugar (la instalación automática ya prueba varias variantes por ti).

### Error: "Permission denied"

En Linux/MacOS, asegúrate de dar permisos:
```bash
chmod +x png_to_astc.py
```

### No aparecen mis PNG originales al restaurar

Verifica que la carpeta `backup-old` exista en la ruta actual y que no la hayas movido o renombrado tras la conversión.

---

## 💡 Consejos

- **Usa el backup integrado**: si no estás seguro del resultado, activa la opción de backup antes de convertir
- **Prueba primero en una copia**: haz pruebas en una carpeta de prueba antes de convertir todo tu mod
- **Compara visualmente**: revisa cómo se ven las texturas convertidas en el juego
- **Ajusta según necesidad**: usa mejor calidad (4x4) para texturas importantes y más compresión (8x8) para fondos
- **Revisa el log**: si algo falla, `optimizer-logError.txt` tiene el detalle agrupado por sección

---

## 📜 Licencia

Este script es de uso libre. Úsalo bajo tu propio riesgo.

---

## ⭐ Apóyame

Si esta herramienta te fue útil, **dale una estrella al repositorio** ⭐

¡Tu apoyo significa mucho! ❤️

---

## 🤝 Contribuciones

¿Encontraste un bug o tienes una mejora? ¡Los pull requests son bienvenidos!
