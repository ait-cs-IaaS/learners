import json
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

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id}, icon={self.icon}, tooltip={self.tooltip}, _type={self._type}, url={self.url})"

    def toJson(self):
        return {"id": self.id}


def defaultUrl(id: string, _type: string, user_role: string, language: string, base_url: string) -> string:
    if _type == "standard":
        return f"{base_url}/statics/hugo/{user_role}/{language}/{id}"


def defaultIcon(id: string, _type: string) -> string:
    if _type == "standard":
        if id == "documentation":
            return "clipboard-document-list"
        elif id == "exercises":
            return "play-circle"
        elif id == "presentations":
            return "presentation-chart-line"
    elif _type == "staticsite":
        if id == "mitre":
            return "mitre"
        elif id == "drawio":
            return "drawio"
        else:
            return "globe-alt"
    elif _type == "admin":
        return "bookmark"
    elif _type == "user":
        return "user"
    elif _type == "client":
        return "tv"
    else:
        return "beaker"
