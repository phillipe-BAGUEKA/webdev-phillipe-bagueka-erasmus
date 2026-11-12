"""Reuse the original migration verbatim, without duplicating or editing it."""

from importlib import import_module

Migration = import_module("src.data.migrations.0001_initial").Migration
