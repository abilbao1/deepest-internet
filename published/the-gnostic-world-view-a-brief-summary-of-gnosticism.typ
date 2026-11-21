#import "@preview/droplet:0.3.1": dropcap

#set page(
  paper: "a5",
  fill: rgb("#fbf8f1"),
  margin: (top: 2.2cm, bottom: 2.2cm, left: 2cm, right: 2cm),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(font: "Georgia", size: 8pt, fill: rgb("#7d756c"), style: "italic")
      #smallcaps[gnosis.org] #h(1fr) Semilla: gnosticism
      #v(2pt)
      #line(length: 100%, stroke: 0.4pt + rgb("#dcd4c6"))
    ]
  },
  footer: context [
    #set text(font: "Georgia", size: 8.5pt, fill: rgb("#7d756c"))
    #align(center)[— #counter(page).display("1") —]
  ]
)

#set text(
  font: "Georgia",
  size: 10.2pt,
  fill: rgb("#1d1b18"),
  lang: "es",
)

#set par(
  justify: true,
  leading: 0.78em,
  spacing: 1.35em,
)

// --- Cabecera Editorial ---
#align(center)[
  #set par(justify: false)
  #set text(hyphenate: false)
  #text(size: 8.5pt, fill: rgb("#7a2821"), tracking: 0.18em, weight: "bold")[
    ARCHIVO DEEPEST INTERNET · SEMILLA: #upper[gnosticism]
  ]
  #v(0.6em)
  #text(size: 18pt, weight: "bold", fill: rgb("#161412"))[La cosmovisión gnóstica: un breve resumen del gnosticismo]
  #v(0.3em)
  #if "The Gnostic World View: A Brief Summary of Gnosticism" != "" [
    #text(size: 10pt, style: "italic", fill: rgb("#635c54"))[(The Gnostic World View: A Brief Summary of Gnosticism)]
  ]
  #v(0.8em)
  #line(length: 45%, stroke: 0.8pt + rgb("#7a2821"))
  #v(0.4em)
  #text(size: 8pt, fill: rgb("#635c54"))[
    Fuente original: #raw("http://www.gnosis.org/gnintro.htm")
  ]
  #if "Copyright Estándar (Stephan A. Hoeller / The Gnosis Archive) — Para Twitter/X se recomienda publicar selección de fragmentos/citas comentadas bajo Derecho de Cita con enlace al original." != "" [
    #linebreak()
    #text(size: 7.5pt, fill: rgb("#7a2821"), style: "italic")[Copyright Estándar (Stephan A. Hoeller / The Gnosis Archive) — Para Twitter/X se recomienda publicar selección de fragmentos/citas comentadas bajo Derecho de Cita con enlace al original.]
  ]
  #v(1.2em)
]

#dropcap(height: 3, gap: 6pt, weight: "bold")[EL GNOSTICISMO ES LA ENSEÑANZA basada en la Gnosis, el conocimiento de la trascendencia al que se llega por medios interiores e intuitivos. Aunque el gnosticismo descansa así en la experiencia religiosa personal, es un error suponer que toda experiencia de esa índole desemboque en reconocimientos gnósticos. Es más cercano a la verdad decir que el gnosticismo expresa una experiencia religiosa específica: una experiencia que no se presta al lenguaje de la teología o de la filosofía, sino que guarda una estrecha afinidad con el mito y se expresa a través de él. De hecho, uno descubre que la mayoría de las escrituras gnósticas adoptan la forma de mitos. El término «mito» no debe entenderse aquí como «historias que no son ciertas», sino más bien en el sentido de que las verdades encarnadas en estos mitos pertenecen a un orden distinto al de los dogmas de la teología o los enunciados de la filosofía.]

En las páginas siguientes intentaremos condensar en prosa lo que los mitos gnósticos expresan en su lenguaje distintivamente poético e imaginativo.

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— El Cosmos —]]
#v(0.5em)

Todas las tradiciones religiosas reconocen que el mundo es imperfecto. Donde difieren es en las explicaciones que ofrecen para dar cuenta de esta imperfección y en lo que sugieren que podría hacerse al respecto. Los gnósticos tienen su propia visión —quizá bastante sobrecogedora— sobre estos asuntos: sostienen que el mundo es defectuoso porque fue creado de una manera defectuosa.

Al igual que el budismo, el gnosticismo comienza con el reconocimiento fundamental de que la vida terrenal está colmada de sufrimiento. Para nutrirse, todas las formas de vida se devoran unas a otras, infligiéndose así dolor, miedo y muerte (incluso los animales herbívoros viven destruyendo la vida de las plantas). Además, las llamadas catástrofes naturales —terremotos, inundaciones, incendios, sequías, erupciones volcánicas— traen consigo más sufrimiento y muerte a su paso. El ser humano, con su compleja fisiología y psicología, no solo es consciente de estos dolorosos rasgos de la existencia terrenal: también padece el frecuente reconocimiento de ser un extranjero que habita en un mundo fallido y absurdo.

Muchas religiones sostienen que se debe culpar a los seres humanos por las imperfecciones del mundo. En apoyo de esta postura, interpretan que el mito del Génesis declara que las transgresiones cometidas por la primera pareja humana provocaron una «caída» de la creación que desembocó en el actual estado corrupto del mundo. Los gnósticos responden que esta interpretación del mito es falsa. La culpa de los fracasos del mundo no recae en los humanos, sino en el creador. Puesto que —especialmente en las religiones monoteístas— el creador es Dios, esta posición gnóstica parece blasfema y a menudo es contemplada con consternación incluso por los no creyentes.

Una y otra vez se han ideado subterfugios para eludir el reconocimiento de una creación defectuosa y de su defectuoso creador, pero ninguno de estos argumentos ha impresionado a los gnósticos. Los antiguos griegos, en especial los platónicos, aconsejaban mirar hacia la armonía del universo, de modo que al venerar su grandeza los hombres pudieran olvidar sus aflicciones inmediatas. Pero dado que esa armonía sigue conteniendo las crueles taras, el desamparo y la alienación de la existencia, los gnósticos consideran que tal consejo es de escaso valor. Tampoco la idea oriental del Karma es considerada por los gnósticos como una explicación adecuada de la imperfección y el sufrimiento de la creación. El Karma, en el mejor de los casos, solo puede explicar cómo funciona el encadenamiento del sufrimiento y la imperfección; pero no nos explica, en primer término, por qué habría de existir un sistema tan lúgubre y maligno.

Una vez que se disipa la conmoción inicial ante el carácter «insólito» o «blasfemo» de la explicación gnóstica del sufrimiento y la imperfección del mundo, uno puede empezar a reconocer que es, de hecho, la más sensata de todas las explicaciones. Para apreciarla en su plenitud, sin embargo, se requiere cierta familiaridad con la concepción gnóstica de la Divinidad [Godhead], tanto en su esencia original como Dios Verdadero cuanto en su manifestación degradada como Dios falso o creador.

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— La Deidad —]]
#v(0.5em)

El concepto gnóstico de Dios es más sutil que el de la mayoría de las religiones. A su manera, une y concilia las intuiciones del monoteísmo y el politeísmo, así como las del teísmo, el deísmo y el panteísmo.

Desde la perspectiva gnóstica, existe un Dios verdadero, último y trascendente, que está más allá de todos los universos creados y que jamás creó nada en el sentido en que ordinariamente se entiende el verbo «crear». Si bien este Dios Verdadero no fabricó ni creó nada, Él (o Ello) «emanó» o hizo brotar desde su propio interior la sustancia de todo cuanto existe en todos los mundos, visibles e invisibles. En cierto sentido, por tanto, puede ser verdad afirmar que todo es Dios, pues todo consiste en la sustancia de Dios. Por esa misma razón, debe reconocerse también que muchas porciones de la esencia divina original han sido proyectadas tan lejos de su fuente que sufrieron alteraciones perniciosas en el proceso. Adorar al cosmos, a la naturaleza o a las criaturas encarnadas equivale, pues, a adorar porciones alienadas y corruptas de la esencia divina emanada.

El mito gnóstico fundamental presenta numerosas variantes, pero todas ellas aluden a los Eones, seres deíficos intermedios que existen entre el Dios verdadero y último y nosotros mismos. Ellos, junto con el Dios Verdadero, conforman el reino de la Plenitud (Pléroma), donde la potencia de la divinidad opera íntegramente. La Plenitud contrasta con nuestro estado existencial, que en comparación puede denominarse vaciedad (Kénoma).

Uno de los seres eónicos, que lleva el nombre de Sofía («Sabiduría»), reviste enorme importancia para la cosmovisión gnóstica. En el curso de sus peregrinaciones, Sofía llegó a emanar de su propio ser una conciencia defectuosa: una entidad que se convirtió en el creador del cosmos material y psíquico, todo lo cual modeló a imagen de su propia falta. Este ser, ignorante de sus orígenes, se imaginó a sí mismo como el Dios último y absoluto. Dado que tomó la esencia divina ya existente y la moldeó en diversas formas, se le llama también Demiurgos o «medio-hacedor». Existe una mitad auténtica, un verdadero componente deífico dentro de la creación, pero no es reconocido por el medio-hacedor ni por sus esbirros cósmicos, los Arcontes o «gobernantes».

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— El Ser Humano —]]
#v(0.5em)

La naturaleza humana refleja la dualidad que se halla en el mundo: en parte fue fabricada por el falso Dios creador y en parte consiste en la luz del Dios Verdadero. La humanidad alberga un componente físico y psíquico perecedero, así como un componente espiritual que es un fragmento de la esencia divina. A esta última parte se la denomina a menudo simbólicamente la «chispa divina». El reconocimiento de esta doble naturaleza del mundo y del ser humano le ha valido a la tradición gnóstica el epíteto de «dualista».

Los seres humanos suelen ignorar la chispa divina que reside en su interior. Esta ignorancia es alentada en la naturaleza humana por el influjo del falso creador y sus Arcontes, empeñados conjuntamente en mantener a hombres y mujeres en la ignorancia de su verdadera naturaleza y destino. Todo aquello que nos mantiene apegados a las cosas terrenales sirve para perpetuar nuestra esclavitud bajo estos gobernantes cósmicos inferiores. La muerte libera a la chispa divina de su humilde prisión, pero si el alma no ha emprendido una obra sustancial de Gnosis antes de morir, es probable que la chispa divina sea arrojada de nuevo a los dolores y la servidumbre del mundo físico para reencarnarse en él.

No todos los seres humanos son espirituales (pneumáticos) y, por ende, dispuestos para la Gnosis y la liberación. Algunos son seres terrenales y materialistas (hiléticos), que solo reconocen la realidad física. Otros viven primordialmente en su psique (psíquicos); tales personas suelen confundir al Demiurgo con el Dios Verdadero y tienen escasa o nula conciencia del mundo espiritual más allá de la materia y la mente.

En el transcurso de la historia, el ser humano progresa desde la esclavitud materialista de los sentidos, pasando por la religiosidad ética, hacia la libertad espiritual y la Gnosis liberadora. Como escribió el estudioso G. Quispel: «El espíritu del mundo en el exilio debe atravesar el Infierno de la materia y el Purgatorio de la moral para arribar al Paraíso espiritual». Esta evolución de la conciencia fue concebida por los gnósticos mucho antes de que se conociera el concepto moderno de evolución.

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— La Salvación —]]
#v(0.5em)

Las fuerzas evolutivas por sí solas son, no obstante, insuficientes para consumar la libertad espiritual. Los seres humanos se hallan atrapados en una encrucijada compuesta por la existencia física combinada con la ignorancia de sus verdaderos orígenes, su naturaleza esencial y su destino último. Para liberarse de esta condición, el ser humano precisa auxilio, aunque también debe aportar su propio empeño.

Desde los tiempos más remotos, Mensajeros de la Luz han descendido desde el Dios Verdadero para asistir a los humanos en su búsqueda de la Gnosis. Solo unas pocas de estas figuras salvíficas se mencionan en las escrituras gnósticas; entre las más importantes se cuentan Set (el tercer hijo de Adán), Jesús y el profeta Mani. La mayoría de los gnósticos contempló siempre a Jesús como la figura salvadora principal (el Sóter).

Los gnósticos no buscan la salvación del pecado (original o de otra índole), sino de la ignorancia de la cual el pecado es consecuencia. La ignorancia —entendida como ignorancia de las realidades espirituales— solo es disipada por la Gnosis, y la revelación decisiva de la Gnosis es traída por los Mensajeros de la Luz, muy especialmente por Cristo, el Logos del Dios Verdadero. No es por Su sufrimiento y muerte, sino por Su vida de enseñanza y Su instauración de misterios, que Cristo ha consumado Su obra de salvación.

El concepto gnóstico de salvación, al igual que otros conceptos gnósticos, es sutil. Por un lado, la salvación gnóstica puede confundirse fácilmente con una experiencia individual sin mediaciones, una suerte de proyecto espiritual de «hágalo usted mismo». Los gnósticos sostienen que el potencial para la Gnosis —y, por tanto, para la salvación— está presente en cada hombre y mujer, y que la salvación no es vicaria sino individual. Al mismo tiempo, reconocen también que la Gnosis y la salvación pueden, y de hecho deben, ser estimuladas y facilitadas para brotar efectivamente en la conciencia. Este estímulo lo proveen los Mensajeros de la Luz, quienes, además de sus enseñanzas, instituyen misterios salvíficos (sacramentos) que pueden ser administrados por los apóstoles de los Mensajeros y sus sucesores.

Es menester recordar asimismo que el conocimiento de nuestra verdadera naturaleza —así como otras comprensiones afines— nos es escamoteado por nuestra propia condición de existencia terrenal. El Dios Verdadero de la trascendencia es desconocido en este mundo; de hecho, a menudo se le llama el Padre Desconocido. Resulta obvio, por consiguiente, que se requiere una revelación desde lo Alto para hacer posible la salvación. La chispa interior debe ser despertada de su letargo terrestre por el conocimiento salvífico que viene «desde afuera».

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— La Conducta —]]
#v(0.5em)

Si por las palabras «ética» o «moralidad» se entiende un sistema de reglas, entonces el gnosticismo se opone a ambas. Tales sistemas suelen originarse en el Demiurgo y están diseñados encubiertamente para servir a sus designios. Si, por el contrario, se afirma que la moralidad consiste en una integridad interior que brota de la iluminación de la chispa interna, entonces el gnóstico abrazará como ideal esta ética existencial espiritualmente informada.

Para el gnóstico, los mandamientos y las reglas no son salvíficos; no conducen sustancialmente a la salvación. Las normas de conducta pueden servir a numerosos fines, incluida la estructuración de una sociedad ordenada y pacífica y el mantenimiento de relaciones armoniosas dentro de los grupos sociales. Sin embargo, las reglas son irrelevantes para la salvación: esta solo se alcanza mediante la Gnosis. Por lo tanto, la moralidad debe contemplarse primordialmente en términos temporales y seculares; está siempre sujeta a cambios y modificaciones de acuerdo con el desarrollo espiritual del individuo.

Como se señaló anteriormente, los «materialistas hiléticos» suelen tener escaso interés por la moralidad, mientras que los «disciplinarios psíquicos» a menudo le conceden una importancia desmesurada. En contraste, las personas «espirituales pneumáticas» suelen ocuparse de asuntos más elevados. Los distintos períodos históricos exigen también actitudes diversas respecto de la conducta humana. Así, tanto el movimiento gnóstico maniqueo como el cátaro, que operaron en épocas donde la pureza de conducta era considerada una cuestión de suma importancia, respondieron en consonancia. El período actual de la cultura occidental se asemeja quizá en muchos más sentidos a la Alejandría de los siglos II y III. Parece apropiado, por ende, que los gnósticos de nuestra era adopten las actitudes del gnosticismo alejandrino clásico, en el cual las cuestiones de conducta se dejaban en gran medida a la intuición del individuo.

El gnosticismo abraza numerosas actitudes generales ante la vida: alienta el desapego y la inconformidad frente al mundo —un «estar en el mundo, pero no ser del mundo»—, la ausencia de egoísmo y el respeto por la libertad y la dignidad de los demás seres. No obstante, corresponde a la intuición y sabiduría de cada «gnóstico» individual destilar a partir de estos principios las pautas singulares para su aplicación personal.

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— El Destino —]]
#v(0.5em)

Cuando a Confucio le preguntaron acerca de la muerte, respondió: «¿Por qué me preguntas sobre la muerte cuando aún no sabes cómo vivir?». Esta respuesta bien podría haberla dado un gnóstico. A una pregunta semejante formulada en el Evangelio gnóstico de Tomás, Jesús respondió que los seres humanos deben alcanzar por la Gnosis el conocimiento de la realidad divina e inefable de la cual provienen y a la cual habrán de retornar. Este conocimiento trascendental debe advenirles mientras aún se hallan encarnados en la tierra.

La muerte no trae aparejada automáticamente la liberación del cautiverio en los dominios del Demiurgo. Quienes no hayan alcanzado una Gnosis liberadora mientras estaban encarnados pueden quedar atrapados una vez más en la existencia. Es muy probable que esto ocurra a través del ciclo de renacimientos. El gnosticismo no enfatiza de manera prominente la doctrina de la reencarnación, pero en la mayoría de las enseñanzas gnósticas se sobreentiende implícitamente que aquellos que no hayan establecido un contacto efectivo con sus orígenes trascendentales durante su vida encarnada tendrán que retornar a la penosa condición de la existencia terrenal.

En lo que respecta a la salvación, o al destino del espíritu y del alma tras la muerte, conviene saber que existe auxilio disponible. Valentín, el más grande de los maestros gnósticos, enseñó que Cristo y Sofía aguardan al hombre espiritual —el gnóstico pneumático— a la entrada del Pléroma y lo ayudan a ingresar en la cámara nupcial de la reunión definitiva. Ptolomeo, discípulo de Valentín, enseñó que incluso aquellos que no poseen condición pneumática, los psíquicos, podían ser redimidos y habitar en un mundo celestial en el umbral del Pléroma. En la plenitud de los tiempos, todo ser espiritual recibirá la Gnosis y se unirá con su Yo superior —el Gemelo angélico—, haciéndose así digno de ingresar en el Pléroma. Nada de esto es posible, sin embargo, sin un esfuerzo ferviente por alcanzar la Gnosis.

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— Gnosis y Psique: La Conexión con la Psicología Profunda —]]
#v(0.5em)

A lo largo del siglo XX, la nueva disciplina científica de la psicología profunda adquirió notable preeminencia. Entre los psicólogos profundos que mostraron un interés pronunciado y documentado por el gnosticismo, un lugar de honor corresponde a C. G. Jung. Jung desempeñó un papel decisivo al llamar la atención sobre la biblioteca de escritos gnósticos de Nag Hammadi en la década de 1950, pues advirtió la extraordinaria relevancia psicológica de las intuiciones gnósticas.

El destacado estudioso del gnosticismo G. Filoramo escribió: «Las reflexiones de Jung habían estado largamente inmersas en el pensamiento de los antiguos gnósticos hasta tal punto que los consideraba los descubridores virtuales de la "psicología profunda"... La antigua Gnosis, aun bajo su forma de religión universal, prefiguraba en cierto sentido —y al mismo tiempo ayudaba a esclarecer— la naturaleza de la terapia espiritual junguiana». A la luz de tales reconocimientos cabe preguntarse: «¿Es el gnosticismo una religión o una psicología?». La respuesta es que muy bien puede ser ambas cosas. La mayoría de los mitologemas presentes en las escrituras gnósticas poseen pertinencia y aplicabilidad psicológicas. Por ejemplo, el ciego y arrogante creador-Demiurgo guarda un estrecho parecido con el ego humano alienado que ha perdido el contacto con el Sí-mismo [Self] ontológico. Asimismo, el mito de Sofía se asemeja íntimamente a la historia de la psique humana que pierde su vínculo con el inconsciente colectivo y necesita ser rescatada por el Sí-mismo. Analogías de esta índole existen en gran profusión.

Muchas enseñanzas esotéricas han proclamado: «Como es arriba, así es abajo». Nuestra naturaleza psicológica (el microcosmos) refleja la naturaleza metafísica (el macrocosmos), razón por la cual el gnosticismo puede poseer una autenticidad tanto psicológica como religiosa. La psicología gnóstica y la religión gnóstica no tienen por qué excluirse mutuamente, sino que pueden complementarse dentro de un orden implícito de totalidad. Los gnósticos siempre han sostenido que la divinidad es inmanente al espíritu humano, aunque no se agota en él. La convergencia de la enseñanza religiosa gnóstica con la penetración psicológica resulta, por tanto, plenamente comprensible en términos de los principios gnósticos consagrados por la tradición.

#v(1.2em)
#align(center)[#text(fill: rgb("#7a2821"), size: 12pt, weight: "bold", tracking: 0.08em)[— Conclusión —]]
#v(0.5em)

Algunos autores trazan una distinción entre «Gnosis» y «gnosticismo». Tales distinciones son a la vez útiles y engañosas. La Gnosis es, sin lugar a dudas, una experiencia fundada no en conceptos ni preceptos, sino en la sensibilidad del corazón. El gnosticismo, por su parte, es la cosmovisión edificada sobre la experiencia de la Gnosis. Por esta razón, en otras lenguas distintas del inglés, la palabra Gnosis suele emplearse para designar tanto la experiencia como la cosmovisión (_die Gnosis_ en alemán, _la Gnose_ en francés).

En cierto sentido, no hay Gnosis sin gnosticismo, pues la experiencia de la Gnosis suscita inevitablemente una cosmovisión en la cual encuentra su morada. La cosmovisión gnóstica es experiencial: se asienta en un tipo particular de experiencia espiritual de la Gnosis. Por consiguiente, no basta con omitir o diluir diversas partes de la cosmovisión gnóstica, ya que, de hacerse así, dicha cosmovisión dejaría de corresponderse con la experiencia.

Se ha dicho que la teología es una envoltura intelectual alrededor del núcleo espiritual de una religión. Si esto es cierto, también lo es que la mayoría de las religiones están siendo estranguladas y asfixiadas por sus propias envolturas. El gnosticismo no corre ese peligro, porque su cosmovisión se enuncia en el mito antes que en la teología. Los mitos, incluidos los gnósticos, admiten múltiples interpretaciones: la trascendencia, lo numinoso y los arquetipos psicológicos, junto con otros elementos, desempeñan un papel en dicha interpretación. Y sin embargo, estas formulaciones míticas hablan de verdades hondas que no se dejan desmentir.

El gnosticismo puede traernos tales verdades con suprema autoridad, porque habla con la voz de la parte más elevada del ser humano: el espíritu. De este espíritu se ha dicho que «sopla donde quiere». Esta es, pues, la razón por la cual la cosmovisión gnóstica no pudo ser extirpada a pesar de tantos siglos de persecución.

La cosmovisión gnóstica siempre ha sido actual, porque siempre respondió mejor que ninguna otra al «conocimiento del corazón» que es la verdadera Gnosis. Hoy, sin embargo, su vigencia es cada vez mayor, toda vez que el final del segundo milenio ha sido testigo del deterioro radical de numerosas ideologías que rehuyeron las grandes preguntas y respuestas abordadas por el gnosticismo. La claridad, franqueza y autenticidad de la respuesta gnóstica ante las interrogantes de la condición humana no pueden dejar de impresionar y, con el tiempo, de convencer. Si sus reacciones ante este resumen han sido de un orden igualmente afirmativo, ¡tal vez usted mismo sea un gnóstico!

#pad(left: 1.5em, right: 1em)[#text(style: "italic", fill: rgb("#3d3833"))[_Stephan A. Hoeller (Tau Stephanus, Obispo Gnóstico)_]]

#v(2em)
#align(center)[
  #line(length: 30%, stroke: 0.5pt + rgb("#7a2821"))
  #v(0.5em)
  #text(size: 8pt, style: "italic", fill: rgb("#635c54"))[
    Rescatado, traducido y curado en Deepest Internet
  ]
]
