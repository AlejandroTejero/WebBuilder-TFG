# Resumen reunion TFG 19/02
Implementar un llm al q se le pase el cotnenido, por ejemplo 40 lineas, y el sea capaz de parsearlas y devolverme el contenido suficiente para poder crear poco a poco la app de django
Quiza se podria adapatar a mis codigos y a mi forma de analizar, ver con que funciona mejor, si con ayuda de mi analisis o de forma independeiente

Descargar N8N en local para q sea gratis, e implementar todo el flujo posible ahi dentro, de forma que se vaya autoalimentando para crear el solo la app de django y si es capaz incluso
de desplegarla el solo.

Pensar en si es buena idea q cuando lea los datos, el llm sugiera un tipo de web que mas se adapate al contenido (blog, portfolio...), en este caso quiza si se pueda usar mi analisis,
pero tambien probrar con el llm solo sin ayuda de mi contenido. 
Probar tbm que el usuario ponga una pequeña descripcion para que el llm ajuste un poco el futuro de la pagina a como el quiere

Hacerme un esquema de lo que he hecho este primer mes, aunque haya cosas que no hayan servido, y apuntarme todo el contenido que investigo aunque no sirva, ya que me sirve para facilitarme la memoria


# Resumen para llm
El proyecto se basa en crear paginas de django adapatada cada tipo de datos que se introduzca y a como el usuario quiera que sea. En la antigua version yo parseaba los datos y sugeria un mapping segun el tipo de datos q se introdujeran, el principal problema era que al final yo hacia un mapping generico para todos los tipos de datos que entrasen, ya que era capaz de abarcar todo los datos posibles que existen, de tal forma que mi profe y yo hemos variado la forma del tfg, no me voy a encargar yo solo de la creacion de datos, sino que vamos a implementar una integligencia artificial/llm y tbm la aplicacion n8n, de tal forma que por ejemplo yo parsee los datos y se los pase a la ia, y esta adapate perfectamente los datos para cada caso de uno, el llm sugerira, tu tipo de datos tiene buena pinta para realizar un blog, un portfolio... y el usuario aqui metera un buen prompt explicnado q quiere y como lo quiere. La idea principal es ser capaz de desplegar la pagina final de forma que el usuario escriba lo menos necesario, de tal forma debere conectar mi app a la ia y a n8n para que entre los 3 se vaya siguiendo el curso necesario, que por ejemplo serian parsear, mapping, guardar, deplejar un docker django, seguir generando codigos, deplegar... ns, eso ya poco a poco ira surgiendo, pero es importante que la ia y n8n no se coman el tfg, porque sino entonces no hay nada que defender, todo lo hace la ia y n8n ns si me explico.

Hay partes de codigos que yo tenia en la antigua version que los elimine porque eran innecesarios, la cosa es, como seguimos ahora? adapto un poco los codigos q tengo, intento implementar la ia, como me sugieres q avancemos, comentame como lo ves el proyecto

