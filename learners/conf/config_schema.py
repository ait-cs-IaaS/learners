from strictyaml import Any, Bool, EmptyDict, EmptyList, EmptyNone, Int, Map, MapPattern, Optional, Seq, Str

config_schema = Map(
    {
        Optional("learners", default={"theme": "dark", "language_code": "en"},): Map(
            {
                Optional("theme", default="dark"): Str(),
                Optional("landingpage", default="documentation"): Str(),
                Optional("language_code", default="en"): Str(),
                Optional("upload_folder", default="/var/tmp/"): Str(),
                Optional("upload_extensions", default=["txt", "pdf", "png", "jpg", "jpeg", "gif", "json", "svg"]): Seq(Str()),
            }
        ),
        "jwt": Map(
            {
                "jwt_secret_key": Str(),
                Optional("jwt_access_token_duration", default=720): Int(),
                Optional("jwt_for_vnc_access", default=True): Bool(),
            }
        ),
        "database": Map(
            {
                "db_uri": Str(),
            }
        ),
        "users": MapPattern(
            Str(),
            Map(
                {
                    "password": Str(),
                    Optional("admin", default=False): Bool(),
                    Optional("role", default="participant"): Str(),
                    Optional("vnc_clients"): MapPattern(
                        Str(),
                        Map(
                            {
                                "target": Str(),
                                Optional("tooltip", default="Access client"): Str(),
                                Optional("server", default="DEFAULT-VNC-SERVER"): Str(),
                                Optional("username"): Str(),
                                Optional("password"): Str(),
                            }
                        ),
                    ),
                }
            ),
        ),
        Optional("venjix", default={"auth_secret": "", "url": ""}): Map(
            {
                Optional("auth_secret", default=""): Str(),
                Optional("url", default=""): Str(),
            }
        ),
        Optional("callback", default={"endpoint": "/callback"}): Map(
            {
                Optional("endpoint", default="/callback"): Str(),
            }
        ),
        Optional("novnc", default={"server": ""}): Map(
            {
                Optional("server", default=""): Str(),
            }
        ),
        Optional("statics", default={"directory": "static", "serve_mode": "role"}): Map(
            {
                Optional("directory", default="static"): Str(),
                Optional("serve_mode", default="role"): Str(),
            }
        ),
        Optional("staticsites"): EmptyList()
        | Seq(
            Map(
                {
                    Optional("url", default=""): Str(),
                    Optional("id", default=""): Str(),
                    Optional("title", default=""): Str(),
                    Optional("icon", default="web"): Str(),
                }
            )
        ),
        Optional("serve_documentation", default=True): Bool(),
        Optional("serve_presentations", default=False): Bool(),
        Optional("serve_exercises", default=True): Bool(),
        Optional("exercise_json", default="static/hugo/exercises.json"): Str(),
        Optional("questionaire_json", default="static/hugo/questionaires.json"): Str(),
        Optional("questionaires_questions_json", default="static/hugo/questionaires_questions.json"): Str(),
    }
)
