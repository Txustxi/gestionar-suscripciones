#!/usr/bin/env python3
"""Herramienta para listar suscripciones de correo usando IMAP."""

import argparse
import getpass
import imaplib
import email
from collections import defaultdict
from email.header import decode_header
from typing import Dict, Set


def conectar(imap_server: str, email_user: str, password: str) -> imaplib.IMAP4_SSL:
    """Establece una conexión IMAP segura."""
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_user, password)
    return imap


def obtener_suscripciones(imap: imaplib.IMAP4_SSL, mailbox: str = "INBOX") -> Dict[str, Set[str]]:
    """Devuelve un diccionario de remitentes y sus cabeceras de desuscripción."""
    suscripciones: Dict[str, Set[str]] = defaultdict(set)
    imap.select(mailbox)
    status, data = imap.search(None, "ALL")
    if status != "OK":
        return suscripciones

    for num in data[0].split():
        status, msg_data = imap.fetch(num, '(RFC822.HEADER)')
        if status != 'OK' or not msg_data:
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        list_unsub = msg.get('List-Unsubscribe')
        list_id = msg.get('List-Id')
        if list_unsub or list_id:
            from_addr = email.utils.parseaddr(msg.get('From'))[1]
            if list_unsub:
                suscripciones[from_addr].add(list_unsub)
            if list_id:
                suscripciones[from_addr].add(list_id)
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


def mostrar_suscripciones(suscripciones: Dict[str, Set[str]]):
    if not suscripciones:
        print("No se encontraron suscripciones")
        return
    print("Suscripciones encontradas:")
    for remitente, datos in suscripciones.items():
        print(f"- {remitente}")
        for d in datos:
            print(f"    {decodificar(d)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Muestra las suscripciones asociadas a una cuenta de correo")
    parser.add_argument("--servidor", required=True, help="Servidor IMAP, por ejemplo: imap.gmail.com")
    parser.add_argument("--correo", required=True, help="Dirección de correo electrónico")
    parser.add_argument("--mailbox", default="INBOX", help="Buzón a inspeccionar")
    args = parser.parse_args()

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

