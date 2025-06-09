Este proyecto consiste en el diseño e implementación de un Sistema de Recuperación de Información (SRI) que opera sobre un corpus de documentos en texto plano. Su objetivo principal es permitir la ejecución de consultas de texto libre mediante el uso del modelo vectorial, con soporte tanto para la ponderación TF-IDF como para el modelo BM25. El sistema realiza un preprocesamiento básico del texto, incluyendo tokenización, normalización y eliminación de palabras vacías, para posteriormente construir un índice invertido que almacena la frecuencia de cada término por documento. A través de una interfaz de línea de comandos (CLI), el usuario puede ingresar consultas y visualizar un ranking de documentos ordenados por relevancia según la métrica seleccionada. Además, el sistema permite evaluar la calidad de los resultados obtenidos, mediante la comparación con un conjunto de relevancia (qrels), utilizando métricas estándar como precisión, recall y Mean Average Precision (MAP). Esta herramienta proporciona una base funcional para el análisis y evaluación de técnicas clásicas de recuperación de información.

📹 Video demostrativo
https://teams.microsoft.com/l/meetingrecap?driveId=b%21f6yt-IKpsEixsOs1ZFn35pBy5_ORzC1PrDgg5kbn8HE4pZg3aRxIQ7wC73j0DQgT&driveItemId=017YQT2GDBXST4WGWCO5F3ZQZS5PQ4TBUQ&sitePath=https%3A%2F%2Fepnecuador-my.sharepoint.com%2F%3Av%3A%2Fg%2Fpersonal%2Fluis_bolanos01_epn_edu_ec%2FEWG8p8sawndLvMMy6-HJhpABv6x4P6g1NIVPTvKTi38qiw&fileUrl=https%3A%2F%2Fepnecuador-my.sharepoint.com%2Fpersonal%2Fluis_bolanos01_epn_edu_ec%2FDocuments%2FGrabaciones%2FLlamada%2520con%2520ANDRES%2520y%25201%2520m%25C3%25A1s-20250609_010149-Grabaci%25C3%25B3n%2520de%2520la%2520reuni%25C3%25B3n.mp4%3Fweb%3D1&threadId=19%3A649f38e5767a427faf145635b39f262a%40thread.v2&callId=e7fe4f10-3339-4bae-b9a3-bb82ef4642a0&threadType=GroupChat&meetingType=Unknown&subType=RecapSharingLink_RecapCore

📄 Informe técnico
https://epnecuador-my.sharepoint.com/:b:/g/personal/sonia_silva_epn_edu_ec/ES4W5uQSELNNqH9YfUcIQ9MB2Y_zr98Uemmmr83NAvJdOw?e=20WDkJ

# Sistema de Recuperación de Información

##Requisitos:
* Python
* Node.js + npm
* Angular CLI (npm install -g @angular/cli)

##Cómo ejecutar el backend:
1. Entra a la carpeta back/
2. Instalar las dependencias pip install -r requirements.txt
3. Ejecutar el backend python back.py
4. De manera general, El backend se levanta en http://localhost:3000

##Cómo ejecutar el front:
1. Entra a la carpeta project/
2. npm install
3. ng serve
4. Generalmente, desde el navegador se despliega en el http://localhost:4200
