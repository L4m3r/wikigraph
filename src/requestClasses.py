class BaseRequest:
    def __init__(self, **kwargs) -> None:
        variables = self.get_parameters()
        for var, t in variables.items():
            try:
                if t == int:
                    setattr(self, var, int(kwargs[var]))
                else:
                    setattr(self, var, kwargs[var])
            except KeyError:  # TODO: add handling
                pass
            except ValueError:
                pass

        for var in variables:
            if getattr(self, var) is None:
                raise AttributeError(f"No such attribute: {var}")

    @classmethod
    def get_parameters(cls) -> dict[str, type]:
        return {**cls.get_optional_parameters(), **cls.get_required_parameters()}

    @classmethod
    def get_optional_parameters(cls) -> dict[str, type]:
        variables = [var for var in dir(cls)
                     if not callable(getattr(cls, var)) and
                     not var.startswith("__")]
        d = dict([(var, type(getattr(cls, var))) for var in variables])
        return d

    @classmethod
    def get_required_parameters(cls) -> dict[str, type]:
        return cls.__annotations__


class GraphRequest(BaseRequest):
    title: str
    depth = 2


class SearchRequest(BaseRequest):
    title: str
    limit = 10
