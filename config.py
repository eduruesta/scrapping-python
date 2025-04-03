# config.py

CATEGORIAS_URLS = [
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

# Selector CSS para la tabla de posiciones
CSS_SELECTOR = "tbody"  # selector CSS más específico

REQUIRED_KEYS = [
    "Pos","Club", "Logo",
    "Pts", "PJ", "PG", "PE", "PP", "SP",
    "GF", "GC", "DG", "Bo", "Sa"
]
