#!/usr/bin/env python3
"""Herramienta para listar suscripciones de correo usando IMAP."""

import argparse
import getpass
import imaplib
import email
from collections import defaultdict
from email.header import decode_header
from typing import DefaultDict, Dict, Set
import sys


def conectar(imap_server: str, email_user: str, password: str) -> imaplib.IMAP4_SSL:
    """Establece una conexión IMAP segura."""
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_user, password)
    return imap


def obtener_suscripciones(imap: imaplib.IMAP4_SSL, mailbox: str = "INBOX") -> Dict[str, Dict[str, Set[str]]]:
    """Devuelve las cabeceras de listas de correo agrupadas por ``List-Id``."""
    suscripciones: DefaultDict[str, Dict[str, Set[str]]] = defaultdict(lambda: {"remitentes": set(), "unsub": set()})

    imap.select(mailbox)
    status, data = imap.search(None, "ALL")
    if status != "OK" or not data or not data[0]:
        return suscripciones

    for num in data[0].split():
        status, msg_data = imap.fetch(num, '(BODY.PEEK[HEADER])')
        if status != 'OK' or not msg_data:
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        list_id = msg.get('List-Id')
        list_unsub = msg.get('List-Unsubscribe')
        if not list_id and not list_unsub:
            continue
        key = list_id if list_id else email.utils.parseaddr(msg.get('From'))[1]
        remitente = email.utils.parseaddr(msg.get('From'))[1]
        suscripciones[key]["remitentes"].add(remitente)
        if list_unsub:
            suscripciones[key]["unsub"].add(list_unsub)

    return suscripciones


def decodificar(texto: str) -> str:
    if not texto:
        return ""
    partes = decode_header(texto)
    resultado = []
    for parte, cod in partes:
        if isinstance(parte, bytes):
            resultado.append(parte.decode(cod or 'utf-8', errors='ignore'))
        else:
            resultado.append(parte)
    return ''.join(resultado)


def mostrar_suscripciones(suscripciones: Dict[str, Dict[str, Set[str]]]):
    if not suscripciones:
        print("No se encontraron suscripciones")
        return

    print("Suscripciones encontradas:")
    for list_id, datos in suscripciones.items():
        print(f"- {decodificar(list_id)}")
        for remitente in sorted(datos["remitentes"]):
            print(f"    Remitente: {remitente}")
        for unsub in sorted(datos["unsub"]):
            print(f"    Desuscribir: {decodificar(unsub)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Muestra las suscripciones asociadas a una cuenta de correo"
    )
    parser.add_argument("--servidor", required=True, help="Servidor IMAP, por ejemplo: imap.gmail.com")
    parser.add_argument("--correo", required=True, help="Dirección de correo electrónico")
    parser.add_argument("--mailbox", default="INBOX", help="Buzón a inspeccionar")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        # Asegura que la salida utilice UTF-8 para evitar errores con caracteres
        # no ASCII en sistemas cuyo locale no esté configurado.
        sys.stdout.reconfigure(encoding="utf-8")

    password = getpass.getpass(prompt=f"Contraseña para {args.correo}: ")
    try:
        imap = conectar(args.servidor, args.correo, password)
    except imaplib.IMAP4.error as exc:
        print(f"Error al conectar: {exc}")
        return 1

    try:
        subs = obtener_suscripciones(imap, args.mailbox)
        mostrar_suscripciones(subs)
    finally:
        imap.logout()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

