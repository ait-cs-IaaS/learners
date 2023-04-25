from strictyaml import Any, Bool, EmptyDict, EmptyList, EmptyNone, Int, Map, MapPattern, Optional, Seq, Str

config_schema = Map(
    {
        Optional("learners"): EmptyDict()
        | Map(
            {
                Optional("theme"): EmptyDict()
                | Map(
                    {
                        Optional("primary", default="#666666"): Str(),
                        Optional("secondary", default="#666666"): Str(),
                        Optional("success", default="#666666"): Str(),
                        Optional("primary_color", default="#666666"): Str(),
                        Optional("sidebar_background_color", default="#666666"): Str(),
                        Optional("menu_active_color", default="#ffffff"): Str(),
                        Optional("menu_inactive_color", default="#a3a3a3"): Str(),
                        Optional("main_background_color", default="#f6f6f6"): Str(),
                        Optional("main_text_color", default="#191b23"): Str(),
                        Optional("success_color", default="#4a8864"): Str(),
                        Optional("success_color_light", default="#6cbd8e"): Str(),
                        Optional("fail_color", default="#da1e55"): Str(),
                        Optional("fail_color_light", default="#d34a5d"): Str(),
                        Optional("info_color", default="#619dc7"): Str(),
                        Optional("info_color_light", default="#87b6d8"): Str(),
                        Optional("light_grey_color", default="#dedfe4"): Str(),
                        Optional("mid_grey_color", default="#c0c0c0"): Str(),
                        Optional("dark_grey_color", default="#8c8c8c"): Str(),
                        Optional("input_placeholder_color", default="#bfbfbf"): Str(),
                        Optional("input_background_color", default="#dedfe4"): Str(),
                        Optional("input_text_color", default="#191b23"): Str(),
                        Optional("nav_width", default="60px"): Str(),
                    }
                ),
                Optional("logo"): Str(),
                Optional("landingpage", default="documentation"): Str(),
                Optional("language_code", default="en"): Str(),
                Optional("upload_folder", default="backend/static/uploads"): Str(),
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
                    Optional("groups"): Seq(Str()),
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
        Optional("tabs"): EmptyDict()
        | Map(
            {
                Optional("standard", default={"documentation": {}, "exercises": {}, "presentations": {}}): MapPattern(
                    Str(),
                    EmptyDict()
                    | Map(
                        {
                            Optional("tooltip"): Str(),
                            Optional("icon"): Str(),
                            Optional("url"): Str(),
                        }
                    ),
                ),
                Optional("staticsites"): MapPattern(
                    Str(),
                    EmptyDict()
                    | Map(
                        {
                            Optional("tooltip"): Str(),
                            Optional("icon"): Str(),
                            Optional("proxy", default=False): Bool(),
                            "url": Str(),
                        }
                    ),
                ),
            }
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
        Optional("init_notifications"): EmptyList()
        | Seq(
            Map(
                {
                    "title": Str(),
                    "msg": Str(),
                }
            )
        ),
    }
)
