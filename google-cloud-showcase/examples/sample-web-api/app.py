"""Tiny Flask-shaped example with deliberate AppSec footguns for the scanner."""

import pickle
import ssl
import urllib.request

# Deliberate: TLS verification off
ssl._create_default_https_context = ssl._create_unverified_context

PASSWORD = "hardcoded-demo-password"


def load_blob(raw: bytes):
    return pickle.loads(raw)


def fetch(url: str):
    return urllib.request.urlopen(url, context=ssl._create_unverified_context())
