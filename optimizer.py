#!/usr/bin/env python3
"""
ASTC Optimizer - Convierte PNG a ASTC con interfaz de consola interactiva.
by Ari - https://github.com/Ari-Aguilar/astc-optimizer
"""

import os
import sys
import io
import json
import stat
import time
import shutil
import platform
import subprocess
import urllib.request
import zipfile
from pathlib import Path

## Colores ANSI
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"

    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[37m"
    DARK    = "\033[90m"

    # Fondo oscuro para highlight de selección
    SEL_BG  = "\033[48;5;236m"
    SEL_FG  = "\033[97m"


def _strip_ansi(text):
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)


def box(text, color=C.WHITE, width=50):
    """Dibuja un recuadro alrededor del texto."""
    border = color + "┌" + "─" * (width - 2) + "┐" + C.RESET
    pad    = color + "│" + C.RESET + " " * (width - 2) + color + "│" + C.RESET
    lines  = text.split("\n")
    result = [border, pad]
    for line in lines:
        visible_len = len(_strip_ansi(line))
        padding = width - 2 - visible_len - 2
        result.append(color + "│" + C.RESET + " " + line + " " * max(0, padding) + " " + color + "│" + C.RESET)
    result.append(pad)
    result.append(color + "└" + "─" * (width - 2) + "┘" + C.RESET)
    return "\n".join(result)


def print_path_bar(path):
    # Instrucción general: la ruta actual siempre debe estar visible en pantalla
    print(f"  {C.DARK}📍 Ruta actual:{C.RESET} {C.CYAN}{path}{C.RESET}")
    print()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_status(emoji, msg, color=C.GRAY):
    print(f" {C.DARK}[{C.RESET} {emoji} {C.DARK}]{C.RESET} {color}{msg}{C.RESET}")


def print_ok(msg):
    print_status("✅", msg, C.GREEN)


def print_err(msg):
    print_status("❌", msg, C.RED)


def print_warn(msg):
    print_status("⚠️ ", msg, C.YELLOW)


def print_info(msg):
    print_status("📂", msg, C.GRAY)


## ASCII art titles
ASCII_ASTC = r"""
  █████╗ ███████╗████████╗ ██████╗
 ██╔══██╗██╔════╝╚══██╔══╝██╔════╝
 ███████║███████╗   ██║   ██║
 ██╔══██║╚════██║   ██║   ██║
 ██║  ██║███████║   ██║   ╚██████╗
 ╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝
  ██████╗ ██████╗ ████████╗
 ██╔═══██╗██╔══██╗╚══██╔══╝
 ██║   ██║██████╔╝   ██║
 ██║   ██║██╔═══╝    ██║
 ╚██████╔╝██║        ██║
  ╚═════╝ ╚═╝        ╚═╝
"""

ASCII_FOLDERS = r"""
 ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗ ███████╗
 ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗██╔════╝
 █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝███████╗
 ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗╚════██║
 ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║███████║
 ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝
"""

ASCII_OPTIM = r"""
  ██████╗ ██████╗ ████████╗██╗███╗   ███╗
 ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗ ████║
 ██║   ██║██████╔╝   ██║   ██║██╔████╔██║
 ██║   ██║██╔═══╝    ██║   ██║██║╚██╔╝██║
 ╚██████╔╝██║        ██║   ██║██║ ╚═╝ ██║
  ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝
"""

ASCII_RESULT = r"""
 ██████╗ ███████╗███████╗██╗   ██╗██╗  ████████╗
 ██╔══██╗██╔════╝██╔════╝██║   ██║██║  ╚══██╔══╝
 ██████╔╝█████╗  ███████╗██║   ██║██║     ██║
 ██╔══██╗██╔══╝  ╚════██║██║   ██║██║     ██║
 ██║  ██║███████╗███████║╚██████╔╝███████╗██║
 ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝
"""

ASCII_ERROR = r"""
 ███████╗██████╗ ██████╗  ██████╗ ██████╗
 ██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
 █████╗  ██████╔╝██████╔╝██║   ██║██████╔╝
 ██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗
 ███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║
 ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
"""

ASCII_RESTORE = r"""
 ██████╗ ███████╗███████╗████████╗ ██████╗ ██████╗ ███████╗
 ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
 ██████╔╝█████╗  ███████╗   ██║   ██║   ██║██████╔╝█████╗
 ██╔══██╗██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗██╔══╝
 ██║  ██║███████╗███████║   ██║   ╚██████╔╝██║  ██║███████╗
 ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
"""


def print_ascii(art, color):
    for line in art.split("\n"):
        print(color + C.BOLD + line + C.RESET)


def screen_frame(art, color, current_path=None, subtitle=None):
    """Limpia la pantalla y dibuja el encabezado estándar (ASCII art + ruta actual).
    Se usa al inicio de cada pantalla para que nunca se apilen dos menús juntos."""
    clear()
    print_ascii(art, color)
    print()
    if current_path is not None:
        print_path_bar(current_path)
    if subtitle:
        print(f"  {C.GRAY}{subtitle}{C.RESET}")
        print()


## Log de errores (por secciones)
LOG_FILE = "optimizer-logError.txt"


def log_error(section, message):
    """Escribe una línea de error en el log, marcada con su sección.
    Si no se puede escribir el log, se avisa por consola (nunca lanza excepción)."""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{section}] {timestamp} - {message}\n")
    except Exception as e:
        print_err(f"No se pudo escribir en el log ({LOG_FILE}): {e}")


def log_section(title, lines):
    """Escribe un bloque de errores agrupados bajo una sección en el log."""
    if not lines:
        return
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n=== {title} ({timestamp}) ===\n")
            for line in lines:
                f.write(f"  - {line}\n")
    except Exception as e:
        print_err(f"No se pudo escribir en el log ({LOG_FILE}): {e}")


## Versión del script
VERSION = "1.2.0"
REPO_API_LATEST = "https://api.github.com/repos/Ari-Aguilar/astc-optimizer/releases/latest"


def check_latest_version():
    """Consulta la última release publicada en GitHub para este script.
    Devuelve el tag sin la 'v' inicial (str), o None si falló / sin internet.
    Nunca lanza excepción ni bloquea el flujo del programa."""
    try:
        req = urllib.request.Request(REPO_API_LATEST, headers={"User-Agent": "astc-optimizer"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        tag = data.get("tag_name", "")
        return tag.lstrip("vV") if tag else None
    except Exception:
        return None


def _parse_version(v):
    """Convierte 'v1.2.0' o '1.2.0-beta' en una tupla (1, 2, 0) para poder comparar.
    Ignora sufijos no numéricos (beta, rc, etc). Devuelve None si no se pudo interpretar."""
    if not v:
        return None
    core = v.strip().lstrip("vV").split("-")[0].split("+")[0]
    parts = []
    for p in core.split("."):
        if not p.isdigit():
            return None
        parts.append(int(p))
    return tuple(parts) if parts else None


def format_version_line(current, latest):
    """Arma la línea de versión para el menú principal, según el resultado del chequeo."""
    if latest is None:
        return (f"  {C.DARK}[{C.RESET} 🏷️  {C.DARK}]{C.RESET} "
                f"{C.GRAY}Versión {C.WHITE}v{current}{C.GRAY} (sin conexión para verificar){C.RESET}")

    cur_t = _parse_version(current)
    lat_t = _parse_version(latest)

    # Si no se pudo interpretar alguna de las dos, se recurre a la comparación literal
    if cur_t is None or lat_t is None:
        if latest == current:
            return (f"  {C.DARK}[{C.RESET} 🏷️  {C.DARK}]{C.RESET} "
                    f"{C.GREEN}Versión v{current} (última disponible) ✅{C.RESET}")
        return (f"  {C.DARK}[{C.RESET} 🏷️  {C.DARK}]{C.RESET} "
                f"{C.YELLOW}Versión v{current} (última publicada: v{latest}){C.RESET}")

    if lat_t > cur_t:
        return (f"  {C.DARK}[{C.RESET} 🏷️  {C.DARK}]{C.RESET} "
                f"{C.YELLOW}Versión v{current} — hay una nueva versión disponible: v{latest} ⚠️{C.RESET}")
    if lat_t == cur_t:
        return (f"  {C.DARK}[{C.RESET} 🏷️  {C.DARK}]{C.RESET} "
                f"{C.GREEN}Versión v{current} (última disponible) ✅{C.RESET}")
    # cur_t > lat_t: versión local más nueva que la última Release (build local/dev)
    return (f"  {C.DARK}[{C.RESET} 🏷️  {C.DARK}]{C.RESET} "
            f"{C.CYAN}Versión v{current} (build de desarrollo, por delante de v{latest}){C.RESET}")


## Detección del ejecutable
ENCODER_NAMES = ["astcenc", "astcenc-sse4.1", "astcenc-sse2", "astcenc-avx2", "astcenc-neon"]
DOWNLOAD_URL  = "https://github.com/ARM-software/astc-encoder/releases"
GITHUB_API_LATEST = "https://api.github.com/repos/ARM-software/astc-encoder/releases/latest"

# Nombres de carpetas que pueden excluirse del escaneo (case-insensitive)
IGNORABLE_FOLDER_NAMES = {"icon", "icons"}
BACKUP_FOLDER_NAME = "backup-old"


def _find_local_encoder(script_dir):
    """Busca el ejecutable junto al script o en el PATH."""
    for name in ENCODER_NAMES:
        local = script_dir / name
        if local.exists():
            return str(local)
        if os.name == "nt":
            local_exe = script_dir / (name + ".exe")
            if local_exe.exists():
                return str(local_exe)
    for name in ENCODER_NAMES:
        try:
            result = subprocess.run([name, "-version"], capture_output=True, text=True)
            if result.returncode == 0 or "astcenc" in (result.stdout + result.stderr).lower():
                return name
        except FileNotFoundError:
            continue
    return None


def check_encoder():
    """Devuelve el comando del encoder si está disponible, o None si no se encontró."""
    script_dir = Path(__file__).resolve().parent
    return _find_local_encoder(script_dir)


def _is_inside_folder(path, root_path, folder_names):
    """Devuelve True si alguna carpeta del path relativo coincide (case-insensitive) con folder_names."""
    try:
        rel_parts = path.relative_to(root_path).parts[:-1]
    except ValueError:
        rel_parts = path.parts[:-1]
    for part in rel_parts:
        if part.lower() in folder_names:
            return True
    return False


def _is_inside_ignored_folder(png_path, root_path):
    return _is_inside_folder(png_path, root_path, IGNORABLE_FOLDER_NAMES)


def _is_inside_backup_folder(path, root_path):
    return _is_inside_folder(path, root_path, {BACKUP_FOLDER_NAME.lower()})


## Auto-instalación del encoder
def _pick_asset(assets):
    """Elige el .zip de la release que corresponde al SO y arquitectura actuales.
    Los assets de astc-encoder se llaman p. ej. astcenc-5.7.0-windows-x64.zip,
    astcenc-5.7.0-linux-arm64.zip, astcenc-5.7.0-macos-universal.zip, etc."""
    system  = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        os_key = "windows"
    elif system == "darwin":
        os_key = "macos"
    else:
        os_key = "linux"

    if os_key == "macos":
        # macOS siempre publica un binario universal (x64 + arm64 en el mismo zip)
        arch_keys = ["universal"]
    elif machine in ("arm64", "aarch64"):
        arch_keys = ["arm64"]
    else:
        arch_keys = ["x64", "x86_64", "amd64"]

    def zip_assets():
        return [a for a in assets if a.get("name", "").lower().endswith(".zip")]

    # 1) Coincidencia exacta de SO + arquitectura
    for asset in zip_assets():
        name = asset.get("name", "").lower()
        if os_key in name and any(a in name for a in arch_keys):
            return asset

    # 2) Fallback: mismo SO, cualquier arquitectura
    for asset in zip_assets():
        name = asset.get("name", "").lower()
        if os_key in name:
            return asset

    return None


def try_auto_install_encoder(script_dir):
    """Descarga e instala automáticamente el último astc-encoder disponible para este SO.
    El zip de cada plataforma trae varios binarios (p. ej. astcenc-avx2, astcenc-sse4.1,
    astcenc-sse2): se extraen todos y se prueba cada uno hasta encontrar uno que funcione
    en esta máquina. Devuelve el comando del ejecutable si tuvo éxito, o None si falló
    (registrando el motivo en el log)."""
    try:
        req = urllib.request.Request(GITHUB_API_LATEST, headers={"User-Agent": "astc-optimizer"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        msg = f"No se pudo consultar la última release de astc-encoder: {e}"
        print_err(msg)
        log_error("INSTALL", msg)
        return None

    assets = data.get("assets", [])
    asset = _pick_asset(assets)
    if asset is None:
        msg = "No se encontró un instalador compatible con este sistema operativo en la última release."
        print_err(msg)
        log_error("INSTALL", msg)
        return None

    download_url = asset.get("browser_download_url")
    print_status("⬇️ ", f"Descargando {asset.get('name')}...", C.CYAN)

    try:
        req = urllib.request.Request(download_url, headers={"User-Agent": "astc-optimizer"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
    except Exception as e:
        msg = f"No se pudo descargar el encoder: {e}"
        print_err(msg)
        log_error("INSTALL", msg)
        return None

    extracted_paths = []
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = zf.namelist()
            # El zip trae varios binarios por variante de CPU: astcenc-avx2(.exe),
            # astcenc-sse4.1(.exe), astcenc-sse2(.exe), etc. Se extraen todos.
            candidates = [
                n for n in names
                if not n.endswith("/") and Path(n).stem.lower().startswith("astcenc")
            ]
            if not candidates:
                msg = "El archivo descargado no contiene ejecutables astcenc reconocibles."
                print_err(msg)
                log_error("INSTALL", msg)
                return None

            for name in candidates:
                target_path = script_dir / Path(name).name
                try:
                    with zf.open(name) as src, open(target_path, "wb") as dst:
                        dst.write(src.read())
                    extracted_paths.append(target_path)
                except Exception as e:
                    log_error("INSTALL", f"No se pudo extraer {name}: {e}")
    except Exception as e:
        msg = f"No se pudo abrir el archivo descargado: {e}"
        print_err(msg)
        log_error("INSTALL", msg)
        return None

    if not extracted_paths:
        msg = "No se pudo extraer ningún ejecutable del paquete descargado."
        print_err(msg)
        log_error("INSTALL", msg)
        return None

    # Se prueba cada variante de CPU (avx2 / sse4.1 / sse2 / ...) hasta hallar una que funcione
    print_status("🧪", "Probando ejecutables extraídos...", C.CYAN)
    for exe_path in extracted_paths:
        try:
            if os.name != "nt":
                st = os.stat(exe_path)
                os.chmod(exe_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

            result = subprocess.run([str(exe_path), "-version"], capture_output=True, text=True)
            if result.returncode == 0 or "astcenc" in (result.stdout + result.stderr).lower():
                final_name = "astcenc.exe" if os.name == "nt" else "astcenc"
                final_path = script_dir / final_name
                if exe_path.name.lower() != final_name.lower():
                    try:
                        if final_path.exists():
                            final_path.unlink()
                        exe_path.rename(final_path)
                        exe_path = final_path
                    except Exception as e:
                        log_error("INSTALL", f"No se pudo renombrar {exe_path} a {final_path}: {e}")
                return str(exe_path)
        except Exception as e:
            log_error("INSTALL", f"Falló la prueba de {exe_path}: {e}")
            continue

    msg = "Se descargaron ejecutables pero ninguno pasó la prueba de funcionamiento (-version)."
    print_err(msg)
    log_error("INSTALL", msg)
    return None


## Selección con flechas
if os.name == "nt":
    import msvcrt

    def _getch():
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return 'UP'
            if ch2 == 'P': return 'DOWN'
            if ch2 == 'M': return 'RIGHT'
            if ch2 == 'K': return 'LEFT'
            return ch2
        if ch == '\r': return 'ENTER'
        if ch == '\x1b': return 'ESC'
        return ch
else:
    import tty, termios, select

    def _getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                # Distingue un ESC suelto de una secuencia de flecha (ESC [ A/B/C/D)
                ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                if not ready:
                    return 'ESC'
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    if ch3 == 'B': return 'DOWN'
                    if ch3 == 'C': return 'RIGHT'
                    if ch3 == 'D': return 'LEFT'
                return 'ESC'
            if ch in ('\r', '\n'): return 'ENTER'
            if ch == '\x03': raise KeyboardInterrupt
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def arrow_select(options, prompt="", start=0, color_active=C.CYAN):
    """Muestra una lista de opciones navegables con flechas.
    Devuelve el índice seleccionado, o None si el usuario presionó ESC (retroceder)."""
    idx = start
    n   = len(options)

    while True:
        sys.stdout.write(f"\033[{n}A")
        for i, opt in enumerate(options):
            if i == idx:
                line = f"  {color_active}▶  {opt}{C.RESET}"
            else:
                line = f"  {C.DARK}   {C.GRAY}{opt}{C.RESET}"
            print(line + " " * 10)

        key = _getch()
        if key == 'UP':
            idx = (idx - 1) % n
        elif key == 'DOWN':
            idx = (idx + 1) % n
        elif key == 'ENTER':
            return idx
        elif key == 'ESC':
            return None


def _print_options_initial(options, color_active=C.CYAN):
    """Imprime las opciones por primera vez."""
    for i, opt in enumerate(options):
        if i == 0:
            print(f"  {color_active}▶  {opt}{C.RESET}")
        else:
            print(f"  {C.DARK}   {C.GRAY}{opt}{C.RESET}")


def select_menu(options, color=C.CYAN, start=0):
    """Imprime la pista de navegación + las opciones, y devuelve el índice elegido
    (o None si se presionó ESC). Punto único para que todos los menús se comporten igual."""
    print(f"  {C.DARK}(↑↓ mover · Enter seleccionar · Esc retroceder){C.RESET}")
    _print_options_initial(options, color)
    return arrow_select(options, color_active=color, start=start)


## Pantallas
def screen_offer_install():
    """Pantalla previa al error de encoder no encontrado: ofrece instalación automática.
    ESC equivale a 'No, mostrar instrucciones manuales' (opción menos destructiva)."""
    screen_frame(ASCII_ERROR, C.YELLOW)
    print(f"  {C.GRAY}No se detectó el ejecutable del compresor ASTC{C.RESET}")
    print()
    print(f"  {C.CYAN}¿Intentar instalar los últimos binarios en esta instancia?{C.RESET}")
    print()

    opts = ["📥  Sí, intentar instalar automáticamente", "🚪  No, mostrar instrucciones manuales"]
    choice = select_menu(opts, C.YELLOW)
    return 1 if choice is None else choice


def screen_no_encoder(missing_name="astcenc"):
    """Pantalla de error: encoder no detectado (instrucciones manuales).
    ESC equivale a 'Reintentar detección' (opción menos destructiva que Salir)."""
    screen_frame(ASCII_ERROR, C.RED)
    print(f"  {C.GRAY}No se detectó el ejecutable del compresor{C.RESET}")
    print()

    print(f"  {C.RED}┌─ ❌  No se detectó: {C.WHITE}{missing_name}{C.RED} {'─' * (30 - len(missing_name))}┐{C.RESET}")
    print(f"  {C.RED}│{C.RESET}  {C.YELLOW}El compresor ASTC no fue encontrado en el PATH          {C.RED}│{C.RESET}")
    print(f"  {C.RED}│{C.RESET}  {C.YELLOW}ni junto a este script.                                 {C.RED}│{C.RESET}")
    print(f"  {C.RED}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    print(f"  {C.CYAN}┌─ 🛠️  Solución ───────────────────────────────────────────┐{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}")

    steps = [
        ("📥", "Descargar ASTC Encoder:",     f"{C.CYAN}{DOWNLOAD_URL}{C.RESET}"),
        ("📦", "Descomprimir el archivo",      f"{C.DARK}extrae el .zip / .tar.gz descargado{C.RESET}"),
        ("🔍", "Dentro de la carpeta bin/",    f"{C.DARK}encontrarás los ejecutables{C.RESET}"),
        ("✏️ ", "Renombrar el ejecutable a:",  f"{C.WHITE}astcenc{C.RESET}{C.DARK}  (ej: astcenc-sse4.1 → astcenc){C.RESET}"),
        ("📂", "Mover junto a este script:",   f"{C.DARK}en la misma carpeta que {C.WHITE}png_to_astc.py{C.RESET}"),
        ("🚀", "Volver a ejecutar el script",  f"{C.DARK}y selecciona 'Iniciar Optimización'{C.RESET}"),
    ]

    for emoji, label, detail in steps:
        print(f"  {C.CYAN}│{C.RESET}  {C.DARK}[{C.RESET} {emoji} {C.DARK}]{C.RESET}  {C.WHITE}{label}{C.RESET}")
        print(f"  {C.CYAN}│{C.RESET}         {detail}")
        print(f"  {C.CYAN}│{C.RESET}")

    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}──────────────────────────────────────────────────{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}[{C.RESET} 🪟 {C.DARK}]{C.RESET}  {C.GRAY}Windows: renombra a {C.WHITE}astcenc.exe{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}[{C.RESET} 🐧 {C.DARK}]{C.RESET}  {C.GRAY}Linux/Mac: ejecuta {C.WHITE}chmod +x astcenc{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}")
    print(f"  {C.CYAN}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    opts = ["🔄  Reintentar detección", "🚪  Salir"]
    choice = select_menu(opts, C.RED)
    return 0 if choice is None else choice


def ensure_encoder():
    """Verifica el encoder; si falta, ofrece auto-instalación y guía manual.
    Devuelve el comando del encoder, o None si el usuario decidió salir."""
    encoder_cmd = check_encoder()
    while encoder_cmd is None:
        choice = screen_offer_install()

        if choice == 0:
            script_dir = Path(__file__).resolve().parent
            print()
            encoder_cmd = try_auto_install_encoder(script_dir)
            if encoder_cmd:
                print()
                print_ok("Encoder instalado y verificado correctamente.")
                time.sleep(1.5)
                break
            else:
                print()
                print_warn("La instalación automática falló. Mostrando instrucciones manuales...")
                time.sleep(1.5)

        retry_choice = screen_no_encoder("astcenc")
        if retry_choice == 0:
            encoder_cmd = check_encoder()
        else:
            return None

    return encoder_cmd


def screen_main(current_path, latest_version=None):
    """Pantalla principal. No hay un 'atrás' real desde aquí: ESC simplemente refresca el menú."""
    screen_frame(ASCII_ASTC, C.RED, current_path=current_path,
                 subtitle="Optimizador de texturas PNG → ASTC")

    print(format_version_line(VERSION, latest_version))
    print_status("🚀", f"GITHUB: {C.CYAN}https://github.com/Ari-Aguilar/astc-optimizer{C.RESET}", C.DARK)
    print()

    print(f"  {C.RED}┌─ ⚠️  ADVERTENCIAS ──────────────────────────────────────┐{C.RESET}")
    print(f"  {C.RED}│{C.RESET}  {C.YELLOW}Este script ELIMINA los PNG originales de forma        {C.RED}│{C.RESET}")
    print(f"  {C.RED}│{C.RESET}  {C.YELLOW}permanente. Haz una copia de seguridad antes.          {C.RED}│{C.RESET}")
    print(f"  {C.RED}│{C.RESET}  {C.YELLOW}La compresión ASTC puede generar artefactos visuales.  {C.RED}│{C.RESET}")
    print(f"  {C.RED}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    opts = [
        "🔥  Iniciar Optimización",
        "🔁  Restaurar desde Backup (RESTORE)",
        "📂  Moverme a otra localización",
        "🚪  Salir",
    ]
    return select_menu(opts, C.RED)


def screen_folder(current_path=None):
    """Pantalla para cambiar de carpeta."""
    screen_frame(ASCII_FOLDERS, C.GREEN, subtitle="Moverme a otra localización")

    if current_path:
        print_status("📍", f"Localización actual: {C.CYAN}{current_path}{C.RESET}", C.DARK)
        print()

    print(f"  {C.DARK}[ {C.RESET}📂{C.DARK} ]{C.RESET} {C.GRAY}Nueva localización:{C.RESET}")
    print(f"  {C.DARK}    Ej. {C.DARK}/home/ari/proyectos/mi_mod/textures{C.RESET}")
    print(f"  {C.DARK}    (deja vacío y presiona Enter para mantener la ruta actual){C.RESET}")
    print()
    sys.stdout.write(f"  {C.CYAN}▶  {C.WHITE}")
    sys.stdout.flush()

    # Volver a modo normal para leer input
    if os.name != "nt":
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    path_input = input("").strip()
    print(C.RESET, end="")

    if not path_input:
        return current_path or Path(".").resolve()
    return Path(path_input).expanduser().resolve()


def screen_ignore_icons():
    """Pregunta si se deben ignorar las carpetas icon/icons.
    Devuelve True/False, o None si el usuario presionó ESC (retroceder)."""
    print(f"  {C.CYAN}┌─ Ignorar carpetas de íconos ─────────────────────────────┐{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}¿Quieres excluir carpetas llamadas {C.WHITE}icon{C.DARK}/{C.WHITE}icons{C.DARK}?{C.RESET}")
    print(f"  {C.CYAN}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    opts = [
        "🚫  Sí, ignorar carpetas icon/icons",
        "✅  No, incluir todos los PNG",
    ]
    choice = select_menu(opts, C.CYAN)
    if choice is None:
        return None
    return choice == 0


def screen_backup_prompt():
    """Pregunta si se debe crear una carpeta de backup con los PNG originales.
    Devuelve True/False, o None si el usuario presionó ESC (retroceder)."""
    print(f"  {C.CYAN}┌─ Crear backup de los PNG originales ────────────────────┐{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}¿Crear la carpeta {C.WHITE}{BACKUP_FOLDER_NAME}{C.DARK} con copia de los PNG{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}(preservando la estructura de carpetas)?{C.RESET}")
    print(f"  {C.CYAN}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    opts = [
        "💾  Sí, crear carpeta backup",
        "🚫  No, continuar sin backup",
    ]
    choice = select_menu(opts, C.CYAN)
    if choice is None:
        return None
    return choice == 0


def screen_block_select():
    """Selección del tamaño de bloque ASTC. Devuelve el string elegido, o None si ESC."""
    print(f"  {C.CYAN}┌─ Seleccionar Resolución (bloque) ───────────────────────┐{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {'Tamaño':<8}{'Calidad':<16}{'Compresión':<14}{'Uso Recomendado'}{C.CYAN}  │{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {'─'*60}{C.CYAN}  │{C.RESET}")
    block_opts = [
        ("4x4",   "⭐⭐⭐⭐⭐", "🔵🔵",      "Texturas UI / importantes"),
        ("6x6",   "⭐⭐⭐⭐ ", "🔵🔵🔵",    "Balance general ✅"),
        ("8x8",   "⭐⭐⭐  ",  "🔵🔵🔵🔵",  "Fondos / efectos"),
        ("12x12", "⭐⭐   ",   "🔵🔵🔵🔵🔵","Máxima compresión"),
    ]
    for b in block_opts:
        print(f"  {C.CYAN}│{C.RESET}  {C.WHITE}{b[0]:<8}{C.RESET}{b[1]:<16}{b[2]:<14}{C.DARK}{b[3]}{C.RESET}{C.CYAN}  │{C.RESET}")
    print(f"  {C.CYAN}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    block_labels = [f"{b[0]}  {b[1]}  {b[2]}  {b[3]}" for b in block_opts]
    choice = select_menu(block_labels, C.CYAN)
    if choice is None:
        return None
    return block_opts[choice][0]


def screen_quality_select():
    """Selección de la calidad de compresión. Devuelve el string elegido, o None si ESC."""
    print(f"  {C.CYAN}┌─ Seleccionar Calidad ────────────────────────────────────┐{C.RESET}")
    quality_opts = [
        ("veryfast",  "Conversión rápida, menor calidad final"),
        ("fast",      "Rápido con calidad aceptable"),
        ("medium",    "Balance entre velocidad y calidad"),
        ("thorough",  "Buena calidad, velocidad aceptable ✅"),
        ("exhaustive","Mejor calidad posible, muy lento"),
    ]
    for q in quality_opts:
        print(f"  {C.CYAN}│{C.RESET}  {C.WHITE}{q[0]:<14}{C.RESET}{C.DARK}{q[1]}{C.RESET}")
    print(f"  {C.CYAN}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    quality_labels = [f"{q[0]:<14}  {q[1]}" for q in quality_opts]
    choice = select_menu(quality_labels, C.CYAN)
    if choice is None:
        return None
    return quality_opts[choice][0]


def create_backup(root_path, png_files):
    """Copia los PNG a una carpeta backup-old, preservando la estructura de carpetas.
    Devuelve (ok, cantidad_copiada)."""
    root_path = Path(root_path)
    backup_root = root_path / BACKUP_FOLDER_NAME

    try:
        backup_root.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        msg = f"No se pudo crear la carpeta de backup ({backup_root}): {e}"
        print_err(msg)
        log_error("BACKUP", msg)
        return False, 0

    copied = 0
    errors = []
    for png_path in png_files:
        try:
            rel = Path(png_path).relative_to(root_path)
        except ValueError:
            rel = Path(Path(png_path).name)

        dest = backup_root / rel
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(png_path, dest)
            copied += 1
        except Exception as e:
            errors.append(f"{rel}: {e}")

    if errors:
        log_section("BACKUP - Errores al copiar", errors)

    return True, copied


def screen_optimize(root_path):
    """Escanea la carpeta y guía al usuario paso a paso (un solo menú visible a la vez).
    Cada paso permite retroceder con ESC al paso anterior; ESC en el primer paso
    cancela la optimización y vuelve al menú principal."""
    root_path = Path(root_path)

    screen_frame(ASCII_OPTIM, C.BLUE, current_path=root_path, subtitle="Resultado del escaneo")

    if not root_path.exists():
        print_err(f"El directorio no existe: {root_path}")
        log_error("SCAN", f"El directorio no existe: {root_path}")
        time.sleep(2)
        return None, None, None, None

    backup_root = root_path / BACKUP_FOLDER_NAME
    all_png_files = [
        p for p in root_path.rglob("*.png")
        if not _is_inside_backup_folder(p, backup_root)
    ]

    if not all_png_files:
        print_warn("No se encontraron archivos PNG en la ruta especificada.")
        time.sleep(2)
        return None, None, None, None

    print(f"  {C.DARK}[{C.RESET} {C.YELLOW}!{C.RESET} {C.DARK}]{C.RESET}  {C.WHITE}Encontrados {C.YELLOW}{len(all_png_files)}{C.WHITE} archivos PNG{C.RESET}")
    time.sleep(0.8)

    STEP_ICONS, STEP_BACKUP, STEP_BLOCK, STEP_QUALITY, STEP_DONE = range(5)
    step = STEP_ICONS

    png_files    = all_png_files
    do_backup    = False
    chosen_block = None
    chosen_quality = None

    while step != STEP_DONE:
        if step == STEP_ICONS:
            screen_frame(ASCII_OPTIM, C.BLUE, current_path=root_path, subtitle="Resultado del escaneo")
            choice = screen_ignore_icons()
            if choice is None:
                # No hay paso anterior: ESC cancela la optimización
                return None, None, None, None

            if choice:
                png_files = [p for p in all_png_files if not _is_inside_ignored_folder(p, root_path)]
                if not png_files:
                    print_warn("No quedan archivos PNG tras excluir icon/icons.")
                    time.sleep(2)
                    return None, None, None, None
            else:
                png_files = all_png_files
            step = STEP_BACKUP

        elif step == STEP_BACKUP:
            screen_frame(ASCII_OPTIM, C.BLUE, current_path=root_path,
                         subtitle=f"Archivos a convertir: {len(png_files)}")
            choice = screen_backup_prompt()
            if choice is None:
                step = STEP_ICONS
                continue
            do_backup = choice
            step = STEP_BLOCK

        elif step == STEP_BLOCK:
            screen_frame(ASCII_OPTIM, C.BLUE, current_path=root_path,
                         subtitle=f"Archivos a convertir: {len(png_files)}")
            choice = screen_block_select()
            if choice is None:
                step = STEP_BACKUP
                continue
            chosen_block = choice
            step = STEP_QUALITY

        elif step == STEP_QUALITY:
            screen_frame(ASCII_OPTIM, C.BLUE, current_path=root_path,
                         subtitle=f"Bloque elegido: {chosen_block}")
            choice = screen_quality_select()
            if choice is None:
                step = STEP_BLOCK
                continue
            chosen_quality = choice
            step = STEP_DONE

    return png_files, chosen_block, chosen_quality, do_backup


def screen_converting(png_files, block_size, quality, encoder_cmd, root_path, do_backup):
    """Ejecuta el backup opcional, la conversión y muestra progreso."""
    screen_frame(ASCII_OPTIM, C.BLUE, current_path=root_path, subtitle="Convirtiendo archivos...")

    if do_backup:
        print_status("💾", "Creando backup de los PNG originales...", C.CYAN)
        ok, backup_copied = create_backup(root_path, png_files)
        if ok:
            print_ok(f"Backup creado en '{BACKUP_FOLDER_NAME}': {backup_copied} archivo(s) copiados")
        else:
            print_warn("No se pudo crear la carpeta de backup. Continuando sin backup.")
        print()

    print_status("⚙️ ", f"Bloque: {C.CYAN}{block_size}{C.RESET}  Calidad: {C.CYAN}{quality}{C.RESET}", C.DARK)
    print_status("🔧", f"Encoder: {C.CYAN}{encoder_cmd}{C.RESET}", C.DARK)
    print()

    success = 0
    fail    = 0
    total   = len(png_files)
    fail_details = []

    for i, png_path in enumerate(png_files, 1):
        png_file  = Path(png_path)
        astc_file = png_file.with_suffix('.astc')

        bar_done  = int((i / total) * 30)
        bar       = C.CYAN + "█" * bar_done + C.DARK + "░" * (30 - bar_done) + C.RESET
        pct       = int((i / total) * 100)

        sys.stdout.write(f"\r  {C.DARK}[{C.RESET}{bar}{C.DARK}]{C.RESET} {C.WHITE}{pct:>3}%{C.RESET}  {C.DARK}{png_file.name[:40]}{C.RESET}   ")
        sys.stdout.flush()

        try:
            cmd = [
                encoder_cmd, '-cl',
                str(png_file), str(astc_file),
                block_size, f'-{quality}'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and astc_file.exists() and astc_file.stat().st_size > 0:
                png_file.unlink()
                success += 1
            else:
                fail += 1
                raw_error = (result.stderr or result.stdout or "").strip()
                error_line = raw_error.splitlines()[-1] if raw_error else "Error desconocido"
                fail_details.append(f"{png_file.name}: {error_line}")

        except Exception as e:
            fail += 1
            fail_details.append(f"{png_file.name}: {e}")

    print(f"\r  {C.DARK}[{C.RESET}{C.GREEN}{'█' * 30}{C.DARK}]{C.RESET} {C.GREEN}100%{C.RESET}  {C.DARK}Completado{'  ' * 20}{C.RESET}")
    print()

    if fail_details:
        log_section("COMPRESION FAILED", fail_details)

    return success, fail


def screen_results(success, fail):
    """Pantalla de resultados finales.
    ESC equivale a 'Moverme a otra carpeta' (opción menos destructiva que Salir)."""
    screen_frame(ASCII_RESULT, C.MAGENTA, subtitle="¡Felicidades, convertido!")

    print_status("✅", f"Convertidos: {C.GREEN}{success}{C.RESET}", C.DARK)
    print_status("❌", f"Errores:     {C.RED}{fail}{C.RESET}", C.DARK)
    if fail:
        print()
        print(f"  {C.DARK}Detalle de los errores en: {C.WHITE}{LOG_FILE}{C.RESET}")
    print()

    opts = [
        "📂  Moverme a otra carpeta",
        "🚪  Salir",
    ]
    choice = select_menu(opts, C.MAGENTA)
    return 0 if choice is None else choice


def screen_restore(current_path):
    """Restaura los PNG originales desde 'backup-old', reemplazando cada .astc encontrado.
    ESC en la confirmación equivale a 'No, cancelar'."""
    root_path = Path(current_path)

    screen_frame(ASCII_RESTORE, C.YELLOW, current_path=root_path)

    print(f"  {C.CYAN}┌─ Restablecer PNG's originales desde backup ────────────┐{C.RESET}")
    print(f"  {C.CYAN}│{C.RESET}  {C.DARK}Se buscará la carpeta {C.WHITE}{BACKUP_FOLDER_NAME}{C.DARK} en la ruta actual.{C.RESET}")
    print(f"  {C.CYAN}└──────────────────────────────────────────────────────────┘{C.RESET}")
    print()

    opts = ["✅  Sí, restablecer", "❌  No, cancelar"]
    choice = select_menu(opts, C.YELLOW)
    choice = 1 if choice is None else choice
    print()

    if choice == 1:
        return

    backup_root = root_path / BACKUP_FOLDER_NAME

    if not backup_root.exists():
        print_err(f"No se encontró la carpeta de backup: {backup_root}")
        log_error("RESTORE", f"Carpeta de backup no encontrada: {backup_root}")
        time.sleep(2)
        return

    astc_files = [
        p for p in root_path.rglob("*.astc")
        if not _is_inside_backup_folder(p, backup_root)
    ]

    if not astc_files:
        print_warn("No se encontraron archivos .astc para restaurar.")
        time.sleep(2)
        return

    total = len(astc_files)
    restored = 0
    failures = []

    for i, astc_path in enumerate(astc_files, 1):
        try:
            rel = astc_path.relative_to(root_path)
        except ValueError:
            rel = Path(astc_path.name)

        backup_png = backup_root / rel.with_suffix(".png")

        sys.stdout.write(f"\r  {C.DARK}[{C.RESET}{C.YELLOW}{i}/{total}{C.RESET}{C.DARK}]{C.RESET}  {C.DARK}{astc_path.name[:40]}{C.RESET}" + " " * 15)
        sys.stdout.flush()

        if backup_png.exists():
            try:
                dest_png = astc_path.with_suffix(".png")
                shutil.copy2(backup_png, dest_png)
                astc_path.unlink()
                restored += 1
            except Exception as e:
                failures.append((astc_path, f"Error al restaurar: {e}"))
        else:
            failures.append((astc_path, "No se encontró versión PNG en el backup"))

    print()
    print()
    print_status("✅", f"Restablecidos: {C.GREEN}{restored}{C.WHITE} de {C.YELLOW}{total}{C.RESET}", C.DARK)

    if failures:
        print_status("❌", f"Fallos: {C.RED}{len(failures)}{C.RESET}", C.DARK)
        print()
        for idx, (astc_path, reason) in enumerate(failures, 1):
            print(f"  {C.RED}{idx}.{C.RESET} {C.WHITE}{astc_path.name}{C.RESET}  {C.DARK}{astc_path}{C.RESET}")
            print(f"     {C.RED}({reason}){C.RESET}")
        log_section(
            "RESTORE - Fallos",
            [f"{astc_path.name} | {astc_path} | {reason}" for astc_path, reason in failures]
        )

    print()
    input(f"  {C.DARK}Presiona ENTER para continuar...{C.RESET}")


## Flujo principal
def main():
    current_path = Path(".").resolve()
    latest_version = check_latest_version()  # se chequea una única vez, al iniciar

    encoder_cmd = ensure_encoder()
    if encoder_cmd is None:
        clear()
        print_ok("¡Hasta luego!")
        print()
        sys.exit(0)

    while True:
        try:
            choice = screen_main(current_path, latest_version)
            if choice is None:
                continue  # ESC en el menú principal: no hay nada a lo que volver

            if choice == 0:
                # Verificar encoder de nuevo (pudo moverse o eliminarse)
                encoder_cmd = ensure_encoder()
                if encoder_cmd is None:
                    clear(); print_ok("¡Hasta luego!"); print(); sys.exit(0)

                result = screen_optimize(current_path)
                png_files, block_size, quality, do_backup = result

                if png_files is None:
                    continue

                success, fail = screen_converting(
                    png_files, block_size, quality, encoder_cmd, current_path, do_backup
                )
                post = screen_results(success, fail)

                if post == 0:
                    current_path = screen_folder(current_path)
                else:
                    clear(); print_ok("¡Hasta luego!"); print(); sys.exit(0)

            elif choice == 1:
                screen_restore(current_path)

            elif choice == 2:
                current_path = screen_folder(current_path)

            elif choice == 3:
                clear(); print_ok("¡Hasta luego!"); print(); sys.exit(0)

        except KeyboardInterrupt:
            clear()
            print_warn("Operación cancelada por el usuario.")
            print()
            sys.exit(0)


if __name__ == "__main__":
    main()