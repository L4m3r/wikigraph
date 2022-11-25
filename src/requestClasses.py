class BaseRequest:
    def __init__(self, **kwargs) -> None:
        variables = [var for var in dir(self) if not var.startswith("__")]
        for var in variables:
            try:
                attr = getattr(self, var)
                if type(attr) == int:
                    setattr(self, var, int(kwargs[var]))
                else:
                    setattr(self, var, kwargs[var])
            except KeyError: # TODO: add handling
                pass
            except ValueError:
                pass

        for var in variables:
            if getattr(self, var) is None:
                raise AttributeError(f"No such attribute: {var}")

class GraphRequest(BaseRequest):
    title: str = None
    depth = 2

class SearchRequest(BaseRequest):
    title: str = None
    limit = 10
