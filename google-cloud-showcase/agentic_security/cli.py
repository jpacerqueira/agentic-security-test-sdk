from __future__ import annotations

import typer
import uvicorn

app = typer.Typer(help="Macro-Search - Agentic Security Scan")


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8090):
    uvicorn.run("agentic_security.web.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()
