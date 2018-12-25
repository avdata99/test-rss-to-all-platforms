#!/usr/bin/env python
""" 
Crear y publicar un archivo XML con el RSS para podcast que sea compatible con las plataformas más usadas 
Usa como parámetro único el directorio con los audios en MP3
"""

__author__ = "Andrés Vázquez"
__credits__ = ["Andrés Vázquez", "Ivo Dionisio Vázquez"]
__license__ = "GPL"
__version__ = "0.0.001"
__maintainer__ = "Andrés Vázquez"
__email__ = "andres@data99.com.ar"
__status__ = "Beta"

import sys
import os
from termcolor import colored
import json
from jinja2 import Template

# el primer parámetro de la llamada debe indicar la carpeta donde buscar
directorio = sys.argv[1]
mp3s = []
# todos los links publicos en la web dependeran de una misma base dependiendo de donde se publique este código
base_url = 'https://avdata99.github.io/test-rss-to-all-platforms'

"""
dentro del directorio se espera que estén:
 - Los audios en formato MP3
 - Una imagen por cada audio con el mismo nombre de archivo que el MP3 pero con extensión PNG o JPG
 - Un archivo JSON con datos del episodio
 - Un archivo de información llamado info.json con datos del PODCAST en general
"""

# leer los datos del podcast
canal_info_file = '{}/info.json'.format(directorio)
canal_data_file = open(canal_info_file)
# guardar en un diccionario todo lo que dice el archivo info.json
canal_info = json.load(canal_data_file)

# fecha de ultima compilacion (ahora)
canal_info['ultima_compilacion'] = ''

# buscar todos los archivos MP3s y guardarlos en una lista
for filename in os.listdir(directorio):
    if filename.endswith('.mp3'):
        print('Archivo encontrado {}'.format(filename))
        mp3s.append(filename)

# para simplificar este proceso se espera que la imagen y la info estén en archivos con identico nombre pero diferente extensión
# imagen: jpg o png
# info del episodio: JSON

# guardar todo en un diccionario más elaborado
canal_info['items'] = [] # cada episodio se contruye revisando sus datos en diccionarios individuales

for mp3 in mp3s:

    # contruir el episodio de una propiedad a la vez
    # AUDIO del episodio -----------------------------
    url_mp3 = '{}/{}/{}'.format(base_url, directorio, mp3)
    episodio = {'url_audio': url_mp3}
    file_mp3 = '{}/{}'.format(directorio, mp3)
    episodio['audio_size_bytes'] = os.path.getsize(file_mp3)

    # IMAGEN del episodio -----------------------------
    base_name = mp3.replace('.mp3', '')
    extensiones_imagenes_aceptadas = ['png', 'jpg']
    imagen_encontrada = None

    for ext in extensiones_imagenes_aceptadas:
        imagen = '{}/{}.png'.format(directorio, base_name)
        if os.path.isfile(imagen):
            imagen_encontrada = imagen
    
    if imagen_encontrada is None:
        print(colored('No se encontro la imagen de {}'.format(base_name), 'red'))
        sys.exit(1)
    else:
        print(colored('Se encontro la imagen de {}'.format(base_name), 'green'))

    url_imagen = '{}/{}/{}'.format(base_url, directorio, imagen_encontrada)
    episodio['url_imagen'] = url_imagen

    # INFO del episodio -----------------------------
    datos_episodio = '{}/{}.json'.format(directorio, base_name)
    if not os.path.isfile(datos_episodio):
        print(colored('No se encontraron los datos del episodio {}'.format(base_name), 'red'))
        sys.exit(1)

    # abrir el archivo JSON, tomar todas sus propiedades y sumarlas (update) a este diccionario
    data_file = open(datos_episodio)
    episodio.update(json.load(data_file))

    print('-------------------------------------')
    nice_json = json.dumps(episodio, indent=4)
    print('EPISODIO LISTO {}'.format(nice_json))
    print('-------------------------------------')

    canal_info['items'].append(episodio)

# ya tengo todas las variables de contexto para aplicar al template
# aplicarla a todos los templates disponibles en la carpeta templates
template_file = 'templates/basic.xml.tpl'

for filename in os.listdir('templates'):
    if filename.endswith('.tpl'):
        print('Template encontrado {}'.format(filename))
        base_template = filename.replace('.tpl', '')
        tpl = open('templates/{}'.format(filename))
        template = Template(tpl.read())
        tpl.close()
        rss = template.render(canal_info)

        # escribir los resultados en un archivo llamado podcast.xml
        file_resultado = open('{}/podcast_{}'.format(directorio, base_template), 'w')
        file_resultado.write(rss)
        file_resultado.close()

        url_rss = '{}/{}/podcast_{}'.format(base_url, directorio, base_template)
        print(colored('Se genero RSS para {}. Una vez subido el feed a compartir estará en el link {}'.format(base_template, url_rss), 'green'))



