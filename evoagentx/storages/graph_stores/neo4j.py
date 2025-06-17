from .base import GraphStoreBase


class Neo4jGraphStore(GraphStoreBase):
    """Simple Neo4j graph store stub used for testing."""

    def __init__(self, uri: str = "", user: str = "", password: str = "", **kwargs):
        super().__init__(uri=uri, user=user, password=password, **kwargs)
        self.uri = uri
        self.user = user
        self.password = password
