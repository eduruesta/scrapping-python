from pydantic import BaseModel

class Team(BaseModel):
    """
    Represents the data structure of a Hockey Team in the standings.
    """

    _id: str
    Pos: str
    categoria: str
    Club: str
    Logo: str
    Pts: str
    PJ: str
    PG: str
    PE: str
    PP: str
    SP: str
    GF: str
    GC: str
    DG: str
    Bo: str
    Sa: str
