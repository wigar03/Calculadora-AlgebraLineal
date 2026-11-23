# AGENTS.md — Instrucciones permanentes para agentes

## Objetivo y criterio de finalización
La calculadora debe resolver, desde la propia interfaz, los 49 ejercicios de `docs/INVENTARIO-EJERCICIOS.md`
mostrando procedimiento, resultado y verificación. Un ejercicio solo se acepta cuando su resultado coincide con
la referencia independiente (`tests/validacion/`) y está registrado en `docs/VALIDACION-EJERCICIOS.md`.
Los enunciados incompletos (IV-2 y IV-5) se registran aparte en `docs/INCIDENCIAS.md`; no se inventan.

## Arquitectura
- `src/solver`, `src/ecuaciones`, `src/matrices`: Gauss/Gauss-Jordan, determinante e inversa con `Fraction`.
- `src/biseccion/expresiones.py`: analizador seguro de f(x) (AST), compartido por los cuatro métodos.
- `src/biseccion`, `src/regla_falsa`, `src/secante`, `src/newton_raphson`, `src/derivadas`: métodos numéricos.
- `src/ui/web_server.py` (API JSON), `src/ui/web/*` (HTML/JS/CSS, KaTeX local en `vendor/`).
- `tests/`: `unittest` (Python) y `node --test` (`*.cjs`, sin dependencias externas).

## Agentes, cuentas y modelos autorizados
| Agente | Modelo | Área exclusiva (archivos) |
|---|---|---|
| Codex cuenta 1 (Plus) | gpt-6.1-sol xhigh | álgebra lineal: `src/solver`, `src/ecuaciones`, `src/matrices`, sus pruebas, vista de sistemas/matrices en `app.js` |
| Codex cuenta 2 (Team) | gpt-6.1-sol xhigh | métodos numéricos: `src/biseccion/metodo.py`, `src/regla_falsa`, `src/secante`, `src/newton_raphson`, `src/derivadas` y sus pruebas |
| Antigravity | gemini-4-neon-high | `src/biseccion/expresiones.py`, diagnósticos de entrada, LaTeX/KaTeX, pruebas de interfaz `*.cjs` |
| Claude Business | Opus 5.5 medium (Sonnet 5.5 para tareas ordinarias) | plan, contratos, revisión, `web_server.py`, `AGENTS.md`, `docs/`, referencias en `tests/validacion/`, integración y releases |

**Prohibido usar Claude Pro individual** (cuenta personal gestionada en Orca): ni como sesión, ni como cuota,
ni como respaldo cuando otra cuenta se agote. Si una cuenta se limita, el trabajo continúa con las demás.

## Trabajo paralelo, ramas y worktrees
- Cada agente trabaja en su propia rama `orca/<area>` y en su propio worktree creado por Orca.
- Nadie edita archivos de otra área. Para tocar un archivo ajeno, se pide al integrador mediante Orca.
- El integrador (Claude Business) es el único que fusiona en `main`. Nunca `push --force` ni reescritura publicada.

## Comandos
```
python -m unittest discover tests -v          # pruebas Python (incluye validación de ejercicios)
for f in tests/*.cjs; do node --test "$f"; done  # pruebas de interfaz sin dependencias
python main.py                                  # aplicación web local
python tests/validacion/generar_referencias.py   # regenera referencias (requiere sympy y mpmath)
```

## Commits
- Conventional Commits en español o inglés (`fix(parser): ...`, `test(numerical): ...`).
- Máximo 100 líneas modificadas (añadidas + eliminadas) por commit; el gancho `pre-commit` lo comprueba.
- Prohibido `Co-authored-by` o cualquier atribución a modelos o agentes; el gancho `commit-msg` lo rechaza.
- Respetar la identidad Git configurada del propietario. No usar `--no-verify`.

## Pruebas independientes
- Las referencias se calculan con SymPy/mpmath o `Fraction` en `tests/validacion/`, nunca con el código bajo prueba.
- Lineales: clasificación, solución exacta y sustitución A·X = B. Matrices: det, existencia de inversa, A·A⁻¹ = I.
- Raíces: dominio, datos iniciales, convergencia, comparación con la raíz de referencia (|x−r| ≤ 1e-6) y residuo.
- Cada ejercicio se prueba también por la vía del usuario (API de la página y, donde aplique, la interfaz).
- Quien implementa no aprueba solo su trabajo: el integrador revisa y ejecuta la batería completa.

## UX
No cambiar navegación, disposición, colores, tipografía, controles ni flujos sin autorización del propietario.
Permitido: corregir errores internos, ampliar capacidades matemáticas y mejorar los mensajes de error.
Si algo exige cambiar la UX, se documenta en `docs/INCIDENCIAS.md` y se consulta mediante Orca.

## Analizador y mensajes de error
Errores de sintaxis, de dominio y de convergencia se distinguen. Los mensajes indican qué parte falla y cómo
corregirla (p. ej. «Falta el operador de multiplicación entre 2 y x. Escribe 2*x»). No corregir en silencio
nada que cambie la interpretación. En sistemas, `x1`, `x₂`, `x_2` son variables indexadas.

## Integración y releases
1. El agente entrega su rama con pruebas en verde y un resumen de evidencia.
2. El integrador revisa el diff, ejecuta todas las pruebas y fusiona sin modificar funcionalidades ajenas.
3. Release (SemVer existente, `src/core/version.py`) solo con módulo completo verificado, notas en
   `docs/RELEASES.md` y `CHANGELOG.md`, y sin declarar validados ejercicios pendientes.

## Documentación y comunicación
Mantener al día `docs/ORCA-ESTADO.md`, `docs/REGISTRO-CAMBIOS.md`, `docs/INCIDENCIAS.md` y
`docs/VALIDACION-EJERCICIOS.md` con resultados realmente obtenidos. Preguntar al propietario mediante Orca solo
por enunciados incompletos, cambios de UX o decisiones irreversibles; mientras, seguir con el resto.
