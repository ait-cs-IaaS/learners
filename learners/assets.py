from flask_assets import Bundle


def get_bundle(theme):
    return {
        "theme.css": Bundle(
            "css/theme_{0}.scss".format(theme),
            filters="libsass",
            depends="**/*.scss",
            output="gen/theme.%(version)s.css",
        )
    }
