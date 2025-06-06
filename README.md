# Gestor de Suscripciones

Esta herramienta permite mostrar las suscripciones reales asociadas a una cuenta de correo electrónico.
Utiliza el protocolo IMAP para inspeccionar los mensajes de la bandeja de entrada y extraer la información de las listas de distribución.

Para cada remitente se recuperan los valores reales de las cabeceras `List-Id` y
`List-Unsubscribe`, de modo que las suscripciones mostradas corresponden a las
listas en las que la cuenta está dada de alta.

## Uso rápido

```bash
python3 suscripciones.py --servidor imap.ejemplo.com --correo usuario@ejemplo.com
```
El programa solicitará la contraseña de la cuenta para iniciar sesión y, a continuación,
listará las suscripciones detectadas. Opcionalmente se puede indicar el buzón a revisar
mediante `--mailbox`.

## Requisitos

- Python 3
- Acceso IMAP habilitado en la cuenta de correo.

