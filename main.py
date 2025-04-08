import pandas as pd
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid


def get_driver():
    """Configura y retorna una instancia de WebDriver con bypass de Cloudflare."""
    options = Options()
    options.add_argument("--headless")  # Modo sin interfaz
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver


def obtener_tabla_de_posiciones(url, categoria):
    """Extrae la tabla de posiciones desde la URL de la categoría dada."""
    driver = get_driver()
    
    
    driver.get(url)


    try:
        # Esperar a que la tabla aparezca en el DOM (máximo 20s)
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/table'))
        )
        table = driver.find_element(By.XPATH, '//*[@id="main"]/div/table')
    except Exception as e:
        print(f"No se encontró la tabla de posiciones para la categoría {categoria}: {e}")
        driver.quit()
        return pd.DataFrame()

    html_content = table.get_attribute('outerHTML')
    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr')

    data = []
    headers = ['Pos', 'Club', 'Logo', 'Pts', 'PJ', 'PG', 'PE', 'PP', 'SP', 'GF', 'GC', 'DG', 'Bo', 'Sa', 'Categoria']

    for i, row in enumerate(rows):
        if i > 1:  # Saltar los encabezados
            cols = row.find_all('td')
            if len(cols) >= 13:
                pos = cols[0].get_text(strip=True)
                club_td = cols[1]
                club_name = club_td.get_text(strip=True)
                try:
                    img = club_td.find('img')
                    logo_url = urljoin(url, img['src']) if img else None
                except:
                    logo_url = None
                # Extraer el resto de los datos
                stats = [col.get_text(strip=True) for col in cols[2:13]]
                data.append([pos, club_name, logo_url, *stats, categoria])

    df = pd.DataFrame(data, columns=headers)
    return df


def actualizar_en_mongodb(df):
    """Actualiza la base de datos con los datos de la tabla de posiciones."""
    client = MongoClient("mongodb+srv://bebiruesta90:Bebiwing11@mycluster.vheby.mongodb.net/")
    db = client['maristapp']
    collection = db['hockey_team_information']

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        query = {'Pos': row['Pos'], 'categoria': row['Categoria']}
        
        existing_doc = collection.find_one(query)
        if existing_doc:
            if '_id' in row_dict:
                del row_dict['_id']
        else:
            row_dict['_id'] = str(uuid.uuid4())

        collection.update_one(query, {'$set': row_dict}, upsert=True)

categorias_urls = [
    ('Primera A', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=1&nombre_torneo=144&subdivision=2'),
    ('Intermedia A', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=2&nombre_torneo=144&subdivision=2'),
    ('Quinta A', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=3&nombre_torneo=144&subdivision=2'),
    ('Sexta A', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=4&nombre_torneo=144&subdivision=2'),
    ('Séptima A', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=5&nombre_torneo=144&subdivision=2'),
    ('Primera B', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=1&nombre_torneo=105&subdivision=27'),
    ('Intermedia B', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=2&nombre_torneo=105&subdivision=27'),
    ('Quinta B', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=3&nombre_torneo=105&subdivision=27'),
    ('Sexta B', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=4&nombre_torneo=105&subdivision=27'),
    ('Séptima B', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=5&nombre_torneo=105&subdivision=27'),
    ('Primera C', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=1&nombre_torneo=99&subdivision=46'),
    ('Intermedia C', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=2&nombre_torneo=99&subdivision=46'),
    ('Quinta C', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=3&nombre_torneo=99&subdivision=46'),
    ('Sexta C', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=4&nombre_torneo=99&subdivision=46'),
    ('Séptima C', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=5&nombre_torneo=99&subdivision=46'),
    ('Cuarta', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=10&nombre_torneo=134&subdivision=65'),
    ('Segunda', 'https://www.ahba.com.ar/club.php?id=173&seccion=TABLA_DE_POSICIONES&genero=2&categoria=9&nombre_torneo=5&subdivision=65')
]

tabla_completa = pd.DataFrame()

for categoria, url in categorias_urls:
    df_categoria = obtener_tabla_de_posiciones(url, categoria)
    if not df_categoria.empty:
        tabla_completa = pd.concat([tabla_completa, df_categoria], ignore_index=True)
        print(f"Tabla encontrada para {categoria}:\n", df_categoria)
    else:
        print(f"No se encontró tabla para {categoria}.")

if not tabla_completa.empty:
    actualizar_en_mongodb(tabla_completa)
    print("Datos actualizados en MongoDB.")
else:
    print("No se encontraron datos para actualizar en MongoDB.")
