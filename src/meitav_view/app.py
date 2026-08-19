import argparse
import importlib.metadata
import logging
import os
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from meitav_view.model.stock import Stock
from meitav_view.utils import auth_utils
from meitav_view.utils.auth_utils import require_authentication
from meitav_view.viewer import MeitavViewer

logger: logging.Logger = logging.getLogger("uvicorn")
viewer: MeitavViewer = MeitavViewer()

STATIC_DIR = Path(__file__).resolve().parent / "static"


def get_version() -> str:
    """Safely retrieves the distribution version."""
    try:
        return importlib.metadata.version("meitav-view")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0.dev0"


app = FastAPI(title="Meitav View", version=get_version())

_URL_PREFIX: str = os.getenv("URL_PREFIX", "")


@app.middleware("http")
async def strip_url_prefix(request: Request, call_next: Any) -> Response:
    """Strip URL_PREFIX from the request path so routes stay prefix-agnostic."""
    if _URL_PREFIX and request.url.path.startswith(_URL_PREFIX):
        request.scope["path"] = request.url.path[len(_URL_PREFIX) :] or "/"
    return await call_next(request)


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    if (STATIC_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")
    if (STATIC_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
    if (STATIC_DIR / "webfonts").exists():
        app.mount("/webfonts", StaticFiles(directory=STATIC_DIR / "webfonts"), name="webfonts")
    if (STATIC_DIR / "favicon").exists():
        app.mount("/favicon", StaticFiles(directory=STATIC_DIR / "favicon"), name="favicon")


@app.get("/trends")
def get_trends(_auth: str | None = Depends(require_authentication)) -> dict[str, Any]:
    return viewer.get_trends()


@app.get("/marketState")
def get_market_state(_auth: str | None = Depends(require_authentication)) -> dict[str, Any]:
    try:
        return viewer.get_market_state()
    except RuntimeError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@app.get("/portfolio")
def get_enriched_portfolio(
    request: Request,
    _auth: str | None = Depends(require_authentication),
) -> list[Stock]:
    logger.info(
        "request for portfolio from: %s %s",
        request.headers.get("x-real-ip"),
        request.headers.get("user-agent"),
    )
    logger.debug(
        "Request - Method: %s, Path: %s, Query Parameters: %s, Headers: %s",
        request.method,
        request.url.path,
        request.query_params,
        request.headers,
    )

    try:
        return viewer.enrich_portfolio()
    except ConnectionError as err:
        logger.exception("Connection error while getting enriched portfolio")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connection error",
        ) from err


@app.get("/ticker/{name}")
def ticker_data(name: str, _auth: str | None = Depends(require_authentication)) -> dict[str, Any]:
    return {
        "stock": viewer.find_stock(name),
        "market-state-4calc": viewer.get_current_market_state_key(),
    }


@app.get("/", response_class=FileResponse)
def root(
    request: Request,
    x_email: str | None = Header(default=None, alias="X-Email"),
) -> FileResponse:
    target_file = (
        STATIC_DIR / "index.html"
        if auth_utils.is_authenticated(x_email=x_email, request=request)
        else STATIC_DIR / "401.html"
    )
    if not target_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{target_file.name}' not found",
        )
    return FileResponse(target_file)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/watchList")
def get_watchlist() -> list[str]:
    return list(viewer.watchlist)


@app.post("/watchList")
def update_watchlist(new_watchlist: list[str]) -> dict[str, str]:
    viewer.config.set_and_save("watch_list", new_watchlist)
    return {"message": "Watchlist updated successfully"}


def setup_logging(level_name: str) -> None:
    """Configures system-wide structured logging."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=level,
    )


def main() -> None:
    # 1. Define CLI arguments with environment variable fallbacks
    parser = argparse.ArgumentParser(description="Production server entry point for the meitav-view application.")

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show the application version and exit.",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=int(os.getenv("APP_PORT", "8080")),
        help="Port to bind the server to (default: 8080 or $APP_PORT).",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("APP_LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set execution logging severity (default: INFO or $APP_LOG_LEVEL).",
    )

    # 2. Parse arguments (handles --version and --help immediately)
    args = parser.parse_args()

    # 3. Configure logging infrastructure
    setup_logging(args.log_level)

    logger.info("Starting meitav-view app version %s", get_version())

    # 4. Spin up the application server
    uvicorn.run(
        "meitav_view.app:app",
        host="0.0.0.0",  # noqa: S104
        port=args.port,
        log_level=args.log_level.lower(),
        workers=2,
    )


if __name__ == "__main__":
    main()
