from django.conf import settings


def test_upload_limits_are_bounded_and_product_images_have_an_explicit_cap() -> None:
    assert settings.DATA_UPLOAD_MAX_MEMORY_SIZE == 2 * 1024 * 1024
    assert settings.FILE_UPLOAD_MAX_MEMORY_SIZE == 2 * 1024 * 1024
    assert settings.PRODUCT_IMAGE_MAX_BYTES == 10 * 1024 * 1024
