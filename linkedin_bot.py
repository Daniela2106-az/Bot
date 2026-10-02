# ----------------------------------------------------
#               CONFIGURACIÓN DE LIBRERÍAS
# ----------------------------------------------------
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# ----------------------------------------------------
#                   VARIABLES DE CONFIGURACIÓN
# ----------------------------------------------------
# AÑADE TUS CREDENCIALES AQUÍ
EMAIL = "danielaamaya2106@gmail.com"
PASSWORD = "Daniela2106."

# ----------------------------------------------------
#                   FUNCIONES PRINCIPALES
# ----------------------------------------------------
def get_driver():
    """Configura y devuelve un driver de Chrome para mantener la sesión."""
    chrome_options = Options()
    
    # Esta opción es clave para mantener el inicio de sesión.
    user_profile_path = os.path.join(os.getcwd(), "linkedin_profile")
    chrome_options.add_argument(f"user-data-dir={user_profile_path}")

    # Para que funcione en segundo plano (invisible), descomenta la siguiente línea:
    # chrome_options.add_argument("--headless")
    
    try:
        driver_path = ChromeDriverManager().install()
    except Exception as e:
        print(f"❌ Error al descargar ChromeDriver: {e}")
        print("Intentando con una versión específica...")
        driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1000, 800)
    return driver

def iniciar_sesion(driver, email, password):
    """Navega a la página de login de LinkedIn e inicia sesión."""
    print("➡️ Iniciando sesión en LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "session_key"))
        )
        password_input = driver.find_element(By.NAME, "session_password")
        
        email_input.send_keys(email)
        password_input.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, ".btn__primary--large.from__button--floating")
        login_button.click()
        
        WebDriverWait(driver, 15).until(
            EC.url_contains("feed")
        )
        
        print("✅ ¡Inicio de sesión exitoso!")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Error al iniciar sesión. El bot no pudo encontrar los elementos de login. {e}")
        driver.quit()

def buscar_perfiles(driver, busqueda):
    """Realiza una búsqueda de perfiles en LinkedIn."""
    print(f"🔎 Buscando perfiles de '{busqueda}'...")
    
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={busqueda.replace(' ', '%20')}"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "reusable-search__result-container"))
        )
        print("✅ Resultados de búsqueda cargados.")
        time.sleep(3)
    except Exception as e:
        print(f"❌ No se pudieron cargar los resultados de búsqueda: {e}")
        driver.quit()
        return []

# ----------------------------------------------------
#                   FUNCIÓN PRINCIPAL
# ----------------------------------------------------
def main():
    driver = None
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔄 Intento de conexión con el navegador: {retry_count + 1}/{max_retries}")
            driver = get_driver()
            break
        except Exception as e:
            print(f"❌ Fallo en el intento de conexión: {e}")
            retry_count += 1
            time.sleep(5)
    
    if driver is None:
        print("❌ Error fatal: No se pudo conectar con el navegador después de varios intentos.")
        return

    iniciar_sesion(driver, EMAIL, PASSWORD)

    if "feed" in driver.current_url:
        busqueda = "Desarrolladores de Software en Bogotá"
        buscar_perfiles(driver, busqueda)

        print("➡️ Extrayendo enlaces de perfiles...")
        try:
            profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
            enlaces_encontrados = set()
            for link in profile_links:
                href = link.get_attribute('href')
                if href and '/in/' in href:
                    limpio = href.split("?")[0]
                    enlaces_encontrados.add(limpio)
            
            print(f"📊 Se encontraron {len(enlaces_encontrados)} enlaces únicos en la página.")
            for enlace in enlaces_encontrados:
                print(enlace)

        except Exception as e:
            print(f"❌ Error al extraer enlaces: {e}")

    else:
        print("❌ Error: No se pudo iniciar sesión. No se puede continuar la búsqueda.")

    driver.quit()

if __name__ == "__main__":
    main()