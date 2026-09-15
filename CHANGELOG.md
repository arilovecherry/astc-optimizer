# CHANGELOG

## [1.2.0] - 14/09/2026

### Nuevo
- [NUEVO] Interfaz de consola interactiva con menús navegables por flechas (↑↓), reemplazando los prompts y flags de línea de comandos
- [NUEVO] Auto-instalación del encoder: descarga, extrae y prueba automáticamente la última release de astc-encoder según SO/arquitectura
- [NUEVO] Sistema de backup: opción de copiar los PNG originales a una carpeta "backup-old" antes de convertir, preservando la estructura de carpetas
- [NUEVO] Función de restauración: recupera los PNG originales desde "backup-old" reemplazando los .astc, disponible desde el menú principal
- [NUEVO] Opción para ignorar carpetas "icon"/"icons" durante el escaneo de PNG
- [NUEVO] Cambio de carpeta de trabajo sin reiniciar el script ("Moverme a otra localización")
- [NUEVO] Barra de progreso visual durante la conversión de archivos
- [NUEVO] Log de errores por secciones en optimizer-logError.txt (instalación, backup, conversión, restauración)
- [NUEVO] Busqueda de versiones del script
### Mejora
- [MEJORA] Detección del encoder ahora soporta múltiples nombres de binario (astcenc, astcenc-sse4.1, astcenc-sse2, astcenc-avx2, astcenc-neon)
- [MEJORA] Pantalla de error con guía manual paso a paso si la auto-instalación falla
### BugFix
- [BUGFIX] Menú seleccionable en Linux/MacOS fallaba al seleccionar opciones
- [BUGFIX] Seleccionar `veryfast` en opciones hacia fallar a la compresion al no existir, cambio a `fastest`