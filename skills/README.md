# AI Agent Skills - PrimeFire API

Este directorio contiene **Agent Skills** siguiendo el estándar [Agent Skills](https://agentskills.io). Las skills proporcionan patrones, convenciones y directrices específicas del dominio que ayudan a los asistentes de IA a entender los requisitos del proyecto PrimeFire API.

## ¿Qué son las Skills?

[Agent Skills](https://agentskills.io) es un formato abierto para extender las capacidades de los agentes de IA con conocimiento especializado. Desarrollado originalmente por Anthropic y liberado como estándar abierto, ahora es adoptado por múltiples productos de agentes.

Las skills enseñan a los asistentes de IA cómo realizar tareas específicas. Cuando una IA carga una skill, obtiene contexto sobre:

- Reglas críticas (qué siempre/nunca hacer)
- Patrones y convenciones de código
- Flujos de trabajo específicos del proyecto
- Referencias a documentación detallada

## Configuración

Ejecuta el script de configuración para configurar las skills:

```bash
./skills/setup.sh
```

Esto crea symlinks para que cada herramienta encuentre las skills en su ubicación esperada:

| Herramienta | Symlink Creado |
|------------|----------------|
| Claude Code / OpenCode | `.claude/skills/` |
| Codex (OpenAI) | `.codex/skills/` |
| GitHub Copilot | `.github/skills/` |
| Gemini CLI | `.gemini/skills/` |

Después de ejecutar la configuración, reinicia tu asistente de IA para cargar las skills.

## Cómo Usar las Skills

Las skills son descubiertas automáticamente por el agente de IA. Para cargar manualmente una skill durante una sesión:

```
Read skills/{skill-name}/SKILL.md
```

## Skills Disponibles

### Meta Skills (Anthropics)

| Skill | Descripción |
|-------|-------------|
| `skill-creator` | Crear nuevas skills de IA |
| `skill-sync` | Sincronizar metadata con AGENTS.md |

### Meta Skills (Prowler)

| Skill | Descripción |
|-------|-------------|
| `skill-creator-prowler` | Crear skills siguiendo el estándar de Prowler |
| `skill-sync-prowler` | Sincronizar skills con AGENTS.md (estilo Prowler) |

### Skills de Desarrollo

| Skill | Descripción |
|-------|-------------|
| `fastapi-templates` | Templates de proyectos FastAPI |
| `python-testing-patterns` | Patrones de testing en Python |
| `find-skills` | Buscar skills en el ecosistema |
| `mcp-builder` | Crear servidores MCP |

### Skills de Documentación

| Skill | Descripción |
|-------|-------------|
| `obsidian-markdown` | Markdown para Obsidian |

### Skills de Agentes

| Skill | Descripción |
|-------|-------------|
| `self-improving-agent` | Agente auto-mejorable |
| `memory-merger` | Consolidar memorias de aprendizaje |

## Estructura del Directorio

```
skills/
├── {skill-name}/
│   ├── SKILL.md              # Requerido - instrucciones principales y metadata
│   ├── scripts/              # Opcional - código ejecutable
│   ├── assets/               # Opcional - templates, esquemas, recursos
│   └── references/           # Opcional - enlaces a documentación local
└── README.md                 # Este archivo
```

## Por qué las Secciones Auto-invoke?

**Problema**: Los asistentes de IA (Claude, Gemini, etc.) no invocan confiablemente las skills automáticamente incluso cuando el `Trigger:` en la descripción de la skill coincide con la solicitud del usuario.

**Solución**: Los archivos `AGENTS.md` (o `AGENDA.md` en este proyecto) contienen una sección **Auto-invoke Skills** que ordena explícitamente a la IA: "Cuando realices X acción, SIEMPRE invoca Y skill PRIMERO."

**Automatización**: En lugar de mantener manualmente estas secciones, puedes ejecutar `skill-sync` después de crear o modificar una skill:

```bash
./skills/skill-sync/assets/sync.sh
```

Esto lee `metadata.scope` y `metadata.auto_invoke` de cada `SKILL.md` y genera las tablas Auto-invoke en los archivos correspondientes.

## Creando Nuevas Skills

Usa la skill `skill-creator` como guía:

```
Read skills/skill-creator/SKILL.md
```

### Checklist Rápido

1. Crear directorio: `skills/{skill-name}/`
2. Agregar `SKILL.md` con frontmatter requerido
3. Agregar campos `metadata.scope` y `metadata.auto_invoke`
4. Mantener contenido conciso (menos de 500 líneas)
5. Referenciar documentación existente en lugar de duplicar
6. Ejecutar `./skills/skill-sync/assets/sync.sh` para actualizar AGENTS.md
7. Agregar a la tabla de skills en AGENDA.md

## Principios de Diseño

- **Conciso**: Solo incluir lo que la IA no sabe automáticamente
- **Revelación progresiva**: Apuntar a documentación detallada, no duplicar
- **Reglas críticas primero**: Liderar con patrones SIEMPRE/NUNCA
- **Ejemplos mínimos**: Mostrar patrones, no tutoriales

## Recursos

- [Agent Skills Standard](https://agentskills.io) - Especificación del estándar
- [Agent Skills GitHub](https://github.com/anthropics/skills) - Ejemplos de skills
- [Claude Code Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Guía de creación de skills
- [PrimeFire AGENDA.md](../AGENDA.md) - Reglas generales del agente
