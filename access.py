#!/usr/bin/env python3
"""
Tilgang til å lese tastetrykk på macOS.

En aktiv event tap krever to tillatelser:

  Inndataovervåking  (kTCCServiceListenEvent)  — å se hendelsene
  Tilgjengelighet    (kTCCServiceAccessibility) — å endre/svelge dem

Inndataovervåking kan bes om via Quartz. Tilgjengelighet krever
AXIsProcessTrustedWithOptions, som pyobjc bare eksponerer gjennom
ApplicationServices — en modul PyInstaller ikke får med seg. Vi laster derfor
rammeverket rett fra systemet med ctypes. Det virker likt fra kildekode og fra
en buntet .app, og er den eneste kallet som faktisk *legger appen inn i lista*
og viser Apples egen dialog.
"""
import ctypes
import ctypes.util

import Quartz

_lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library("ApplicationServices"))
_cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))

_lib.AXIsProcessTrusted.restype = ctypes.c_bool
_lib.AXIsProcessTrustedWithOptions.restype = ctypes.c_bool
_lib.AXIsProcessTrustedWithOptions.argtypes = [ctypes.c_void_p]

_cf.CFDictionaryCreate.restype = ctypes.c_void_p
_cf.CFStringCreateWithCString.restype = ctypes.c_void_p
_cf.CFRelease.argtypes = [ctypes.c_void_p]

_kCFBooleanTrue = ctypes.c_void_p.in_dll(_cf, "kCFBooleanTrue")
_kCFTypeDictionaryKeyCallBacks = ctypes.c_void_p.in_dll(
    _cf, "kCFTypeDictionaryKeyCallBacks")
_kCFTypeDictionaryValueCallBacks = ctypes.c_void_p.in_dll(
    _cf, "kCFTypeDictionaryValueCallBacks")


def _cfstr(s: str):
    return _cf.CFStringCreateWithCString(None, s.encode(), 0x08000100)  # UTF-8


def accessibility(prompt=False) -> bool:
    """Har vi Tilgjengelighet? Med prompt=True viser macOS dialogen og legger
    appen inn i lista — det er den eneste måten den havner der av seg selv."""
    if not prompt:
        return bool(_lib.AXIsProcessTrusted())
    key = _cfstr("AXTrustedCheckOptionPrompt")
    keys = (ctypes.c_void_p * 1)(key)
    vals = (ctypes.c_void_p * 1)(_kCFBooleanTrue)
    opts = _cf.CFDictionaryCreate(
        None, keys, vals, 1,
        ctypes.byref(_kCFTypeDictionaryKeyCallBacks),
        ctypes.byref(_kCFTypeDictionaryValueCallBacks))
    try:
        return bool(_lib.AXIsProcessTrustedWithOptions(opts))
    finally:
        _cf.CFRelease(opts)
        _cf.CFRelease(key)


def input_monitoring(prompt=False) -> bool:
    if Quartz.CGPreflightListenEventAccess():
        return True
    if prompt:
        return bool(Quartz.CGRequestListenEventAccess())
    return False


def status() -> dict:
    return {"tilgjengelighet": accessibility(),
            "inndataovervåking": bool(Quartz.CGPreflightListenEventAccess())}


def have_all() -> bool:
    s = status()
    return s["tilgjengelighet"] and s["inndataovervåking"]


def request_all() -> bool:
    """Be om begge. Viser Apples dialoger og legger appen inn i begge listene."""
    input_monitoring(prompt=True)
    accessibility(prompt=True)
    return have_all()


if __name__ == "__main__":
    print(status())
