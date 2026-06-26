## Estructura de archivos

- Ejemplos de árboles de decisión pre-generados dentro de `examples/`

## Estructura del árbol de decisión

- Modelo Pydantic `SimulatorTree` en `schema/tree.py` para definir la estructura del árbol de decisión (testing con ejemplos en `tests_schema.py`)
- Agregamos la función `resolve()` dentro del modelo `SimulatorTree` en `schema/tree.py` para más adelante poder tomar la referencia a un nodo y regresar el nodo tal cual

## Arquitecto: Claude LLM para generar árbol

- Prompt de sistema del arquitecto en `architect/prompt.md`
- Llamada al arquitecto en `architect/generator.py` para generar el árbol de decisiones JSON
    - Utiliza el prompt de sistema (que incluye los ejemplos pre-generados)
    - Utiliza Claude API como LLM (Sonnet 4.6)
    - __name__ guard para poder probar y correr directamente `generator.py` desde el prompt de la terminal con `python -m architect.generator "Quiero un simulador...”`
    - La estructura del árbol parece funcionar perfectamente en las pruebas
    - El LLM podría llegar a generar contenido de dominio impreciso (tendría que ser avalada por profesionales del tema)
    - Sonnet 4.6 parece ser muy bueno generando contenido en las pruebas (a cambio de que sea lento a la hora de generar los árboles)
- El árbol generado se guarda automáticamente en `generated_trees/`
- Como excepción, guardamos dos de los mejores ejemplos generados por el arquitecto en `examples/arch_generated` para utilizarlos como referencia a la hora de generar el ejecutor
    - `cybersecurity.json` — prompt para generarlo: Un simulador para entrenar a analistas de seguridad informática en la respuesta a incidentes de ransomware en entornos empresariales.
    - `hvac.json` — prompt para generarlo: Quiero un simulador para diagnosticar problemas en sistemas de refrigeración industrial, orientado a técnicos de mantenimiento HVAC.

## Ejecutor del caso: Groq LLM para interpretar la consulta de usuario + Código determinista para componer la respuesta y avanzar el caso

- En `executor/models.py` : Modelos Pydantic para definir la estructura encargada del estado por turno y para la estructura de la capa de interpretación
- Capa de interpretación (clasificación de consulta y registro de matches con Groq LLM) dentro de `executor/llm_interpretation.py`
    - Llamada a Groq LLM con el modelo Llama 3.3 70B (mejor soporte multilingual pero requiere loop de validación) o GPT-OSS 120B (soporte para strict structure outputs)
    - Tarea por turno (descrita en prompt de sistema): toma el prompt del usuario, lo compara semánticamente con campos relevantes del nodo actual y regresa la interpretación en forma de objeto JSON
    - Inputs:
        - El prompt de sistema `executor/system_prompt.md` (se ejecuta una sola vez): donde se describe la tarea
        - El prompt del usuario construido dentro de `executor/user_message.py` (se ejecuta/cambia en cada turno): Aquí se recibe la consulta del usuario pero también el nodo actual, el historial de conversación reciente, partes relevantes del estado y `hint_path_def` + `off_path_def`
    - Output: el objeto de interpretación JSON que incluye:
        - La clasificación de la consulta del usuario (si hubo match con las acciones esperadas/componentes requeridos, o si una pista es necesaria, o si se fue off path)
        - Si hubo match, registro de cuál/cuales
        - Breve reflexión para debugging futuro
- Código determinista para componer la respuesta en `executor/response_composer.py`
    - Diferente respuesta dependiendo de si hubo decision node action match, accumulator component match, hint needed, going off path o terminal node
- Código determinista responsable de procesar cada turno/actualizar el estado en `executor/runner.py` : `process_turn()`
    - Captura los valores pre-transición (nodo y estado), ya que son necesarios
    - Llama a la interpretación del LLM, obteniendo así la clasificación de la consulta del usuario
    - Aplica nuevos valores al estado (marcando transición de turno) y actualiza la respuesta, dependiendo de la clasificación del interpretador
    - Adjunta el input del usuario y la respuesta al historial de conversación
- Loop que corre el simulador en `executor/runner.py` : `run_simulator()`
    - + funciones adyacentes restantes: `print_presentation()`, `print_node_intro()`, `save_session()` (salva la sesión para debugging futuro)
    - La función utiliza las funciones adyacentes, toma el input del usuario y llama a `process_turn()` para que se haga cargo del turno
    - El loop termina una vez que `process_turn()` marca `is_terminated` como `True` en el estado
    - Al terminar se guarda la sesión en `sessions/`
    - El usuario puede salir al escribir `/exit` o `/quit`

## `app.py` para llamar a arquitecto y ejecutor

- Toma el prompt del usuario para generar el árbol
- Presenta datos básicos del árbol y pregunta al usuario si quiere continuar
- Ejecuta el caso
