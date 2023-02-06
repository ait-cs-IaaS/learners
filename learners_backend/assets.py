from flask_assets import Bundle


def get_bundle():
    return {
        "theme.css": Bundle(
            "css/theme.scss",
            filters="libsass",
            depends="**/*.scss",
            output="gen/theme.%(version)s.css",
        )
    }
