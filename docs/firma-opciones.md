# Opciones para firmar los ejecutables de Windows (informe de investigación)

Consulta: 23 de noviembre de 2026. No se adquirió ni registró nada. Compatible con `docs/firma-codigo.md`
(sin firma actual; SignPath Foundation como vía preparada, aún no solicitada).

## Hechos que condicionan todo

- Microsoft indica que los certificados EV ya no evitan SmartScreen; OV y EV se tratan igual y la reputación
  se acumula por hash del archivo y por identidad de firma, con "semanas y cientos de instalaciones limpias".
  Sin firma o con firma autofirmada: advertencia en cada versión nueva. Smart App Control (Windows 11) puede
  bloquear lo no firmado salvo reputación positiva.
  <https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation> (consultado 2026-11-23).
- Desde junio de 2023 las claves OV/EV deben estar en hardware (token FIPS o HSM en la nube); desde el
  1 de marzo de 2026 la validez máxima es de 460 días (CSC-31); SSL.com usa 458 y DigiCert 459.
  <https://cabforum.org/2025/11/17/ballot-csc-31-maximum-validity-reduction> ·
  <https://www.ssl.com/article/reminder-reduced-code-signing-certificate-lifecycles/>
- Consecuencia: un certificado comercial exige renovación anual y un cambio de certificado puede reiniciar la
  reputación (un solo reporte de usuario, no oficial).

## Opciones

**1. SignPath Foundation (gratuita, código abierto).**
Requisitos (<https://signpath.org/terms>, 2026-11-23): licencia aprobada por OSI en todos los componentes, sin
doble licencia comercial; proyecto activo y ya publicado; build automatizado y verificable desde el repositorio;
cada firma con aprobación manual; el equipo debe mantener el repositorio; MFA en SignPath y en el repositorio;
metadatos de producto y versión; sin herramientas de seguridad ofensiva ni código propietario; línea de
atribución obligatoria "Free code signing provided by SignPath.io, certificate by SignPath Foundation.".
El editor que muestra Windows es SignPath Foundation, no la universidad ni el equipo. Los términos no mencionan
restricciones por país ni exigen persona jurídica (a confirmar en la solicitud). Coste 0 USD. Plazo: no
publicado; depende de la revisión humana (estimar semanas). GitHub Actions: integración nativa de origen de
build verificable, claves en HSM de SignPath, nunca exportadas. SmartScreen: reputación progresiva, compartida
por el certificado de la fundación. Limitaciones: sin garantía de aceptación; depende de elegir licencia OSI.

**2. Azure Artifact Signing (antes Trusted Signing).**
Certificados públicos solo para organizaciones en EE. UU., Canadá, UE, Reino Unido, Australia, Nueva Zelanda,
Japón, Corea del Sur, Singapur, Suiza, Noruega e Israel; individuos solo en EE. UU. y Canadá.
Nicaragua no figura: la opción no está disponible para el equipo (ni como persona ni como universidad local).
<https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart>. Precio de referencia 9,99 USD/mes
(Basic, 5000 firmas) pero exige suscripción Azure de pago (no gratuita ni patrocinada;
<https://learn.microsoft.com/en-us/azure/artifact-signing/faq>). Validación 1 a 30 días hábiles. Acción de
GitHub y firma sin exportar clave. SmartScreen progresivo. Posible solo vía una entidad legal en un país
admitido (no recomendable: el editor sería ajeno al proyecto).

**3. Certum Open Source Code Signing (SimplySign, nube).**
Dirigido a desarrolladores de código abierto; certificado a nombre de persona natural con prefijo
"Open Source Developer"; verificación documental; RSA 3072; clave en tarjeta virtual en la nube; hasta 5000
firmas al mes. Precio en la tienda: 49 EUR (otras páginas de la tienda mostraron 69 y 359 EUR para "set";
verificar al comprar); validez típica de un año. Restricción de país no declarada. Integración con Actions: no
documentada oficialmente; SimplySign requiere sesión con código móvil, lo que complica el CI sin intervención
(riesgo alto; probar firmando manualmente en un equipo antes). SmartScreen progresivo; el nombre mostrado es
el de la persona. <https://shop.certum.eu/open-source-code-signing-on-simplysign.html>

**4. OV de una CA comercial (SSL.com, DigiCert, Sectigo).**
OV para organizaciones con registro mercantil (SSL.com OV 129 USD/año a un año más suscripción eSigner;
<https://www.ssl.com/certificates/code-signing/buy/>; DigiCert OV unos 400 USD/año y Sectigo unos 219 USD/año
según revendedor, sin confirmar en la CA). Para personas, SSL.com ofrece IV sin entidad. Validación estándar
3 a 5 días, exprés 599 USD. Actions: eSigner (API, nube) o DigiCert KeyLocker; sin exportar clave. Coste real
anual probable: 250 a 500 USD. SmartScreen progresivo (igual que OV).
Limitaciones: documentos de entidad nicaragüense pueden no ser aceptados por todas las CA (verificar con cada
una antes de pagar); renovación anual.

**5. EV (DigiCert, Sectigo, SSL.com).**
Más estricto (entidad legal verificable, a menudo D-U-N-S) y de 300 a 700 USD/año o más. Ya no da reputación
inmediata en SmartScreen: no se justifica.

**6. Autofirmado.** 0 USD. Solo pruebas internas (instalar el certificado en la máquina de prueba). Mismo
comportamiento que sin firma ante SmartScreen y Smart App Control; no usar para publicar.

**7. Sin firma (estado actual).** 0 USD. Advertencia en cada versión, posible bloqueo por Smart App Control y
por políticas empresariales. Mitigaciones: publicar sumas SHA-256 y el procedimiento "Ejecutar de todas formas".

## Tabla comparativa

| Opción | Coste anual (USD) | Identidad / país | Actions y claves | SmartScreen | Nicaragua |
|---|---|---|---|---|---|
| SignPath Foundation | 0 | Proyecto OSI; editor = Fundación | Sí, HSM propio | Progresiva | Sin restricción declarada |
| Azure Artifact Signing | ~120 + Azure | Org. en 12 regiones; individuos EE. UU./Canadá | Sí | Progresiva | No disponible |
| Certum Open Source | ~50 a 75 EUR | Persona natural, documentos | No documentado | Progresiva | No declarada |
| OV comercial | ~130 a 500 | Entidad registrada (o IV persona) | Sí (eSigner, KeyLocker) | Progresiva | Por verificar con la CA |
| EV | ~300 a 700+ | Entidad verificable | Sí | Progresiva (igual que OV) | Por verificar |
| Autofirmado | 0 | Ninguna | Local | Advertencia | Sí (solo pruebas) |
| Sin firma | 0 | Ninguna | No aplica | Advertencia cada versión | Sí |

## Recomendación

1. Seguir con SignPath Foundation: es la única vía gratuita, compatible con Actions y con claves no exportables,
   sin restricción de país declarada. Los pasos previos ya están en `docs/firma-codigo.md`: elegir y publicar una
   licencia OSI, designar autores/revisores/aprobadores con MFA, metadatos de producto y versión, línea de
   atribución. Contrapartida aceptable: el editor será la Fundación.
2. Plan B si la solicitud se rechaza: Certum Open Source (más barato, a nombre de una persona responsable) tras
   una prueba de firma manual, o un OV de SSL.com/DigiCert si la universidad aporta documentos de entidad.
3. No pagar EV por SmartScreen. Descartar Azure Artifact Signing por país. Mientras tanto, mantener la
   distribución sin firma con sumas SHA-256 y aviso honesto de la advertencia, sin prometer ausencia de avisos.
4. Aunque se firme, la reputación es progresiva: informar a los usuarios y no declarar que el bloqueo desaparece
   desde la primera descarga.

Fuentes de precios de terceros (DigiCert, Sectigo) provienen de revendedores y deben confirmarse en la CA.
