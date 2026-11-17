# Mejoras futuras del modelo

Ideas que mejorarían el modelo, pero que hoy no se hacen por falta de tiempo o de datos oficiales. Cada una dice qué falta, por qué importa y cómo se incorporaría.

## 1. Costo oficial de la permanencia escolar (PTAFI)

*Agregada el 1 de noviembre de 2026.*

**Qué falta:** el costo por estudiante de una intervención para que un niño **ya matriculado** no deserte ni pierda el año. Puede ser refuerzo, tutorías o apoyo para la promoción anticipada del Decreto 1290 de 2009, art. 7.

**Por qué no está hoy:** no hay un costo oficial por estudiante. Revisión del 1 de noviembre de 2026:

| Programa | Fuente | Por qué no sirve como costo por niño |
|---|---|---|
| PTAFI (MEN, sucesor de Todos a Aprender) | [MEN](https://www.mineducacion.gov.co/1780/w3-article-423569.html): 6,277 tutores en 2025 para unos 5,000 colegios | Acompaña a docentes, no a estudiantes, y no publica costo por estudiante |
| Formación Integral | [MEN](https://www.mineducacion.gov.co/1780/w3-article-427986.html): $567,395 M en el cuatrienio, 1,169,341 estudiantes | Dividir da unos $485 mil, pero esa cuenta es nuestra, no del MEN, y es por cuatrienio |
| CONPES 4188 | [DNP](https://www.dnp.gov.co/Prensa_/Noticias/Paginas/colombia-asegura-204-billones-formacion-integral-estudiantes.aspx): $2.046 billones para 2026–2036 | Incluye la formación de docentes y no da valor por estudiante |
| Estrategias de permanencia MEN 2023 | [MEN](https://www.mineducacion.gov.co/1780/w3-article-415819.html) | Lista de líneas de acción, sin montos |
| Promoción anticipada | Decreto 1290 de 2009, art. 7 | Es un trámite del consejo académico, sin programa ni costo propio |

**Cómo queda el modelo mientras tanto:** a los niños matriculados no se les asigna intervención de permanencia. El cupo ya lo paga el SGP, así que cobrarlo otra vez sería contarlo dos veces. Su riesgo de desertar o perder el año queda en el escenario sin intervenir ($q_k$, sección 4.6 del informe del rezago). Esto se declara como limitación en el informe.

**Cómo se conseguiría el dato:** un derecho de petición al MEN (Ley 1755 de 2015) que pida el costo anual por estudiante de PTAFI o del programa de permanencia que aplique, desagregado para Antioquia si es posible. Las solicitudes de información deben responderse en 10 días hábiles (art. 14).

**Cómo entraría al modelo:** como una intervención nueva $w_k$ para el niño matriculado con riesgo:
- **Costo:** $c^{\text{perm}}_k$.
- **Efecto:** sube la probabilidad de avanzar de $q_k$ a $q_k'$. El beneficio en severidad sería $(q_k' - q_k)$ por el término de la sección 4.6.
- **Datos que se necesitan:** el costo y también la efectividad ($q_k'$), las dos con fuente oficial o con una evaluación publicada.

## 2. Tiempo por fuera del colegio, para habilitar el CLEI de secundaria (E3)

*Agregada el 2 de noviembre de 2026. Decisión de Martín: el caso base va sin E3.*

**Qué falta:** saber cuántos años lleva por fuera del colegio cada joven que no asiste. Para entrar a los ciclos de secundaria del CLEI, el Decreto 1075 de 2015, art. 2.3.3.5.3.4.2, exige tres cosas: tener 15 años o más, haber terminado la primaria y llevar **2 años o más por fuera** de la educación formal.

**Por qué no está hoy:** la ECV 2025 no tiene esa variable. El módulo de Educación (82 variables) pregunta si la persona asiste (P8586), cuál fue el último grado aprobado (P8587S1) y por qué no estudia (P6218), pero no cuándo dejó de estudiar. El atraso no sirve para reemplazarla. Un joven de 15 años con 4 de atraso pudo haberse salido hace 4 años, o haber repetido 3 veces y salirse el año pasado. Lo único que el atraso garantiza es una condición necesaria: con menos de 2 años de atraso, es imposible llevar 2 años por fuera.

**Cómo queda el modelo mientras tanto (caso base):** a los jóvenes de 15 y 16 años que no asisten se les ofrece solo el regreso al colegio (E1), que es legal para todos. Esa estrategia cuesta $3.0 M / p de Renta Ciudadana por hogar más el cupo del SGP por cada niño. En el modelo: $e_{i,E3} = 0$ para todo $i$. Se escogió así porque la regla del proyecto es no meter al modelo nada que no esté sustentado con datos o fuentes oficiales. Usar E3 sería lo deseable, porque es mucho más barato ($958,431 por ciclo en lo urbano, frente a unos $11 M por regreso exitoso), pero hoy dependería de un supuesto que no se puede comprobar.

**Lo que cuesta no tener el dato** (p = 0.37, normalizado, 215 niños):

| | Caso base, sin E3 | Con E3 (supuesto atraso ≥ 2, 33 elegibles) |
|---|---|---|
| Cubrir a los 29 menores de 16 que no asisten | 11.8 %, $104.2 mm | 12.4 %, $65.7 mm |
| Reducción máxima de SevEdu | 16.9 %, $201.6 mm | 21.2 %, $83.3 mm |

Con E3, la severidad bajaría más y costaría menos. La diferencia es el valor de conseguir el dato.

**Cómo se conseguiría el dato:**
1. Pedir al MEN o a la Secretaría de Educación de Antioquia, mediante derecho de petición (Ley 1755 de 2015), el año de retiro de los desertores según el SIMAT. Las solicitudes de información se responden en 10 días hábiles.
2. Buscar en otras encuestas del DANE (por ejemplo, la GEIH) una pregunta sobre el último año en que la persona estudió.
3. Cruzar el último grado aprobado con la edad a la que normalmente se aprueba ese grado. Así se obtiene una cota, no el dato exacto, y habría que declararlo como supuesto.

**Cómo entraría al modelo:** como el parámetro de elegibilidad $e_{i,E3} = 1[\text{edad}_i \ge 15] \cdot 1[\text{asiste}_i = 0] \cdot 1[g_i \in \{5,\dots,8\}] \cdot 1[\text{años por fuera}_i \ge 2]$, junto con la restricción $z_{i,E3} \le e_{i,E3}$. Las demás restricciones no cambian. Mientras no haya dato, la versión "con E3", que usa el atraso $a_i \ge 2$ como aproximación, se presenta solo como **sensibilidad**, con el supuesto escrito explícitamente.

## 3. Probabilidad de regreso (p) dentro de la decisión de E1

*Agregada el 4 de noviembre de 2026. Decisión de Martín: se deja como está por falta de tiempo y se declara como limitación.*

**Qué pasa hoy:** cuando el modelo pone $z_{k,E1} = 1$, cuenta el beneficio **completo** del niño en SevEdu (como si volviera con certeza) y paga $3.0\text{ M}/p$ por hogar más el cupo del SGP. Pero con $p = 0.37$ solo volvería, en promedio, el 37 % de los niños que reciben el pago.

**Por qué importa:** el beneficio de E1 queda inflado. Por eso la reducción máxima de SevEdu (16.9 %) y la cobertura de 6 a 15 años (11.8 %) del caso base son cotas optimistas, no valores esperados.

**Cómo se corregiría:** interpretar $z_{k,E1}$ como "el Estado **ofrece** el pago" y no como "el niño vuelve":
- **Beneficio en SevEdu:** $p \cdot$ coeficiente del niño (valor esperado).
- **Costo:** $HW_k \cdot (3.0\text{ M} + p \cdot \text{cupo SGP})$, porque el pago se hace siempre y el cupo solo se paga a quien vuelve.
- **Pregunta abierta:** si $z$ es una decisión (ofrecer) o un resultado (volver). La versión corregida usa la primera.

**Cómo queda el modelo mientras tanto:** sin cambios. En el informe se declara que las cifras de E1 suponen que el niño beneficiado vuelve, y que con valor esperado bajarían.

## 4. Cobertura del art. 67 para todos los niños que no asisten

*Agregada el 4 de noviembre de 2026. Decisión de Martín: se deja como mejora futura y se declara como limitación.*

**Qué pasa hoy:** la cobertura obligatoria (restricción E-7, $\sum_s z_{ks} = 1$) solo incluye a los niños de 6 a 15 años que no asisten **y** están entre los 215 rezagados. Un niño de esa edad que no asiste y no tiene rezago queda por fuera. Tampoco lo empuja el techo de SevEdu, porque su atraso es 0, así que subir $\rho_e$ no lo cubre.

**Por qué importa:** el art. 67 de la Constitución obliga a la educación de los 5 a los 15 años para todos, no solo para los rezagados.

**Cómo se corregiría:**
- **Ampliar E-7** a todos los niños de 6 a 15 años que no asisten según la ECV, tengan o no rezago. A los que no tienen rezago solo les sirve E1 (Renta Ciudadana $3.0 M / p por hogar + cupo SGP). Eso mejora el H por inasistencia, pero no SevEdu.
- **Dato que se necesita:** el conteo de esos niños por hogar, que sale de `05_conteo_personas.py`. El costo total superaría los $105.8 mm del caso base.
- **Los 14 jóvenes de 16 años** quedan sin obligación, porque el art. 67 obliga solo hasta los 15. El modelo puede atenderlos con E1 si le conviene para H.

**Cómo queda el modelo mientras tanto:** E-7 cubre a los 29 no asistentes de 6 a 15 años de la cohorte de rezagados, más ρ_e = 14 %. En el informe se declara que los no asistentes sin rezago y los de 16 años no tienen cobertura obligatoria.

## 5. Sensibilidad de trabajo infantil con apoyo psicosocial del ICBF

*Agregada el 4 de noviembre de 2026. Decisión de Martín: el caso base es el externado de media jornada y el apoyo psicosocial queda como sensibilidad.*

**Qué pasa hoy:** eliminar la privación de `trabajo_infantil` cuesta **$5,316,348 por niño que trabaja**: el externado de media jornada del ICBF (código SIM 420212) por 6 meses, a $886,058 por cupo al mes. El externado atiende al niño 4 horas al día en contrajornada escolar, de lunes a viernes.

**La sensibilidad:** cambiar el externado por la otra modalidad del lineamiento del ICBF, el **apoyo psicosocial** (código SIM 420213), con 10 sesiones al mes:

| Modalidad | Costo cupo mes (feb–dic 2025) | Meses por niño | Costo por niño |
|---|---|---|---|
| Externado media jornada (caso base) | $886,058 | 6 | $5,316,348 |
| Apoyo psicosocial (sensibilidad baja) | $554,907 | 6 | $3,329,442 |

**Fuentes:**
- [Lineamiento técnico del ICBF para la atención de NNA en situación de trabajo infantil](https://www.icbf.gov.co/sites/default/files/procesos/lm4.p_lineamiento_tecnico_para_la_atencion_de_ninos_ninas_y_adolescentes_en_situacion_de_trabajo_infantil_v1.pdf), LM4.P v1, aprobado por la Res. 1513 de 2016.
- [Res. ICBF 0001 de 2025](https://www.icbf.gov.co/sites/default/files/res._no._0001_2025_line_de_prog_y_ejec_msyf_.pdf), ficha I-12-122: 6 meses de operación y 2 niños por cupo al año.
- [Res. ICBF 0296 de 2025](https://www.icbf.gov.co/sites/default/files/resolucion_no._0296-310125_lineamientos_de_programacion_2025.pdf), que actualizó el costo cupo mes desde febrero. Las Res. 988, 3182, 4254, 5287, 6458 y 7284 no modifican esta ficha.

**Qué muestra:** cuánto cambian H, M0 y la severidad si se usa la intervención más barata, que no ocupa el tiempo del niño. El costo por niño baja 37 % ($1,986,906 menos), así que el modelo podría preferir intervenir trabajo infantil antes que otros indicadores.

**Supuesto que hay que declarar:** en ambos casos se asume que 6 meses de atención del ICBF bastan para que el niño deje de trabajar. Con apoyo psicosocial el supuesto es más débil, porque el niño sigue teniendo las horas libres en las que trabajaba. Por eso es una cota baja del costo y no el caso base.

**Cómo entraría al modelo:** se reemplaza $EpF_{trabajo\_infantil}$ = $5,316,348 por $3,329,442 en `parametros.py`, con $u_{ij}$ = niños en trabajo infantil del hogar. Las restricciones no cambian.

## 6. Severidad de logro educativo ponderada por la edad de los adultos

*Agregada el 4 de noviembre de 2026. Decisión de Martín: no entra al caso base porque falta investigación.*

**Qué pasa hoy:** el CLEI dura al menos 40 semanas por ciclo (Decreto 1075 de 2015, art. 2.3.3.5.3.4.4), así que en un año un adulto hace como máximo un ciclo. Con esa regla, solo 33 de los 503 hogares pobres con privación de logro pueden quitarla en un año (`costos/logro_educativo_analisis.md`). En los otros 470, hacer un ciclo no cambia ni H ni la severidad del Modelo 1, porque el indicador es binario. El modelo no tiene incentivo para educar a esos adultos y, en este indicador, los "abandona".

**Idea de solución:** una segunda capa, como la SevEdu del rezago. Sería una severidad de logro por adulto, $\sum_a HW_a \left(\frac{9 - e_a'}{9}\right)^2$ sobre los adultos con menos de 9 años, con un techo $\rho_l$. Como cada adulto hace como máximo un ciclo ($w_a$ binaria), sería lineal y exacta.

**Por qué falta investigación (planteamiento de Martín):** no es lo mismo un hogar donde solo viven personas mayores de 60 años que uno de jóvenes menores de 30. En el hogar joven hay más probabilidad de que el adulto **sí complete** el ciclo, y el beneficio dura más años. La severidad debería pesar distinto según la composición por edades del hogar. Martín propone medir esa composición con una entropía sobre las personas del hogar.

**Qué habría que conseguir o decidir:**
- **Tasa de finalización del CLEI por grupo de edad**, con fuente oficial: MEN, SIMAT o evaluaciones de educación de adultos. Con ella se pondera cada adulto por su probabilidad de completar el ciclo, $\pi_{edad}$. Así el beneficio esperado sería $\pi_{edad} \cdot$ coeficiente, la misma lógica que la $p$ de E1 (mejora 3).
- **Cómo medir la composición del hogar.** Hay dos caminos:
  - una entropía de Shannon sobre los grupos de edad de los adultos;
  - ponderar directamente con $\pi_{edad}$.
  Ojo: la entropía mide qué tan **diversa** es la mezcla de edades, no qué tan joven es el hogar. Un hogar con solo jóvenes y uno con solo mayores tienen la misma entropía (0). Si lo que importa es la probabilidad de terminar, la ponderación por $\pi_{edad}$ lo captura de forma directa.
- **Duración y costo de los ciclos 5 y 6** (media académica de adultos), que hoy no están verificados.

**Cómo queda el modelo mientras tanto:** sin capa de severidad de logro. Se declara como limitación que el modelo no premia el avance parcial en logro educativo.

## 7. Revisar por qué se usaban 4 consultas en barreras de acceso a salud

*Agregada el 4 de noviembre de 2026. Decisión de Martín: se descartan las 4 consultas; el caso base es 1 consulta.*

**Qué pasa hoy:** el costo de `barreras_acceso_salud` pasa de 4 consultas ($0.21 M por persona) a **1 consulta de medicina general = $52,100** por persona. La cifra es la del código 39141, "Consulta ambulatoria de medicina general", con 4.51 UVB, según la [Circular Externa 25 de 2024 de Minsalud](https://www.minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/DE/DIJ/circular-externa-0025-de-2024.pdf), p. 34, tarifas SOAT de 2025. En lo rural se mantiene la prima por dispersión de la UPC: 11.47 % × $1,323,403 = $151,794 (Res. 2717 de 2024). Esa prima es una aproximación al costo de llevar al paciente, no un subsidio de transporte.

**Por qué 1 consulta:** el DANE marca la privación cuando la persona tuvo un problema de salud (`P5665` = 1) y no la atendió un profesional (`P8563` ∉ {1, 2}). Una consulta con un profesional basta para quitarla.

**Pendiente:** revisar en el hilo **"Análisis de paper sobre optimización"** por qué se decidió usar 4 consultas. Allí se tomó esa decisión. Si hubo una razón con fuente oficial, por ejemplo una ruta de atención o una norma de Minsalud, se puede volver a usar como sensibilidad. Si no la hubo, queda descartada.

## 8. Renta Ciudadana exige matrícula, no asistencia (inasistencia escolar)

**Qué dice la norma:** la [Resolución 652 de 2025 de Prosperidad Social](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=179667&dt=S) (21 abr 2025, Diario Oficial 53.097 del 23 abr 2025) adiciona el Capítulo 6 a la Resolución 079 de 2024. Su art. 1.6.1, num. 2.1, dice: "Todos los niños, niñas y adolescentes entre cinco (5) y diecisiete (17) años deberán estar matriculados en el sistema educativo colombiano. Esta corresponsabilidad se verificará cada dos ciclos operativos." Aplica a las líneas Valoración del Cuidado y Colombia sin Hambre. Si no se cumple, el hogar no recibe las transferencias hasta que se verifique (Parágrafo 2). No se exige en hogares con una persona con discapacidad que ya atiende Valoración del Cuidado (Parágrafo 1).

**Qué pasa hoy:** el costo de `inasistencia_escolar` ($3.0 M/p + cupo SGP) se sostiene, porque la condición educativa existe en la norma vigente. Pero la condición es la **matrícula**, y el indicador del DANE mide la **asistencia**. Un niño matriculado que no asiste seguiría recibiendo la transferencia y seguiría privado.

**Limitación:** el modelo supone que matricularse implica asistir. Para cerrarla haría falta un costo oficial de permanencia (ver mejora #1, PTAFI), que hoy no existe.

## 9. Hogares que ya reciben Renta Ciudadana (E1)

*Agregada el 4 de noviembre de 2026. Decisión de Martín: se declara como limitación (objeción 2 del hilo "Debatir").*

**Qué pasa hoy:** el costo de E1 (regreso al colegio) es $3.0 M / p por hogar de Renta Ciudadana más el cupo del SGP. El modelo lo cobra a todos los hogares con niños que no asisten, como si ninguno recibiera ya la transferencia.

**Por qué importa:** muchos hogares pobres ya son beneficiarios de Renta Ciudadana. En ellos pasan dos cosas: (1) los $3.0 M ya los paga el Estado y no son un gasto nuevo dentro de $B$, así que el costo de E1 está **sobrestimado**; (2) si el hogar ya recibe la transferencia y el niño igual no asiste, la intervención **no es nueva**: ya se aplicó y no funcionó, y no se puede pagar dos veces.

**Por qué no se corrige hoy:** la ECV 2025 no pregunta si el hogar es beneficiario de Renta Ciudadana.

**Cómo se corregiría:** cruzar los hogares con la base de beneficiarios de Prosperidad Social (solicitud de información, Ley 1755 de 2015), o usar otra encuesta que pregunte por transferencias. Con ese dato, a los beneficiarios se les cobraría solo el cupo SGP, o se les excluiría de E1 y se les ofrecería otra estrategia.

**Cómo queda el modelo mientras tanto:** sin cambios. En el informe (§7) se declara la limitación.

## 10. Salidas "solas" del rezago por cumplir 18 años: ¿son buenas o malas?

*Agregada el 5 de noviembre de 2026. Contexto: decisión D4, en la que H es la foto inicial y nadie envejece dentro de H.*

**El fenómeno:** el indicador de rezago del DANE solo mira a las personas de 7 a 17 años. Un joven de 17 años rezagado que cumple 18 deja de contar, aunque siga exactamente igual de atrasado. Si su hogar estaba apenas por encima del umbral por esa privación, el hogar "sale" de la pobreza sin que nadie haya hecho nada. Entre los 215 niños rezagados hay 27 de 17 años. Con la inasistencia pasa lo mismo: hay 14 no asistentes de 16 años, y el indicador solo llega hasta los 16.

**¿Es bueno o malo?**

- **Para la persona, no es una mejora real.** El joven no aprendió nada ni se niveló. Su déficit educativo sigue ahí: solo se movió de indicador. Como tiene 15 años o más, sus años de estudio ya cuentan en el **logro educativo** del hogar, que es un promedio. Además, al salir del rezago su atraso deja de "verse" en el IPM justo cuando es más difícil corregirlo.
- **Para medir la política, es malo contarlo como logro.** Si el modelo lo contara, premiaría esperar en vez de invertir. Sería un logro que nadie pagó y que inflaría H con salidas que no dependen del presupuesto. Por eso se excluye (D4, lectura a) y la cohorte fija lo neutraliza en SevEdu.
- **Para predecir la cifra oficial del año siguiente, sí es real.** El DANE sí reportará a ese hogar como no pobre. El H oficial bajará un poco por pura demografía, sin relación con la política.
- **No es simétrico.** En el mismo año también hay **entradas solas**: el niño que cumple 6 años sin matrícula entra en inasistencia, y el que cumple 7 con atraso entra en rezago. Contar solo las salidas sesgaría el resultado hacia el optimismo.

**Conclusión:** es malo como medida de impacto y neutro o cosmético como estadística. El modelo hace bien en no atribuírselo. En la sustentación conviene decir que el IPM tiene este **efecto frontera por edad**: una parte de la caída del H oficial de un año a otro puede venir de jóvenes que salen del rango, no de políticas.

**Cómo se mejoraría:** con la opción (c), que mide H al final del año contra el H sin intervenir. Se proyectarían las salidas **y** las entradas por edad de los indicadores que dependen de ella (rezago, inasistencia, trabajo infantil, atención integral). Al modelo se le atribuiría solo la diferencia. Así se podría reportar por separado:
- el efecto demográfico (lo que cambia solo);
- el efecto de la política (lo que compra el presupuesto).

Requiere los datos de edad que ya están en la ECV. No requiere supuestos sobre empleo, salud o vivienda, porque esos indicadores no se envejecen.

## 11. El codo de r es débil con presupuestos altos

*Agregada el 9 de noviembre de 2026. Contexto: decisión de Martín de que r (el piso de equidad por zona) sea el codo de la curva H contra r de cada corrida (P24).*

**El problema:** el rango de r sale de los datos: empieza en el piso que la solución libre ya da (el menor porcentaje de pobres que sale en una zona con r = 0) y termina en el mayor r factible. Con presupuestos bajos la curva tiene una forma clara y el codo se ve. Con presupuestos altos la curva baja casi en línea recta y el codo está poco marcado:

| B (mil millones) | Piso libre | r factible máximo | Codo | Personas que cuesta |
|---|---|---|---|---|
| $127.1 | 16.3 % | 26.1 % | 0.234 | 6,222 (2.9 % de H) |
| $187 | 40.4 % | 49.7 % | 0.438 | 618 (0.2 %) |
| $424 | 80.7 % | 85.5 % | 0.833 | 1,497 (0.3 %) |

**Por qué importa:**
- Con $424 mil millones el r del codo (0.833) es casi lo que ya sale solo (89 %, 87 % y 81 %). La equidad no restringe de verdad: el valor es técnicamente correcto pero casi decorativo.
- El codo depende del tramo que se mire: con una malla que arrancaba en 0.15 daba 0.21 con $127.1 mil millones; con el rango del piso libre da 0.234 (unas 5,600 personas de diferencia).
- El valor de r cambia con B (0.23, 0.44, 0.83), por lo que no hay un único r para reportar.

**Cómo se mejoraría:**
- Probar otro criterio de codo para curvas casi lineales (por ejemplo la mayor curvatura o la regla de la pendiente, en la que se marca el punto donde cada punto de r adicional cuesta más de cierto número de personas, con ese número sustentado).
- Reportar junto al codo el piso logrado por zona y declarar cuándo r no actúa.
- Revisar si con presupuestos altos conviene fijar un piso por criterio de política (por ejemplo, un piso mínimo por zona) y no por codo.

**Cómo queda el modelo mientras tanto:** r = codo de cada corrida. Con presupuestos bajos (donde r actúa) el valor es claro; con presupuestos altos se reporta el piso logrado por zona y se declara la limitación.

## 12. La regla de la brecha como restricción directa (R1 de la segunda auditoría)

*Agregada el 10 de noviembre de 2026. Origen: segunda auditoría del Modelo 1 (`auditoria/auditoria_modelo1_v2.md`, hallazgo R1). Estado: **pendiente de decisión de Martín**; no está implementado.*

**La regla.** "Los hogares que siguen pobres no quedan, en promedio, más pobres que hoy": A ≤ A0, donde A es la brecha (intensidad) promedio de los que siguen pobres.

**Cómo se aplica hoy.** El código no impone A ≤ A0 directamente. Busca por bisección el menor techo de severidad ρ con el que, de paso, A queda ≤ A0. Pero ρ limita la suma de severidades de **todos** los hogares (los que salen y los que no), mientras que la regla solo habla de los que siguen pobres.

**Ejemplo sencillo.** Es como exigir que los alumnos que reprueban no tengan peor promedio que el año pasado, y para lograrlo pedir una nota mínima a todo el salón, incluidos los que ya aprobaron. Funciona, pero se gasta esfuerzo en quienes la regla no pedía cuidar. Aquí ese esfuerzo se paga en personas que no salen de la pobreza.

**Qué cambia si se escribe la regla directamente** (mismo B, r y ρ_e; prueba del auditor, `exp_brecha_directa.py`):

| B (mil millones) | Hoy (ρ por bisección) | Regla directa A ≤ A0 | Diferencia |
|---|---|---|---|
| $424 | 581,452 personas, A = 0.40910, severidad −47.4 % | 586,268, A = 0.40935, severidad −46.3 % | +4,816 (+0.8 %) |
| $187 | 332,582 personas, A = 0.40925, severidad −27.2 % | 333,127, A = 0.40935, severidad −27.1 % | +545 (+0.16 %) |

**Cómo se escribe (exacto y lineal, no una aproximación).**
1. A ≤ A0 ⇔ Σ p_i (s_i − A0)(1 − y_i) ≤ 0. A es un cociente de sumas sobre los que siguen pobres (y_i = 0) y el denominador es positivo, así que se puede multiplicar sin cambiar el sentido.
2. El producto s_i·y_i se linealiza exacto con una variable w_i (McCormick, con y_i binaria y 0 ≤ s_i ≤ c_i⁰): w_i ≤ c_i⁰ y_i, w_i ≤ s_i, w_i ≥ s_i − c_i⁰(1 − y_i).
3. Hay que agregar s_i ≥ 0.34 (1 − y_i): "si y_i = 0, el hogar sigue pobre". Sin esto el modelo podría dejar y_i = 0 en un hogar que ya bajó de 0.34 para bajar A de forma artificial. Con puntajes en múltiplos de 0.01 no corta ninguna solución real.

**Costo computacional.** 523 variables continuas y 2,093 filas más. La etapa 1 tarda 9.6 s (B = 424) y 17 s (B = 187) y reemplaza las ~10 corridas de la bisección. La etapa 2 (min severidad con H ≥ H*) tarda 533 s y 134 s: hay que subir su límite de tiempo a 600 s.

**Problema adicional de la bisección (R2).** A no es monótona en ρ: con B = 424, A pasa de 0.4131 a 0.4145 al subir ρ de 0.4625 a 0.4675, porque la etapa 2 minimiza la severidad de todos, no A. Además, ρ = 0.4738 ya cumple la regla y la bisección devolvió 0.4741 (tolerancia 0.001): unas 206 personas. En las mallas probadas A cruzó A0 una sola vez, así que el resultado de hoy es correcto, pero la bisección supone algo que no está garantizado. Con la regla directa no hay nada que suponer.

**Las dos opciones.**

- **Opción 1 (recomendada por el auditor).** Caso base = max H sujeto a A ≤ A0 escrita directamente; la severidad queda como desempate en la etapa 2 (que ya existe). Cumple la regla tal como se enunció, con más personas, y el resultado pasa de ser una cota inferior a ser el óptimo de la regla.
  - *Ventajas:* +4,816 personas con B = 424; desaparece la bisección y R2; sin supuesto de monotonía.
  - *Costos:* el modelo ya no tiene techo de severidad propio (solo se protege a los que siguen pobres); la severidad total baja menos (46.3 % frente a 47.4 %); la etapa 2 pasa de ~16 s a ~9 min; hay que cambiar `modelo1.py` (una capa nueva en `agregar_restricciones_propias`), la formulación y extender `verificar_m1.py`.
- **Opción 2.** Dejar ρ por bisección y reportar la regla directa como cota ("con la regla exacta saldrían 4,816 más").
  - *Ventajas:* casi sin trabajo; se conserva el techo de severidad y el resultado de referencia (581,452).
  - *Costos:* el caso base queda por debajo de lo que la regla permite; conviene afinar la búsqueda (`tol` de 0.001 a 0.0002) y revisar 2 o 3 valores de ρ por debajo del resultado.

**Cómo se implementaría (opción 1), por fases, cada una con luz verde de Martín.**
1. Agregar s_i ≥ 0.34 (1 − y_i) y probarla contra enumeración exacta.
2. Agregar w_i y la restricción de la brecha; verificar A ≤ A0 recalculando desde los datos.
3. Quitar la bisección de ρ del caso base (queda como sensibilidad) y subir el límite de la etapa 2.
4. Extender `verificar_m1.py` y repetir B = $187 y $424 mil millones.
5. Registrar la decisión en `justificacion_decisiones.md` (P25) y actualizar la formulación y el grafo.

**Decisión pendiente de Martín:** opción 1 o 2.

## 13. Revisar por qué, en los análisis de sensibilidad del Modelo 2, las cajas no se mueven

*(Pedido por Martín el 10-nov-2026 al leer `informe_cajas_modelo2.md`. Es una revisión pendiente, no un error confirmado.)*

**El fragmento que motivó la revisión** (conclusión 1 de la sección 5 del informe de cajas):

> **1. Cuatro sensibilidades no mueven las cajas.** El cumplimiento de Renta Ciudadana (p = 0.50 y 0.75), SevEdu activa al 14 % y el desempleo imputado quitable dan las mismas cajas que el caso base: salen los mismos hogares (19, 29 y 65), con los mismos puntajes. Lo único que cambia es el costo (por ejemplo, con 20 %: 118.86 mm en el caso base, 102.19 con p = 0.50, 86.53 con p = 0.75, 120.38 con SevEdu 14 %). Conclusión: esas sensibilidades cambian el presupuesto, no la posición de los pobres. *(En p = 0.50 con 20 %, el puntaje mínimo es 0.18 y no 0.24: es otra solución de igual costo con los mismos resultados, y no cambia ninguna estadística de la caja.)*

**Qué hay que revisar.** Por qué cuatro de las seis sensibilidades del Modelo 2 dan exactamente los mismos hogares que salen (19, 29 y 65 con metas de 5, 10 y 20 %) y las mismas cajas, y si eso significa que la sensibilidad es poco informativa o que hay algo mal en cómo se aplica.

**Hipótesis (sin verificar, hay que comprobarlas en el código y con corridas).**
1. **El cambio no toca lo que la meta compra.** El parámetro p solo afecta el costo de Renta Ciudadana (E1), que entra por la cobertura obligatoria del art. 67 (E-7). Lo que compra la meta de M0 con 5, 10 y 20 % son barreras de salud, ciclos CLEI de adultos y aseguramiento, cuyos costos no dependen de p. Si es así, la sensibilidad a p mueve el piso de E-7 pero no el costo de la meta (que queda en 1.17 / 4.25 / 14.45 mm) ni quién sale.
2. **Las metas pequeñas están dominadas por el piso de E-7.** El piso es el 99 %, 96 % y 88 % del costo con metas de 5, 10 y 20 %. Con tan poco margen, el modelo elige siempre a los hogares más baratos de sacar, y ese orden no cambia con estas sensibilidades.
3. **SevEdu al 14 % y desempleo imputado.** SevEdu ya baja 11.8 % solo por E-7, así que el techo de 14 % exige poco más y su costo se suma al piso sin mezclarse con la meta. El desempleo imputado solo importa en metas altas (80 % o más), que las cajas no incluyen.
4. **Soluciones de igual costo.** En p = 0.50 con 20 %, el puntaje mínimo es 0.18 y no 0.24 con los mismos resultados: hay más de una solución óptima. Conviene confirmar que las estadísticas de la caja no dependen de cuál elige el solver.

**Contraste que hay que explicar.** En el Modelo 1, p sí cambia el resultado (con el mismo presupuesto salen 576,975 personas con p = 0.50 y 588,501 con p = 0.75, contra 564,443 del caso base), porque allí el presupuesto es fijo y p cambia a cuántos hogares alcanza. En el Modelo 2 el costo es la salida, y por eso p solo mueve el costo.

**Cómo revisarlo.**
- Confirmar en `modelo2.py` y `datos_modelo.py` qué costos dependen de p (la hipótesis 1) con una corrida que fije todo y varíe solo p.
- Correr las cajas con metas altas (50 %, 80 %) para ver si ahí sí se mueven con p, SevEdu y desempleo imputado.
- Diseñar sensibilidades que toquen lo que la meta compra: el costo de la consulta de salud (por ejemplo, las 4 consultas descartadas en la mejora 7), el costo del ciclo CLEI y el de aseguramiento.
- Comprobar que las estadísticas de la caja son iguales entre las soluciones óptimas alternativas (hipótesis 4).

**Por qué importa.** Si las sensibilidades no mueven la posición de los pobres, el análisis de sensibilidad del Modelo 2 no está probando la solidez de la parte que más interesa (quién sale y qué tan privados quedan los que siguen), y habría que reemplazarlas por otras más informativas.
