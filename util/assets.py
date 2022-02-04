from flask_assets import Bundle

def get_bundle(theme):
    theme_bundle = {
        'theme.css': Bundle(
            'main_{0}.scss'.format(theme),
            filters='libsass',
            depends='*.scss',
            output='gen/theme.%(version)s.css'
        )}
    return theme_bundle
