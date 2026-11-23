# Ejemplo de referencia (versión final escrita por Antonio)

Para la jubilación de mi padre hemos montado un vídeo de 41 minutos con mensajes de familia, amigos y compañeros de trabajo. Salió de 2,8 GB y, al querer compartirlo por telegram, me pedía el premium por >2gb

 Le he pedido a Opus que lo reduzca y lo ha dejado, en la primera pasada, en 1,9 GB. Sin que se note. 🤓

Evidentemente, le he preguntado por el el truco: cambiar quién comprime.

Resulta que un vídeo no guarda cada fotograma entero. Guarda lo que cambia de uno al siguiente: si alguien habla delante de una pared, la pared se describe una vez y se reutiliza. Cuanto mejor busca el compresor esas repeticiones, menos pesa.

La primera versión la sacó la 2060 RTX que tengo de GPU. Va mucho más rápido (pocos minutos), pero busca con prisa y necesita más datos para la misma imagen: 8,9 megabits por segundo.

La segunda la hizo el procesador con x264, en dos pasadas. En la primera recorre el vídeo entero y apunta qué escenas son fáciles y cuáles difíciles. En la segunda comprime con ese mapa: pocos datos en los planos quietos y más donde hay movimiento. Resultado: 6,1 megabits por segundo.

¿Pierde calidad? Se supone que sí, algo, porque recomprimes algo ya comprimido. Comparando fotograma a fotograma los 10 primeros minutos sale un 99,6 % de similitud con el original, y por encima del 99 % el ojo no ve la diferencia.

Ha sido una hora de procesador en lugar de unos minutos de gráfica, pero para algo que vas a guardar o compartir, compensa 🙌

## Qué cambió Antonio respecto al borrador del agente (y por qué importa)

- Añadió el problema real que lo disparó (Telegram pide premium por encima de 2 GB). El borrador no tenía motivo.
- Dijo abiertamente que se lo pidió a Opus y que luego le preguntó por el truco: el post cuenta un proceso, no presume de saber.
- Cambió «la tarjeta gráfica» por «la 2060 RTX que tengo de GPU»: detalle propio.
- Quitó la jerga forzada («va como un tiro», «:O») por frases normales.
- Cambió «sobre el papel» por «se supone que sí, algo»: matiz más humano.
- Fundió el cierre en una frase con «pero» en lugar de «El peaje: …».
