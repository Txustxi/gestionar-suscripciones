# Gestor de Suscripciones

Esta herramienta permite mostrar las suscripciones reales asociadas a una cuenta de correo electrónico.
Utiliza el protocolo IMAP para inspeccionar los mensajes de la bandeja de entrada y extraer la información de las listas de distribución.

## Uso rápido

```bash
python3 suscripciones.py --servidor imap.ejemplo.com --correo usuario@ejemplo.com
```
El programa solicitará la contraseña de la cuenta para iniciar sesión y, a continuación, listará las suscripciones detectadas.

## Requisitos

- Python 3
- Acceso IMAP habilitado en la cuenta de correo.

