import json
import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from datetime import datetime, date
import tempfile
import shutil


def obtener_partidos(url, categoria):
    print(f"\n=== Accediendo a URL original: {url} para la categoría {categoria} ===")

    # Configuración de Chrome con un directorio de datos único
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Ejecutar en modo headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Crear un directorio temporal único para los datos del usuario
    user_data_dir = tempfile.mkdtemp(prefix='chrome_user_data_')
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Esperar a que la página cargue

        # Refrescar para aplicar las cookies
        driver.get(url)

        try:
            WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/section[3]/div/div/main/section[1]/section/div/table[2]"))
            )
            table = driver.find_element(By.XPATH, "/html/body/section[3]/div/div/main/section[1]/section/div/table[2]")
        except Exception as e:
            print(f"❌ No se encontró la tabla para {categoria}: {e}")
            driver.quit()
            return pd.DataFrame(), pd.DataFrame()

        html_content = table.get_attribute("outerHTML")
        driver.quit()
        print(f"✅ Tabla HTML obtenida para {categoria}")

        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')

        headers = ['Nro', 'Day', 'Fecha', 'nro_fecha', 'Local', 'LogoLocal',
                   'ResultadoLocal', 'ResultadoVisitante', 'Visitante', 'LogoVisitante', 'Categoria']

        data_last = []
        data_next = []
        equipo_a_buscar = 'SAN LUIS'
        fecha_actual_encabezado = None
        nro_fecha = 0

        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 1:
                strong_tag = cols[0].find('strong')
                if strong_tag:
                    texto = strong_tag.get_text(strip=True)
                    if 'Fecha N°' in texto:
                        fecha_actual_encabezado = texto.replace('Rueda N° ', 'R ').strip()
                        nro_fecha += 1
                continue

            if len(cols) == 7 and fecha_actual_encabezado:
                nro = cols[0].get_text(strip=True)
                day_str = cols[1].get_text(strip=True)
                local_name = cols[2].get_text(strip=True)
                visitante_name = cols[5].get_text(strip=True)

                logo_local_url = urljoin(url, cols[2].find('img')['src']) if cols[2].find('img') else None
                logo_visitante_url = urljoin(url, cols[5].find('img')['src']) if cols[5].find('img') else None

                resultado_local = cols[3].get_text(strip=True)
                resultado_visitante = cols[4].get_text(strip=True)

                if equipo_a_buscar in local_name or equipo_a_buscar in visitante_name:
                    try:
                        match_date = datetime.strptime(day_str, "%d/%m/%Y").date()
                    except Exception as e:
                        print(f"⚠️ Error al parsear fecha {day_str} en partido {nro}: {e}")
                        continue

                    match = [nro, day_str, fecha_actual_encabezado, nro_fecha, local_name, logo_local_url,
                             resultado_local, resultado_visitante, visitante_name, logo_visitante_url, categoria]

                    if match_date < date.today():
                        data_last.append(match)
                    elif match_date > date.today():
                        data_next.append(match)
                    else:
                        if resultado_local or resultado_visitante:
                            data_last.append(match)
                        else:
                            data_next.append(match)

        df_last = pd.DataFrame(data_last, columns=headers)
        df_next = pd.DataFrame(data_next, columns=headers)
        print(f"✅ {len(df_last)} partidos jugados y {len(df_next)} próximos partidos encontrados para {categoria}")
        return df_last, df_next

    finally:
        # Limpiar el directorio temporal después de usar
        try:
            driver.quit()
            shutil.rmtree(user_data_dir)
        except:
            pass


def actualizar_en_mongodb(df, collection_name):
    print(f"📦 Actualizando MongoDB en colección '{collection_name}'...")
    client = MongoClient("mongodb+srv://bebiruesta90:Bebiwing11@mycluster.vheby.mongodb.net/")
    db = client['maristapp']
    collection = db[collection_name]

    if collection_name == 'hockey_team_next_matches':
        today_str = datetime.now().strftime("%d/%m/%Y")
        result = collection.delete_many({"day": {"$lte": today_str}})
        print(f"🧹 Eliminados {result.deleted_count} documentos antiguos (<= {today_str})")

    for _, row in df.iterrows():
        partido_id = f"{row['Categoria'].replace(' ','')}_{row['Fecha'].replace(' ','')}_{row['Day'].replace('/','')}_{row['Local'].replace(' ','')}_{row['Visitante'].replace(' ','')}"
        partido = {
            '_id': partido_id,
            'category': row['Categoria'],
            'date': row['Fecha'],
            'nro_fecha': row['nro_fecha'],
            'day': row['Day'],
            'local_team': {
                'name': row['Local'],
                'result': row['ResultadoLocal'],
                'logo': row['LogoLocal']
            },
            'visiting_team': {
                'name': row['Visitante'],
                'result': row['ResultadoVisitante'],
                'logo': row['LogoVisitante']
            }
        }
        collection.update_one({'_id': partido_id}, {'$set': partido}, upsert=True)
    print(f"✅ {len(df)} documentos actualizados en '{collection_name}'")


# URLs de categorías
categorias_urls = [
    ('Primera A', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=1&nombre_torneo=144&subdivision=2'),
    ('Intermedia A', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=2&nombre_torneo=144&subdivision=2'),
    ('Quinta A', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=3&nombre_torneo=144&subdivision=2'),
    ('Sexta A', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=4&nombre_torneo=144&subdivision=2'),
    ('Séptima A', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=5&nombre_torneo=144&subdivision=2'),
    ('Primera B', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=1&nombre_torneo=105&subdivision=27'),
    ('Intermedia B', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=2&nombre_torneo=105&subdivision=27'),
    ('Quinta B', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=3&nombre_torneo=105&subdivision=27'),
    ('Sexta B', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=4&nombre_torneo=105&subdivision=27'),
    ('Séptima B', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=5&nombre_torneo=105&subdivision=27'),
    ('Primera C', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=1&nombre_torneo=99&subdivision=46'),
    ('Intermedia C', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=2&nombre_torneo=99&subdivision=46'),
    ('Quinta C', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=3&nombre_torneo=99&subdivision=46'),
    ('Sexta C', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=4&nombre_torneo=99&subdivision=46'),
    ('Séptima C', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=5&nombre_torneo=99&subdivision=46'),
    ('Cuarta', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=10&nombre_torneo=134&subdivision=65'),
    ('Segunda', 'https://www.ahba.com.ar/club.php?id=173&seccion=FIXTURE&genero=2&categoria=9&nombre_torneo=5&subdivision=65')
]

df_last_total = pd.DataFrame()
df_next_total = pd.DataFrame()

for categoria, url in categorias_urls:
    df_last, df_next = obtener_partidos(url, categoria)
    if not df_last.empty:
        df_last_total = pd.concat([df_last_total, df_last], ignore_index=True)
    if not df_next.empty:
        df_next_total = pd.concat([df_next_total, df_next], ignore_index=True)

if not df_last_total.empty:
    actualizar_en_mongodb(df_last_total, 'hockey_team_last_matches')
else:
    print("⚠️ No se encontraron partidos jugados en ninguna categoría.")

if not df_next_total.empty:
    actualizar_en_mongodb(df_next_total, 'hockey_team_next_matches')
else:
    print("⚠️ No se encontraron partidos futuros en ninguna categoría.")
