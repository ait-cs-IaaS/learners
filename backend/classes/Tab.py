import numbers
import string


class Tab:
    def __init__(
        self,
        id: string,
        _type: string,
        base_url: string = "",
        user_role: string = "participant",
        language: string = "en",
        icon: string = None,
        tooltip: string = None,
        url: string = None,
        index: numbers = 0,
        proxy: bool = False,
    ):
        self.id = id
        self._type = _type
        self.icon = icon or defaultIcon(id, _type)
        self.tooltip = tooltip if tooltip else id
        self.index = index

        if proxy:
            self.url = f"{base_url}/proxy/{url}"
        else:
            self.url = url if url else defaultUrl(id, _type, user_role, language, base_url)

    def toJson(self):
        return {"id": self.id}


def defaultUrl(id: string, _type: string, user_role: string, language: string, base_url: string) -> string:
    if _type == "standard":
        return f"{base_url}/statics/hugo/{user_role}/{language}/{id}"
    return ""


def defaultIcon(id: string, _type: string) -> string:
    icon_map = {
        "standard": {"documentation": "clipboard-document-list", "exercises": "play-circle", "presentations": "presentation-chart-line"},
        "staticsite": {"mitre": "mitre", "drawio": "drawio"},
        "admin": "bookmark",
        "user": "user",
        "client": "tv",
    }

    if _type in icon_map:
        if isinstance(icon_map[_type], dict):
            return icon_map[_type].get(id, "globe-alt")
        else:
            return icon_map[_type]
    else:
        return "beaker"
