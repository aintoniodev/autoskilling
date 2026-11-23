# Post sobre la propia skill tweet-es

## Contexto que dio Antonio (preguntado con opciones)

- Detonante: /unslop no sirve en español.
- Lector: cualquiera que escribe con IA.
- Objetivo: que la pruebe y que se haga la suya.
- Formato: post corto o tweet suelto.

## Borrador del agente

Por fin me he hecho una skill para escribir en español con IA. Una skill es un archivo de instrucciones que el agente sigue cada vez que le pides algo.

La típica es /unslop, que quita lo que delata a la IA en inglés. En español se le escapan las rayas largas, el «no es X, es Y» y los calcos.

La mía, tweet-es, me pregunta el contexto antes de escribir y se ajusta con mis correcciones: le paso mi versión retocada y apunta qué cambié y por qué.

Pruébala o hazte la tuya: github.com/aintoniodev/autoskilling 🇪🇸

## Versión de Antonio

(El ejemplo de «aprovechar» y la ruta `/tree/main` del enlace los puso el agente a petición suya; el resto es literal.)

Después de bastante tiempo, por fin me he hecho una skill para escribir tweets (o xs o como se diga jajaja) en español con IA.

La típica de /unslop, funcionará bien en inglés, pero en español deja bastante que desear; se le escapan las rayas largas, el «no es X, es Y» y los «aprovechar» donde diríamos «usar».

De momento, aunque está WiP, github.com/aintoniodev/autoskilling/tree/main/tweet-es, me pregunta el contexto antes de escribir y se ajusta con mis correcciones: le paso mi versión retocada y apunta qué cambié y por qué.

## Qué cambió y por qué

- Abre con el tiempo que llevaba queriéndolo («Después de bastante tiempo»): el detonante tiene historia.
- Humor y autoironía propios («o xs o como se diga jajaja»). Le quita solemnidad.
- Opinión sobre la herramienta ajena matizada («funcionará bien en inglés»), no sentenciada.
- Pidió cambiar «los calcos» por un ejemplo concreto: nombres de categoría abstractos no, el caso real sí.
- Reconoce el estado del proyecto («aunque está WiP»).
- Quitó la definición de «skill», la llamada a la acción («Pruébala o hazte la tuya») y el emoji. El enlace va dentro de la frase. Cero emojis es válido.
- Pidió que el aprendizaje desde sus correcciones fuese automático, no solo cuando él lo pida.
