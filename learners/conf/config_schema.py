from strictyaml import Map, Str, Int, Seq, Bool, Any, Optional, MapPattern, EmptyDict, EmptyNone

config_schema = Map(
    {
        Optional("learners", default={"theme": "dark", "branding": False, "language": "en"}): Map(
            {
                Optional("theme", default="dark"): Str(),
                Optional("branding", default=False): Bool(),
                Optional("language", default="en"): Str(),
            }
        ),
        "jwt": Map(
            {
                "jwt_secret_key": Str(),
                Optional("jwt_access_token_duration", default=120): Int(),
                Optional("jwt_for_vnc_access", default=True): Bool(),
            }
        ),
        "database": Map(
            {
                "db_uri": Str(),
            }
        ),
        Optional("mail", drop_if_none=True): EmptyDict()
        | Map(
            {
                Optional("server", default=""): Str(),
                Optional("port", default=587): Int(),
                Optional("username", default=""): Str(),
                Optional("password", default=""): Str(),
                Optional("tls", default=True): Bool(),
                Optional("ssl", default=False): Bool(),
            }
        ),
        "users": MapPattern(
            Str(),
            Map(
                {
                    Optional("is_admin", default=False): Bool(),
                    "password": Str(),
                    Optional("vnc_clients"): MapPattern(
                        Str(),
                        Map(
                            {
                                "target": Str(),
                                Optional("tooltip", default="Access client"): Str(),
                                Optional("server", default="default"): Str(),
                                Optional("username"): Str(),
                                Optional("password"): Str(),
                            }
                        ),
                    ),
                }
            ),
        ),
        "venjix": Map(
            {
                "auth_secret": Str(),
                "url": Str(),
            }
        ),
        Optional("documentation", default={"directory": "static/documentation", "endpoint": "/documentation"}): Map(
            {
                Optional("directory", default="static/documentation"): Str(),
                Optional("endpoint", default="/documentation"): Str(),
            }
        ),
        Optional("exercises", default={"directory": "static/exercises", "endpoint": "/exercises"}): Map(
            {
                Optional("directory", default="static/exercises"): Str(),
                Optional("endpoint", default="/exercises"): Str(),
            }
        ),
        Optional("callback", default={"endpoint": "/callback"}): Map(
            {
                Optional("endpoint", default="/callback"): Str(),
            }
        ),
        "novnc": Map(
            {
                "server": Str(),
            }
        ),
    }
)
