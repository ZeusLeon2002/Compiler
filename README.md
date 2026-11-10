# C Code Compiler & Analyzer

Proyecto universitario para construir un analizador incremental de código C con editor gráfico.

## Ejecutar

Desde la raíz del repositorio:

```bash
python -m sample.main
```

También se puede iniciar con `python sample/main.py`. La aplicación requiere `customtkinter`.

## Estructura

- `sample/compiler_gui.py`: editor, archivos y presentación de resultados.
- `sample/lexer.py`: tokenización y diagnósticos léxicos con línea y columna.
- `sample/parser.py`: parser recursivo para declaraciones, funciones, bloques, sentencias frecuentes y expresiones.
- `sample/analyzers.py`: exportaciones de compatibilidad para el diccionario.
- `docs/dictionary.json`: palabras clave, operadores, directivas y traducciones.

El parser reconoce un subconjunto introductorio de C; todavía no es una implementación completa del estándar. Las construcciones que falten deben agregarse incrementalmente en `parser.py`.

Los archivos de configuración, logs y traducciones se localizan desde la raíz del proyecto, así que el directorio actual de la terminal no afecta esas rutas.

## Funciones actuales

- Crear, abrir y guardar archivos.
- Cambiar tema y fuente.
- Analizar tokens y sintaxis básica, con ubicación de errores.
- Generar una traducción de las palabras clave que tengan equivalente en el diccionario.
