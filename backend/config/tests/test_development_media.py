import os
import subprocess
import sys
from pathlib import Path


def test_development_urls_serve_managed_product_media() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    assertions = """
import importlib
from tempfile import TemporaryDirectory
from pathlib import Path

import django

django.setup()

from django.test import Client, override_settings
from django.urls import Resolver404, clear_url_caches, resolve

import config.urls

with TemporaryDirectory() as directory:
    media_root = Path(directory)
    product_image = media_root / 'products' / 'example.jpg'
    product_image.parent.mkdir(parents=True)
    product_image.write_bytes(b'fictional-image-bytes')

    with override_settings(MEDIA_ROOT=media_root, ALLOWED_HOSTS=['testserver']):
        importlib.reload(config.urls)
        clear_url_caches()
        response = Client().get('/media/products/example.jpg')

    assert response.status_code == 200
    assert b''.join(response.streaming_content) == b'fictional-image-bytes'

with override_settings(DEBUG=False):
    importlib.reload(config.urls)
    clear_url_caches()
    try:
        resolve('/media/products/example.jpg')
    except Resolver404:
        pass
    else:
        raise AssertionError('Production URL configuration exposed development media')
"""

    subprocess.run(  # noqa: S603
        [sys.executable, "-c", assertions],
        cwd=backend_dir,
        env={
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "config.settings.development",
            "DATABASE_URL": "sqlite:///:memory:",
        },
        check=True,
    )
