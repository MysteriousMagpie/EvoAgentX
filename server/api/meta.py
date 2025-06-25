from fastapi import APIRouter
import pkg_resources

router = APIRouter(tags=["meta"])


@router.get("/status")
def status() -> dict[str, str]:
    """Return basic service health information."""
    version = pkg_resources.get_distribution("evoagentx").version
    return {"status": "ok", "version": version}
