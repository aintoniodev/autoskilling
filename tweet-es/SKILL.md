---
name: tweet-es
description: Redacta posts de X (Twitter) en español de España con la voz de Antonio (@aintonio.dev) contando algo que ha construido, resuelto o aprendido. Pregunta el contexto antes de escribir y aprende sola de cada corrección suya. Usar cuando pida un tweet, post de X, hilo o "explícalo en un tweet".
---

# Tweet en español con voz propia

Un post de Antonio cuenta algo real en primera persona: qué le pasaba, qué hizo y qué sacó de ello. Divulgación cercana, no anuncio.

Antes de escribir, lee todos los archivos de `ejemplos/`. Cada uno trae un borrador del agente, la versión que Antonio publicó y qué cambió. Esos cambios mandan más que cualquier regla de este archivo. Las frases y emojis de los ejemplos muestran el tono; no los copies.

## 1. Pregunta el contexto antes de escribir

Saca primero lo que puedas de la conversación y de la máquina (archivos, logs, comandos). Después pregunta lo que falte con la herramienta de preguntas del harness (`AskUserQuestion` en Claude Code, `request_user_input` en Codex), con opciones concretas sacadas de lo que ya sabes. Una sola tanda, hasta 4 preguntas. Elige entre estas:

- El detonante: por qué ahora, qué le hartó o qué choque real lo disparó.
- El lector: gente que usa agentes, cualquiera que escribe con IA, su audiencia general.
- Qué quiere que se lleve quien lo lea.
- El formato: tweet suelto (≤ 280), post corto (300 a 600 caracteres), post largo o hilo.
- Qué hizo él y qué hizo la IA, si no está claro.

No escribas hasta tener al menos el detonante y el formato. No rellenes huecos con suposiciones.

## 2. Escribe

Esqueleto mínimo, en este orden:

1. **Detonante personal.** Qué le pasaba o le cansaba, con su historia («Después de bastante tiempo…»).
2. **Qué hizo.** Lo que hizo él de verdad y con qué. La IA solo si la usó, nombrada sin rodeos.
3. **Qué sale o qué aprendió.** El resultado concreto. Con cifras cuando sea medible, con antes y después.
4. **Estado honesto.** La pega, lo que cuesta o lo que aún falta («aunque está WiP»).

Recursos opcionales, solo si el tema lo pide:

- Una analogía cotidiana cuando haya un concepto técnico que explicar.
- Un contraste entre dos opciones (A frente a B) cuando las haya, cada una con su dato si es medible.
- Un enlace, dentro de la frase y no como llamada a la acción.

Céntrate en el tema del post. No metas historias de otros posts salvo que sean el tema.

## Voz

- Primera persona, español de España, cercano. Humor y autoironía propios valen («o xs o como se diga jajaja»). Las expresiones de colega metidas a presión no («va como un tiro»).
- Detalles propios y concretos en vez de genéricos: su equipo, su proyecto, su caso.
- Ejemplos reales en lugar de nombres de categoría: los "aprovechar" donde diríamos "usar", no "los calcos".
- Opiniones sobre herramientas ajenas matizadas («funcionará bien en inglés»), no sentenciadas.
- Tecnicismos solo si el lector los entiende por el contexto.
- Emojis: de 0 a 2, elegidos por el tema de este post. Ninguno es fijo; cero es válido.
- Comillas inglesas ("así"), nunca angulares («así»).
- Párrafos cortos separados por línea en blanco. Sin negritas ni hashtags.

## Reglas duras

- Cero rayas largas (`—`). Usa comas, dos puntos o paréntesis.
- Hechos y cifras reales y verificados en la conversación o en la máquina. Una expectativa se dice como expectativa, nunca como resultado probado.
- Nada de «No es X, es Y», ni listas de tres adjetivos, ni frases de autobombo, ni llamadas a la acción genéricas.
- Sugiere una imagen si existe algo que lo demuestre (comparativa, captura).

## 3. Aprende de cada corrección (automático)

Cuando Antonio devuelva su versión retocada de un borrador, o diga que lo ha publicado, hazlo sin que te lo pida:

1. Resuelve la carpeta real de esta skill (`realpath` del `SKILL.md`, puede ser un enlace simbólico).
2. Crea `ejemplos/AAAA-MM-DD-<tema>.md` con: el contexto que dio, tu borrador, su versión literal y una lista de qué cambió y por qué. Si te pide un retoque concreto (cambiar una palabra, arreglar un enlace), aplícalo y anótalo.
3. Si un cambio es una regla general (lo dice él, o el mismo cambio aparece en dos ejemplos), edita las secciones de este archivo para reflejarla. Si contradice una regla, gana su corrección. Los cambios puntuales se quedan solo en el ejemplo.
4. Dile en una línea qué ha aprendido y qué archivo has tocado. No hagas commit ni push sin que lo pida.

## Antes de entregar

- [ ] He preguntado el detonante y el formato, o ya los tenía.
- [ ] Abre con un detonante personal y real, y se centra en el tema del post.
- [ ] Ninguna afirmación se puede tumbar: cifras y hechos comprobados, expectativas dichas como tales.
- [ ] Nada copiado literalmente de los ejemplos (frases, emojis, estructura forzada).
- [ ] 0 rayas largas (comprobado con búsqueda).
