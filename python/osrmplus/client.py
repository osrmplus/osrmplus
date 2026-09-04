"""Thin HTTP client for the OSRMPlus API.

No dependencies beyond the standard library. Works with Python 3.9+.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Sequence

DEFAULT_BASE_URL = "https://api.osrmplus.com"


class APIError(Exception):
    """Raised when the API returns a non-2xx status code."""

    def __init__(self, status_code: int, code: str, message: str, body: Any = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.body = body
        super().__init__(f"{status_code} {code}: {message}")


def _coord_str(coordinates: Sequence[tuple[float, float]]) -> str:
    """Format [(lng, lat), ...] as 'lng,lat;lng,lat'."""
    return ";".join(f"{lng},{lat}" for lng, lat in coordinates)


class Client:
    """OSRMPlus API client.

    Args:
        api_key: Your API key from https://osrmplus.com/dashboard/cloud/keys.
        base_url: Override the default API URL.
        timeout: Request timeout in seconds (default 60).

    Example::

        from osrmplus import Client

        client = Client("opr_your_key_here")
        route = client.route([(74.3436, 31.5497), (74.2650, 31.4700)])
        print(route["routes"][0]["distance"])
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "User-Agent": "osrmplus-python/0.1.0",
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                url += "?" + urllib.parse.urlencode(filtered, doseq=True)
        req = urllib.request.Request(url, headers=self._headers())
        return self._send(req)

    def _post(self, path: str, body: dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode()
        headers = {**self._headers(), "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        return self._send(req)

    def _send(self, req: urllib.request.Request) -> Any:
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read())
                err = body.get("error", {})
                raise APIError(
                    status_code=e.code,
                    code=err.get("code", "unknown"),
                    message=err.get("message", e.reason),
                    body=body,
                ) from e
            except (json.JSONDecodeError, AttributeError):
                raise APIError(
                    status_code=e.code,
                    code="unknown",
                    message=str(e.reason),
                ) from e

    # ── Routing ──────────────────────────────────────────────────────

    def route(
        self,
        coordinates: Sequence[tuple[float, float]],
        *,
        alternatives: bool | None = None,
        steps: bool | None = None,
        overview: str | None = None,
        geometries: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Get a route between two or more points.

        Args:
            coordinates: List of (lng, lat) tuples.
            alternatives: Return alternative routes (default false).
            steps: Return turn-by-turn steps (default false).
            overview: Geometry detail: 'full', 'simplified', or 'false'.
            geometries: Geometry format: 'polyline' (default) or 'geojson'.

        Returns:
            Parsed JSON response with ``routes`` array.
        """
        path = f"/route/v1/driving/{_coord_str(coordinates)}"
        p: dict[str, Any] = {**params}
        if alternatives is not None:
            p["alternatives"] = str(alternatives).lower()
        if steps is not None:
            p["steps"] = str(steps).lower()
        if overview is not None:
            p["overview"] = overview
        if geometries is not None:
            p["geometries"] = geometries
        return self._get(path, p if p else None)

    def nearest(
        self,
        coordinate: tuple[float, float],
        *,
        number: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Snap a coordinate to the nearest road segment.

        Args:
            coordinate: A single (lng, lat) tuple.
            number: Number of nearest segments to return (default 1).
        """
        path = f"/nearest/v1/driving/{coordinate[0]},{coordinate[1]}"
        p: dict[str, Any] = {**params}
        if number is not None:
            p["number"] = number
        return self._get(path, p if p else None)

    def match(
        self,
        coordinates: Sequence[tuple[float, float]],
        **params: Any,
    ) -> dict[str, Any]:
        """Match GPS traces to the road network.

        Args:
            coordinates: List of (lng, lat) tuples from a GPS trace.
        """
        path = f"/match/v1/driving/{_coord_str(coordinates)}"
        return self._get(path, params if params else None)

    def trip(
        self,
        coordinates: Sequence[tuple[float, float]],
        **params: Any,
    ) -> dict[str, Any]:
        """Compute the fastest round trip through all points.

        Args:
            coordinates: List of (lng, lat) tuples.
        """
        path = f"/trip/v1/driving/{_coord_str(coordinates)}"
        return self._get(path, params if params else None)

    # ── Matrix ───────────────────────────────────────────────────────

    def matrix(
        self,
        coordinates: Sequence[tuple[float, float]],
        *,
        sources: Sequence[int] | None = None,
        destinations: Sequence[int] | None = None,
        annotations: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Compute a distance/duration matrix.

        Args:
            coordinates: List of (lng, lat) tuples.
            sources: Indices of source points (default all).
            destinations: Indices of destination points (default all).
            annotations: 'duration' (default), 'distance', or 'duration,distance'.

        Returns:
            Parsed JSON with ``durations`` and/or ``distances`` arrays.
        """
        path = f"/table/v1/driving/{_coord_str(coordinates)}"
        p: dict[str, Any] = {**params}
        if sources is not None:
            p["sources"] = ";".join(str(s) for s in sources)
        if destinations is not None:
            p["destinations"] = ";".join(str(d) for d in destinations)
        if annotations is not None:
            p["annotations"] = annotations
        return self._get(path, p if p else None)

    # ── Optimization ─────────────────────────────────────────────────

    def vrp(
        self,
        vehicles: list[dict[str, Any]],
        jobs: list[dict[str, Any]],
        **params: Any,
    ) -> dict[str, Any]:
        """Solve a vehicle routing problem.

        Args:
            vehicles: List of vehicle objects with at least ``id`` and ``start``.
            jobs: List of job objects with at least ``id`` and ``location``.

        Returns:
            Parsed JSON with ``routes`` and ``unassigned`` arrays.
        """
        return self._post("/vrp", {"vehicles": vehicles, "jobs": jobs, **params})

    def tsp(
        self,
        coordinates: Sequence[tuple[float, float]],
        **params: Any,
    ) -> dict[str, Any]:
        """Find the shortest round trip through a set of stops.

        Args:
            coordinates: List of (lng, lat) tuples.
        """
        return self._post(
            "/tsp",
            {"coordinates": [[lng, lat] for lng, lat in coordinates], **params},
        )

    def optimize(
        self,
        vehicles: list[dict[str, Any]],
        jobs: list[dict[str, Any]],
        **params: Any,
    ) -> dict[str, Any]:
        """Optimize a delivery round with sensible defaults.

        Like :meth:`vrp` but picks reasonable parameters automatically.

        Args:
            vehicles: List of vehicle objects.
            jobs: List of job objects.
        """
        return self._post(
            "/optimize", {"vehicles": vehicles, "jobs": jobs, **params}
        )
