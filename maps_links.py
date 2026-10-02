# ----------------------------------------------------
#               CONFIGURACIÓN DE LIBRERÍAS
# ----------------------------------------------------
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.keys import Keys

# ----------------------------------------------------
#               VARIABLES DE CONFIGURACIÓN
# ----------------------------------------------------
DB_FILE = "negocios.db"

# ----------------------------------------------------
#                   FUNCIONES PRINCIPALES
# ----------------------------------------------------
def get_driver():
    """Configura y devuelve un driver de Chrome."""
    chrome_options = Options()
    
    # Descomenta la siguiente línea para que el navegador se ejecute de forma invisible
    # chrome_options.add_argument("--headless")
    
    # Configuración del driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1000, 800)
    return driver

def crear_tabla():
    """Crea la tabla de la base de datos si no existe."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS negocios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            nombre TEXT,
            direccion TEXT,
            telefono TEXT,
            pagina_web TEXT,
            maps_link TEXT UNIQUE,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def buscar_en_maps(driver, busqueda):
    """Realiza una búsqueda en Google Maps."""
    print(f"🔎 Buscando '{busqueda}' en Google Maps...")
    driver.get("https://www.google.com/maps")
    time.sleep(5)
    caja = driver.find_element(By.ID, "searchboxinput")
    caja.clear()
    caja.send_keys(busqueda)
    caja.send_keys(Keys.ENTER)
    time.sleep(5)

# ----------------------------------------------------
#               FUNCIONES DE EXTRACCIÓN
# ----------------------------------------------------
def extraer_datos_negocio(driver, maps_link):
    """Extrae nombre, dirección, teléfono y web de un negocio dado su link."""
    try:
        driver.get(maps_link)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//h1[contains(@class,"DUwDvf")]'))
        )
    except Exception as e:
        print(f" Error al cargar la página del negocio {maps_link}: {e}")
        return "No disponible", "No disponible", "No disponible", "No disponible"

    nombre = direccion = telefono = pagina_web = "No disponible"

    try:
        nombre_el = driver.find_element(By.XPATH, '//h1[contains(@class,"DUwDvf")]')
        nombre = nombre_el.text.strip()
    except:
        pass

    try:
        direccion_el = driver.find_element(By.XPATH, '//button[@data-item-id="address"]')
        span_direccion = direccion_el.find_element(By.CLASS_NAME, "rogA2c").text.strip()
        direccion = ''.join(c for c in span_direccion if c.isprintable() or c.isspace()).strip()
    except:
        pass

    try:
        telefono_el = driver.find_element(By.XPATH, '//button[contains(@data-item-id,"phone:tel:")]')
        telefono = telefono_el.get_attribute("aria-label").replace("Teléfono: ", "").strip()
        telefono = ''.join(filter(str.isdigit, telefono))

        if telefono:
            if len(telefono) == 7:
                 if telefono.startswith("1"):
                     telefono = f"+57601{telefono}"
                 else:
                     telefono = f"+57{telefono}"
            elif len(telefono) == 10 and telefono.startswith("3"):
                telefono = f"+57{telefono}"
    except:
        telefono = "No disponible"

    try:
        web_el = driver.find_element(By.XPATH, '//a[@data-item-id="authority"]')
        pagina_web = web_el.get_attribute("href").strip()
    except:
        pass
    
    if "No disponible" in direccion and not "No disponible" in telefono:
        if telefono in direccion:
            direccion = "No disponible"
    if "No disponible" in direccion and not "No disponible" in pagina_web:
        if pagina_web in direccion:
            direccion = "No disponible"
    
    if not direccion and direccion != 'No disponible':
        direccion = "No disponible"

    return nombre, direccion, telefono, pagina_web
    
def actualizar_datos_negocio(categoria, ciudad, maps_link, nombre, direccion, telefono, pagina_web):
    """Actualiza los datos completos del negocio en la DB."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE negocios
        SET nombre=?, direccion=?, telefono=?, pagina_web=?
        WHERE categoria=? AND ciudad=? AND maps_link=?
    """, (nombre, direccion, telefono, pagina_web, categoria, ciudad, maps_link))
    conn.commit()
    conn.close()

# ----------------------------------------------------
#                  FUNCIONES DE LA BASE DE DATOS
# ----------------------------------------------------
def vaciar_db():
    """Vacía la tabla 'negocios' de la base de datos."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM negocios")
        conn.commit()
        conn.close()
        print(" Base de datos vaciada con éxito.")
    except Exception as e:
        print(f" Error al vaciar la base de datos: {e}")

def verificar_db_vacia():
    """Verifica si la tabla 'negocios' está vacía."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM negocios")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            print(" La base de datos está vacía.")
            return True
        else:
            print(f" La base de datos contiene {count} registros.")
            return False
    except Exception as e:
        print(f" Error al verificar la base de datos: {e}")
        return False

# ----------------------------------------------------
#                  FUNCION DE EXPORTACIÓN
# ----------------------------------------------------
def exportar_a_excel():
    """Lee todos los datos de la DB y los exporta a un solo archivo de Excel."""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT categoria, ciudad, nombre, direccion, telefono, pagina_web FROM negocios", conn)
        conn.close()
        
        nombre_archivo = "negocios_extraidos.xlsx"
        df.to_excel(nombre_archivo, index=False)
        print(f"\n Datos exportados exitosamente a '{nombre_archivo}'.")

    except Exception as e:
        print(f" Error al exportar a Excel: {e}")

# ----------------------------------------------------
#                  FUNCIÓN PRINCIPAL
# ----------------------------------------------------
def main():
    crear_tabla()
    
    print(" ¡Bienvenido al Bot de Extracción de Empresas! ")
    print("1. Iniciar una nueva búsqueda en Google Maps.")
    print("2. Vaciar la base de datos y salir.")
    opcion = input("Elige una opción (1 o 2): ")

    if opcion == "2":
        vaciar_db()
        return

    # Si eliges la opción 1, se ejecuta el resto del bot
    TIPO_EMPRESA = input(" Ingresa el tipo de empresa (ej: restaurantes, hoteles): ")
    CIUDAD = input(" Ingresa la ciudad y país (ej: Barranquilla, Colombia): ")
    BUSQUEDA = f"{TIPO_EMPRESA} en {CIUDAD}"

    driver = get_driver()
    buscar_en_maps(driver, BUSQUEDA)
    
    enlaces_encontrados = set()
    enlaces_previos = -1
    intentos_sin_nuevos = 0
    MAX_INTENTOS = 5

    while intentos_sin_nuevos < MAX_INTENTOS:
        links_actuales = driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]')
        
        for link in links_actuales:
            href = link.get_attribute("href")
            if href and "/maps/place/" in href:
                enlaces_encontrados.add(href.split("?")[0])
        
        try:
            scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(3)
        except Exception as e:
            print(f" Error al hacer scroll: {e}")
            break

        if len(enlaces_encontrados) == enlaces_previos:
            intentos_sin_nuevos += 1
            print(f" No hay nuevos enlaces. Intento {intentos_sin_nuevos}/{MAX_INTENTOS}.")
        else:
            intentos_sin_nuevos = 0
        
        enlaces_previos = len(enlaces_encontrados)
        print(f" Enlaces únicos encontrados hasta ahora: {len(enlaces_encontrados)}")
    
    print(" Fin del scroll. Se ha alcanzado el límite de intentos sin nuevos enlaces.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT maps_link FROM negocios
        WHERE categoria=? AND ciudad=?
    """, (TIPO_EMPRESA, CIUDAD))
    enlaces_guardados = set(row[0] for row in cursor.fetchall())
    
    nuevos_enlaces = enlaces_encontrados - enlaces_guardados

    if nuevos_enlaces:
        print(f" Nuevos enlaces a procesar: {len(nuevos_enlaces)}")
        for enlace in nuevos_enlaces:
            cursor.execute("""
                INSERT OR IGNORE INTO negocios (categoria, ciudad, maps_link)
                VALUES (?, ?, ?)
            """, (TIPO_EMPRESA, CIUDAD, enlace))
            conn.commit()

            nombre, direccion, telefono, pagina_web = extraer_datos_negocio(driver, enlace)

            actualizar_datos_negocio(TIPO_EMPRESA, CIUDAD, enlace, nombre, direccion, telefono, pagina_web)
            print(f" Datos completos guardados: {nombre} | {direccion} | {telefono} | {pagina_web}")
    else:
        print(" No se encontraron nuevos enlaces en la búsqueda.")

    driver.quit()
    conn.close()

    print(f"\n Proceso terminado.")
    exportar_a_excel()


if __name__ == "__main__":
    main()