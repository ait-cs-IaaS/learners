from strictyaml import Bool, EmptyDict, EmptyList, Int, Map, MapPattern, Optional, Seq, Str, Any

config_schema = Map(
    {
        Optional("learners", default={"landingpage": "documentation"}): EmptyDict()
        | Map(
            {
                Optional(
                    "theme",
                    default={
                        "primary": "#666666",
                        "secondary": "#009899",
                        "success": "#009899",
                    },
                ): EmptyDict()
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
                Optional(
                    "logo",
                    default="<svg viewBox='0 0 343.71 136.32' style='enable-background:new 0 0 200 200;' xml:space='preserve' xmlns='http://www.w3.org/2000/svg'><polygon points='343.71 41.4 343.71 0 236 0 236 41.4 268.17 41.4 268.17 136.32 311.54 136.32 311.54 41.4 343.71 41.4' style='fill: #fff;'/><rect x='184.69' width='43.37' height='136.32' style='fill: #fff;'/><polygon points='133.38 136.32 176.75 136.32 176.75 0 136.22 0 0 136.32 55.97 136.32 133.38 58.82 133.38 136.32' style='fill: #fff;'/></svg>",
                ): Str(),
                Optional("headline", default="Welcome to the CyberRange"): Str(),
                Optional(
                    "welcomeText",
                    default="Please log in with your assigned credentials:",
                ): Str(),
                Optional("landingpage", default="documentation"): Str(),
                Optional("language_code", default="en"): Str(),
                Optional("upload_folder", default="backend/statics/uploads"): Str(),
                Optional("upload_extensions", default=["txt", "pdf", "png", "jpg", "jpeg", "gif", "json", "svg"]): Seq(Str()),
            }
        ),
        Optional("jwt", default={"jwt_secret_key": "3668da1b-cef1-5085-ae20-443409c9cc73"},): Map(
            {
                Optional("jwt_secret_key", default="3668da1b-cef1-5085-ae20-443409c9cc73"): Str(),
                Optional("jwt_access_token_duration", default=720): Int(),
                Optional("jwt_for_vnc_access", default=True): Bool(),
            }
        ),
        Optional("database", default={"db_uri": "sqlite:///data.db"}): Map(
            {
                Optional("db_uri", default="sqlite:///data.db"): Str(),
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
                    Optional("meta"): Any(),
                }
            ),
        ),
        Optional("tabs", default={"documentation": True, "exercises": False, "presentations": False}): MapPattern(
            Str(),
            Bool()
            | EmptyDict()
            | Map(
                {
                    Optional("tooltip"): Str(),
                    Optional("icon"): Str(),
                    Optional("url"): Str(),
                    Optional("proxy"): Bool(),
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
        Optional("statics", default={"directory": "statics", "serve_mode": "role"}): Map(
            {
                Optional("directory", default="statics"): Str(),
                Optional("serve_mode", default="role"): Str(),
            }
        ),
        Optional("exercise_json", default="statics/hugo/exercises.json"): Str(),
        Optional("questionaire_json", default="statics/hugo/questionaires.json"): Str(),
        Optional("page_json", default="statics/hugo/pages.json"): Str(),
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
