import json
import numbers
import string


class Tab:
    def __init__(
        self,
        id: string,
        _type: string,
        user_role: string = "participant",
        language: string = "en",
        icon: string = None,
        tooltip: string = None,
        url: string = None,
        index: numbers = 0,
    ):
        self.id = id
        self._type = _type
        self.icon = icon or defaultIcon(id, _type)
        self.tooltip = tooltip if tooltip else id
        self.url = url if url else defaultUrl(id, _type, user_role, language)
        self.index = index

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id}, icon={self.icon}, tooltip={self.tooltip}, _type={self._type}, url={self.url})"

    def toJson(self):
        return {"id": self.id}


def defaultUrl(id: string, _type: string, user_role: string, language: string) -> string:
    if _type == "standard":
        return f"http://localhost:5000/statics/hugo/{user_role}/{language}/{id}"


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
            return "mdi-alpha-m-box-outline"
        elif id == "drawio":
            return "mdi-graph-outline"
        else:
            return "globe-alt"
    elif _type == "admin":
        return "bookmark"
    elif _type == "client":
        return "tv"
    else:
        return "beaker"
