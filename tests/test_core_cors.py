from backend.core.cors import CorsSettings


def test_origins_list_from_string():
    """String with multiple values"""
    settings = CorsSettings(
        cors_allow_origins="http://a.com, http://b.com",
        cors_allow_methods="GET",
        cors_allow_headers="*"
    )

    assert settings.origins_list == ["http://a.com", "http://b.com"]


def test_origins_list_wildcard():
    """Wildcard '*'"""
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="GET",
        cors_allow_headers="*"
    )

    assert settings.origins_list == ["*"]


def test_origins_list_from_list():
    """Direct list"""
    settings = CorsSettings(
        cors_allow_origins=["http://a.com", "http://b.com"],
        cors_allow_methods="GET",
        cors_allow_headers="*"
    )

    assert settings.origins_list == ["http://a.com", "http://b.com"]


def test_origins_list_strip_and_filter():
    """String with spaces and empty spaces"""
    settings = CorsSettings(
        cors_allow_origins=" http://a.com , , http://b.com  ",
        cors_allow_methods="GET",
        cors_allow_headers="*"
    )

    assert settings.origins_list == ["http://a.com", "http://b.com"]


def test_origins_list_empty_list():
    """Empty list → default '*'"""
    settings = CorsSettings(
        cors_allow_origins=[],
        cors_allow_methods="GET",
        cors_allow_headers="*"
    )

    assert settings.origins_list == ["*"]


# -----------
# - METHODS -
# -----------

def test_methods_list_string():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="GET, POST",
        cors_allow_headers="*"
    )

    assert settings.methods_list == ["GET", "POST"]


def test_methods_list_wildcard():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="*",
        cors_allow_headers="*"
    )

    assert settings.methods_list == ["*"]


def test_methods_list_from_list():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods=["GET", "POST"],
        cors_allow_headers="*"
    )

    assert settings.methods_list == ["GET", "POST"]


def test_methods_list_empty():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods=[],
        cors_allow_headers="*"
    )

    assert settings.methods_list == ["*"]


# -----------
# - HEADERS -
# -----------
def test_headers_list_string():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="GET",
        cors_allow_headers="Authorization, Content-Type"
    )

    assert settings.headers_list == ["Authorization", "Content-Type"]


def test_headers_list_wildcard():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="GET",
        cors_allow_headers="*"
    )

    assert settings.headers_list == ["*"]


def test_headers_list_from_list():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="GET",
        cors_allow_headers=["Authorization"]
    )

    assert settings.headers_list == ["Authorization"]


def test_headers_list_empty():
    settings = CorsSettings(
        cors_allow_origins="*",
        cors_allow_methods="GET",
        cors_allow_headers=[]
    )

    assert settings.headers_list == ["*"]