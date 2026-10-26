# MeitavAlternateView
[![MeitavAlternateView Docker Image CI](https://github.com/Nicokalak/MeitavAlternateView/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Nicokalak/MeitavAlternateView/actions/workflows/docker-image.yml)

## About The Project
This project provides alternative view for your Meitav Dash portfolio.

## Getting Started
You will need to generate excel web query for your portfolio.

1. go to your account and click excel web query

![Excel Web Query](images/excel.png)

2. open the file in text editor (e.g. Notepade++) and copy the linnk

![Get the Link](images/link.png)

3. run as docker container

```shell
  docker run -d -v <path_to_conf>:/app/config.json -e TZ='Asia/Jerusalem' -e portfolio_link='<your link>' -p 8080:8080 nicolak/meitav-alternate-view:latest 
  ```

4. open the app in browser http://localhost:8080/

## Running locally (without Docker)

1. Install dependencies:
```shell
uv sync
```

2. Set required environment variables:
```shell
export portfolio_link='<your link>'
export TZ='Asia/Jerusalem'
# optional: path to your config file
export config_path='<path_to_conf>/config.json'
```

3. Run the app:
```shell
uv run meitav_view
```

4. Open the app in browser http://localhost:8080/

## Building the UI

The UI (Vue 3 + Vite) builds straight into `src/meitav_view/static/`, which the backend serves:

```shell
cd ui
npm ci --ignore-scripts
npm run build      # production bundle -> ../src/meitav_view/static
npm run dev        # Vite dev server on :5173, proxying API calls to :8080
npm run typecheck
npm test
```

Python tests do not need a UI build.

## Running with Docker from source

```shell
mkdir -p .secrets && printf '%s' '<your link>' > .secrets/portfolio_url
./run.sh               # add --rebuild to ignore the build cache
```

The link is mounted into the container as a read-only secret file and read through
`MEITAV_PORTFOLIO_URL_FILE`; it is never placed in the environment. Optional non-secret
settings (see `.env.example`) are picked up from a local `.env` if present.

The image, wheel and UI all take their version from the git tag; `GET /version` returns it.

## Quality checks
run with uv
```shell

uv run ruff check src --fix
uv run ruff format src
uv run mypy src
uv run pytest
```

## License
Distributed under the ISC License.
