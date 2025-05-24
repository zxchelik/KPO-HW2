from typing import Annotated

from sqlalchemy import String

String64 = Annotated[str, String(64)]
