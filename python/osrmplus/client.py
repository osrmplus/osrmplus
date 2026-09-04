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
    """Format [(lng, lat), ...] as 'lng,lat;lng,lat' for OSRM GET endpoints."""
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

    # ── Routing (coordinates are (lng, lat) tuples) ──────────────

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

    # ── Matrix (coordinates are (lng, lat) tuples) ───────────────

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

    # ── Optimization (coordinates are [lat, lon]) ────────────────

    def vrp(
        self,
        coordinates: Sequence[Sequence[float]],
        *,
        num_vehicles: int = 1,
        depot: int = 0,
        demands: Sequence[int] | None = None,
        vehicle_capacities: Sequence[int] | None = None,
        time_windows: Sequence[Sequence[int]] | None = None,
        service_times: Sequence[int] | None = None,
        time_limit_seconds: int | None = None,
        objective: str | None = None,
        allow_dropping_visits: bool | None = None,
        drop_penalty: int | None = None,
        detailed_solution: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Solve a vehicle routing problem.

        Coordinates are [lat, lon] arrays. Index 0 is the depot unless you
        set ``depot`` to something else. Every per-node array (demands,
        time_windows, service_times) follows the same order as coordinates.

        Args:
            coordinates: List of [lat, lon] arrays.
            num_vehicles: Fleet size.
            depot: Index of the depot node (default 0).
            demands: Load demand at each stop. Requires vehicle_capacities.
            vehicle_capacities: Maximum capacity for each vehicle.
            time_windows: [[earliest, latest]] for each stop.
            service_times: Seconds spent at each stop.
            time_limit_seconds: How long the solver may search (default 30).
            objective: 'minimize_total_distance', 'minimize_longest_route',
                       'minimize_total_time', or 'minimize_vehicles_used'.
            allow_dropping_visits: Let the solver skip stops.
            drop_penalty: Cost of skipping a stop.
            detailed_solution: Include coordinates and arrival times.

        Returns:
            Parsed JSON with ``status``, ``routes``, ``total_distance``,
            ``dropped_nodes``, and ``statistics``.
        """
        body: dict[str, Any] = {
            "coordinates": [list(c) for c in coordinates],
            "num_vehicles": num_vehicles,
            "depot": depot,
            **params,
        }
        if demands is not None:
            body["demands"] = list(demands)
        if vehicle_capacities is not None:
            body["vehicle_capacities"] = list(vehicle_capacities)
        if time_windows is not None:
            body["time_windows"] = [list(tw) for tw in time_windows]
        if service_times is not None:
            body["service_times"] = list(service_times)
        if time_limit_seconds is not None:
            body["time_limit_seconds"] = time_limit_seconds
        if objective is not None:
            body["objective"] = objective
        if allow_dropping_visits is not None:
            body["allow_dropping_visits"] = allow_dropping_visits
        if drop_penalty is not None:
            body["drop_penalty"] = drop_penalty
        if detailed_solution is not None:
            body["detailed_solution"] = detailed_solution
        return self._post("/vrp", body)

    def tsp(
        self,
        coordinates: Sequence[Sequence[float]],
        *,
        depot: int = 0,
        time_limit_seconds: int | None = None,
        detailed_solution: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Find the shortest round trip through a set of stops.

        Coordinates are [lat, lon] arrays.

        Args:
            coordinates: List of [lat, lon] arrays.
            depot: Start and end node (default 0).
            time_limit_seconds: How long the solver may search.
            detailed_solution: Include coordinates in the response.
        """
        body: dict[str, Any] = {
            "coordinates": [list(c) for c in coordinates],
            "depot": depot,
            **params,
        }
        if time_limit_seconds is not None:
            body["time_limit_seconds"] = time_limit_seconds
        if detailed_solution is not None:
            body["detailed_solution"] = detailed_solution
        return self._post("/tsp", body)

    def optimize(
        self,
        coordinates: Sequence[Sequence[float]],
        *,
        time_limit_seconds: int | None = None,
        detailed_solution: bool | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Optimize a delivery round with sensible defaults.

        Like :meth:`vrp` but picks fleet size and search parameters
        automatically.

        Coordinates are [lat, lon] arrays.

        Args:
            coordinates: List of [lat, lon] arrays.
            time_limit_seconds: How long the solver may search.
            detailed_solution: Include coordinates in the response.
        """
        body: dict[str, Any] = {
            "coordinates": [list(c) for c in coordinates],
            **params,
        }
        if time_limit_seconds is not None:
            body["time_limit_seconds"] = time_limit_seconds
        if detailed_solution is not None:
            body["detailed_solution"] = detailed_solution
        return self._post("/optimize", body)
