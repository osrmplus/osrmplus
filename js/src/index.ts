/**
 * OSRMPlus JavaScript/TypeScript client.
 *
 * Routing, distance matrices, and fleet optimization in one API.
 * No dependencies. Works in Node.js 18+ and modern browsers.
 *
 * @example
 * ```typescript
 * import { OSRMPlus } from "osrmplus";
 *
 * const client = new OSRMPlus("your_api_key");
 * const route = await client.route([[74.3436, 31.5497], [74.265, 31.47]]);
 * console.log(route.routes[0].distance);
 * ```
 *
 * @module
 */

const DEFAULT_BASE_URL = "https://api.osrmplus.com";

// ── Types ──────────────────────────────────────────────────────────

/** A coordinate pair: [longitude, latitude]. */
export type Coordinate = [number, number];

export interface RouteResponse {
  code: string;
  routes: Array<{
    distance: number;
    duration: number;
    geometry: string;
    legs: Array<Record<string, unknown>>;
  }>;
  waypoints?: Array<Record<string, unknown>>;
}

export interface MatrixResponse {
  code: string;
  durations?: number[][];
  distances?: number[][];
  sources?: Array<Record<string, unknown>>;
  destinations?: Array<Record<string, unknown>>;
}

export interface NearestResponse {
  code: string;
  waypoints: Array<{
    distance: number;
    location: Coordinate;
    name: string;
  }>;
}

export interface MatchResponse {
  code: string;
  matchings: Array<Record<string, unknown>>;
  tracepoints: Array<Record<string, unknown> | null>;
}

export interface TripResponse {
  code: string;
  trips: Array<Record<string, unknown>>;
  waypoints: Array<Record<string, unknown>>;
}

export interface Vehicle {
  id: number | string;
  start?: Coordinate;
  end?: Coordinate;
  capacity?: number[];
  time_window?: [number, number];
  [key: string]: unknown;
}

export interface Job {
  id: number | string;
  location: Coordinate;
  delivery?: number[];
  pickup?: number[];
  service?: number;
  priority?: number;
  time_windows?: Array<[number, number]>;
  [key: string]: unknown;
}

export interface OptimizationResponse {
  code: string;
  routes: Array<{
    vehicle: number | string;
    cost: number;
    steps: Array<{
      type: string;
      id?: number | string;
      location?: Coordinate;
      arrival?: number;
      [key: string]: unknown;
    }>;
    [key: string]: unknown;
  }>;
  unassigned: Array<{ id: number | string; [key: string]: unknown }>;
}

export interface MatrixParams {
  coordinates: Coordinate[];
  sources?: number[];
  destinations?: number[];
  annotations?: string;
  [key: string]: unknown;
}

export interface OptimizeParams {
  vehicles: Vehicle[];
  jobs: Job[];
  [key: string]: unknown;
}

export interface TSPParams {
  coordinates: Coordinate[];
  [key: string]: unknown;
}

export interface ClientOptions {
  baseUrl?: string;
  timeout?: number;
}

// ── Error ──────────────────────────────────────────────────────────

export class OSRMPlusError extends Error {
  statusCode: number;
  code: string;
  body?: unknown;

  constructor(statusCode: number, code: string, message: string, body?: unknown) {
    super(`${statusCode} ${code}: ${message}`);
    this.name = "OSRMPlusError";
    this.statusCode = statusCode;
    this.code = code;
    this.body = body;
  }
}

// ── Client ─────────────────────────────────────────────────────────

function coordStr(coordinates: Coordinate[]): string {
  return coordinates.map(([lng, lat]) => `${lng},${lat}`).join(";");
}

export class OSRMPlus {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;

  /**
   * Create an OSRMPlus client.
   *
   * @param apiKey - Your API key from https://osrmplus.com/dashboard/cloud/keys
   * @param options - Optional configuration
   *
   * @example
   * ```typescript
   * const client = new OSRMPlus("opr_your_key_here");
   * ```
   */
  constructor(apiKey: string, options: ClientOptions = {}) {
    this.apiKey = apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.timeout = options.timeout ?? 60_000;
  }

  private async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    let url = `${this.baseUrl}${path}`;
    if (params) {
      const filtered = Object.entries(params).filter(([, v]) => v != null);
      if (filtered.length) url += "?" + new URLSearchParams(filtered).toString();
    }
    return this.send<T>(url, { method: "GET" });
  }

  private async post<T>(path: string, body: Record<string, unknown>): Promise<T> {
    return this.send<T>(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  private async send<T>(url: string, init: RequestInit): Promise<T> {
    const headers = {
      "x-api-key": this.apiKey,
      "User-Agent": "osrmplus-js/0.1.0",
      ...(init.headers as Record<string, string> | undefined),
    };

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const resp = await fetch(url, { ...init, headers, signal: controller.signal });

      if (!resp.ok) {
        let body: unknown;
        try {
          body = await resp.json();
        } catch {
          throw new OSRMPlusError(resp.status, "unknown", resp.statusText);
        }
        const err = (body as Record<string, Record<string, string>>)?.error ?? {};
        throw new OSRMPlusError(
          resp.status,
          err.code ?? "unknown",
          err.message ?? resp.statusText,
          body,
        );
      }

      return (await resp.json()) as T;
    } finally {
      clearTimeout(timer);
    }
  }

  // ── Routing ────────────────────────────────────────────────────

  /**
   * Get a route between two or more points.
   *
   * @param coordinates - Array of [lng, lat] pairs.
   * @param params - Extra OSRM query parameters (alternatives, steps, overview, geometries).
   *
   * @example
   * ```typescript
   * const result = await client.route([[74.34, 31.55], [74.27, 31.47]]);
   * console.log(result.routes[0].distance);
   * ```
   */
  async route(
    coordinates: Coordinate[],
    params?: Record<string, string>,
  ): Promise<RouteResponse> {
    return this.get(`/route/v1/driving/${coordStr(coordinates)}`, params);
  }

  /**
   * Snap a coordinate to the nearest road segment.
   *
   * @param coordinate - A single [lng, lat] pair.
   * @param params - Extra params (e.g. number of results).
   */
  async nearest(
    coordinate: Coordinate,
    params?: Record<string, string>,
  ): Promise<NearestResponse> {
    return this.get(`/nearest/v1/driving/${coordinate[0]},${coordinate[1]}`, params);
  }

  /**
   * Match GPS traces to the road network.
   *
   * @param coordinates - Array of [lng, lat] pairs from a GPS trace.
   */
  async match(
    coordinates: Coordinate[],
    params?: Record<string, string>,
  ): Promise<MatchResponse> {
    return this.get(`/match/v1/driving/${coordStr(coordinates)}`, params);
  }

  /**
   * Compute the fastest round trip through all points.
   *
   * @param coordinates - Array of [lng, lat] pairs.
   */
  async trip(
    coordinates: Coordinate[],
    params?: Record<string, string>,
  ): Promise<TripResponse> {
    return this.get(`/trip/v1/driving/${coordStr(coordinates)}`, params);
  }

  // ── Matrix ─────────────────────────────────────────────────────

  /**
   * Compute a distance/duration matrix.
   *
   * @param params - Coordinates and optional source/destination indices.
   *
   * @example
   * ```typescript
   * const result = await client.matrix({
   *   coordinates: [[74.34, 31.55], [74.27, 31.47], [74.3, 31.5]],
   *   annotations: "duration,distance",
   * });
   * console.log(result.durations);
   * ```
   */
  async matrix(params: MatrixParams): Promise<MatrixResponse> {
    const { coordinates, sources, destinations, annotations, ...rest } = params;
    const qp: Record<string, string> = { ...rest as Record<string, string> };
    if (sources) qp.sources = sources.join(";");
    if (destinations) qp.destinations = destinations.join(";");
    if (annotations) qp.annotations = annotations;
    return this.get(`/table/v1/driving/${coordStr(coordinates)}`, qp);
  }

  // ── Optimization ───────────────────────────────────────────────

  /**
   * Solve a vehicle routing problem.
   *
   * @param params - Vehicles, jobs, and optional constraints.
   *
   * @example
   * ```typescript
   * const result = await client.vrp({
   *   vehicles: [{ id: 1, start: [74.34, 31.55], capacity: [20] }],
   *   jobs: [{ id: 1, location: [74.27, 31.47], delivery: [5] }],
   * });
   * ```
   */
  async vrp(params: OptimizeParams): Promise<OptimizationResponse> {
    return this.post("/vrp", params);
  }

  /**
   * Find the shortest round trip through a set of stops.
   */
  async tsp(params: TSPParams): Promise<OptimizationResponse> {
    return this.post("/tsp", params);
  }

  /**
   * Optimize a delivery round with sensible defaults.
   * Like vrp() but picks reasonable parameters automatically.
   */
  async optimize(params: OptimizeParams): Promise<OptimizationResponse> {
    return this.post("/optimize", params);
  }
}
