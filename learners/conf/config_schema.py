from strictyaml import Map, Str, Int, Seq, Bool, Any, Optional, MapPattern

config_schema = Map(
    {
        "learners": Map(
            {
                Optional("theme", default="dark"): Str(),
                Optional("branding", default=False): Bool(),
                "htpasswd": Str(),
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
        "components": Map(
            {
                "venjix_auth_secret": Str(),
                "urls": Map(
                    {
                        "venjix": Str(),
                        "callback": Str(),
                        "documentation": Str(),
                        "exercises": Str(),
                        "novnc": Str(),
                    }
                ),
                "user_assignments": MapPattern(
                    Str(),
                    Map(
                        {
                            "vnc_clients": MapPattern(
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
                                minimum_keys=1,
                            ),
                            "ports": Map(
                                {
                                    "docs": Int(),
                                    "exercises": Int(),
                                }
                            ),
                        }
                    ),
                ),
            }
        ),
    }
)
