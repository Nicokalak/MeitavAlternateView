import argparse
import http
import importlib.metadata
import logging
import os
import sys
from http import HTTPStatus
from typing import Any

from flask import Flask, Response, abort, jsonify, request, send_from_directory
from waitress import serve

from meitav_view.model.stock import Stock
from meitav_view.utils import auth_utils
from meitav_view.utils.auth_utils import require_authentication
from meitav_view.viewer import MeitavViewer

logger: logging.Logger = logging.getLogger("waitress")
viewer: MeitavViewer = MeitavViewer()


app = Flask(__name__, static_url_path="/static/")


@app.route("/trends")
@require_authentication
def get_trends() -> dict[str, Any]:
    return viewer.get_trends()


@app.route("/marketState")
@require_authentication
def get_market_state() -> dict[str, Any]:
    try:
        return viewer.get_market_state()
    except RuntimeError:
        abort(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)


@app.route("/portfolio")
@require_authentication
def get_enriched_portfolio() -> list[Stock]:
    logger.info(
        "request for portfolio from: {} {}".format(
            request.headers.get("X-Real-Ip"),
            request.headers.get("User-Agent"),
        ),
    )
    logger.debug(
        f"Request - Method: {request.method}, Path: {request.path}, "
        f"Query Parameters: {request.args}, Data: {request.data.decode()}, "
        f"Headers: {request.headers}",
    )

    try:
        return viewer.enrich_portfolio()
    except ConnectionError:
        logger.exception("Connection error while getting enriched portfolio")
        abort(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)


@app.route("/ticker/<name>")
@require_authentication
def ticker_data(name: str) -> dict[str, Any]:
    return {
        "stock": viewer.find_stock(name),
        "market-state-4calc": viewer.get_current_market_state_key(),
    }


@app.route("/js/<path:path>")
def send_js(path: str) -> Response:
    return send_from_directory("static/js", path)


@app.route("/css/<path:path>")
def send_css(path: str) -> Response:
    return send_from_directory("static/css", path)


@app.route("/webfonts/<path:path>")
def send_webfonts(path: str) -> Response:
    return send_from_directory("static/webfonts", path)


@app.route("/favicon/<path:icon>")
def favicon(icon: str) -> Response:
    if icon == "site.webmanifest":
        return send_from_directory("static/favicon", icon)
    return send_from_directory("static/favicon", icon, mimetype="image/x-icon")


@app.route("/")
def root() -> Response:
    if auth_utils.is_authenticated():
        return app.send_static_file("index.html")
    return app.send_static_file("401.html")


@app.route("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.route("/watchList", methods=["GET"])
def get_watchlist() -> list[str]:
    return list(viewer.watchlist)


@app.route("/watchList", methods=["POST"])
def update_watchlist() -> tuple[Response, int]:
    new_watchlist = request.json
    if not isinstance(new_watchlist, list):
        logger.error("invalid request for update_watchlist")
        return jsonify({"error": "'watchlist' should be a list"}), HTTPStatus.BAD_REQUEST

    viewer.config.set_and_save("watch_list", new_watchlist)

    return jsonify({"message": "Watchlist updated successfully"}), HTTPStatus.OK


def get_version() -> str:
    """Safely retrieves the distribution version."""
    try:
        return importlib.metadata.version("meitav-view")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0.dev0"


def setup_logging(level_name: str) -> None:
    """Configures system-wide structured logging."""
    # Convert string config to logging integer level (fallback to INFO)
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
        "--prefix",
        type=str,
        default=os.getenv("URL_PREFIX", ""),
        help="URL prefix for the application routes (default: $URL_PREFIX).",
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
    serve(
        app,
        listen=f"*:{args.port}",
        url_prefix=args.prefix,
        threads=2,
    )


if __name__ == "__main__":
    main()
