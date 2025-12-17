# Copilot / AI Agent Instructions

This project is a small VANET (vehicular ad-hoc network) simulation/orchestration stack. The goal of these instructions is to give an AI coding agent immediate, actionable context so edits, tests, and improvements are correct and safe.

- **Big Picture**: The system is organized as a protocol stack separated into folders: `application/`, `facilities/`, `transport_network/`, `data_link/`, `in_vehicle_network/`, and `rsu_legacy_systems/`. The runtime is threaded: `ITS_core.py` instantiates threads and inter-layer `Queue`s to pass Python `dict` messages between layers.

- **Entry point**: Run `ITS_core.py` with a `node_id` argument. Example:
  - `python ITS_core.py 1`
  - `ITS_core.py` builds threads (application, facilities, geonetwork, multicast, movement control) and uses the `ITS_maps` file to load node definitions.

- **Message format & flow**: Messages are plain Python `dict` objects with a `msg_type` key (examples: `'CA'`, `'DEN'`, `'SPAT'`, `'IVIM'`, `'BEACON'`). Typical flow:
  - Application -> Facilities (`ca_service_txd`, `den_service_txd`) -> Transport (`geonetwork_txd`) -> Link (`multicast_txd`).
  - Reception flows up the reverse path via queues created in `ITS_core.py`.

- **Key files to reference when editing behavior**:
  - Orchestration: `ITS_core.py` (thread and queue wiring).
  - Application: `application/obu_application.py`, `application/rsu_application.py`, `application/au_application.py`.
  - Facilities/services: `facilities/common_services.py`, `facilities/services.py` (message factories like `create_ca_message`).
  - Transport: `transport_network/geonetworking.py` (geocast/beacon handling).
  - Link layer: `data_link/multicast.py` (multicast socket I/O, physical-layer emulation).
  - Config / toggles: `application/app_config.py`, `ITS_options.py`, `ITS_maps.py`.

- **Patterns & conventions (project-specific)**:
  - Threads communicate exclusively via `Queue` objects created in `ITS_core.py`. Do not introduce global shared state without acquiring existing locks (e.g. `loc_table` guarded by `lock_loc_table`).
  - Messages are JSON-serializable dictionaries sent over UDP multicast in `multicast.py` — preserve the existing keys (`'msg_type'`, `'node'`, `'pos_x'`, `'pos_y'`, `'time'`, etc.).
  - Debugging is controlled by flags in `application/app_config.py` (e.g. `debug_sys`, `debug_multicast`). Prefer toggling those for verbose output rather than adding ad-hoc prints.
  - Network parameters (multicast group `224.0.0.0`, port `4260`, TTL) are defined in `data_link/multicast.py`. Changing them affects all nodes.

- **Runtime & test notes**:
  - This codebase uses threads and blocking `Queue.get()` calls; when running locally, start one node per terminal (different `node_id` values from `ITS_maps`).
  - The `ITS_options.py` file contains runtime models (e.g. `physical_model`, `geonetwork_model`, `forwarding_model`) used as feature flags. Flip those for targeted testing.
  - The multicast receiver binds to `('', 4260)` and joins `224.0.0.0`. On macOS you might need appropriate network permissions or run on an interface that supports multicast.

- **Safe editing guidance for AI agents**:
  - Preserve message-field names and semantics when changing serialization or queue-handling code.
  - If you modify threading/queue behavior, update `ITS_core.py` docstrings/comments to keep the orchestration consistent.
  - When changing network behavior in `multicast.py`, run at least two node instances to validate send/receive.
  - Prefer adding new feature toggles in `ITS_options.py` rather than sprinkling if/else across files.

- **Concrete examples**:
  - To add a new application message type `FOO`: add message factory in `facilities/services.py` (follow `create_ca_message`), ensure `application/*.py` enqueues it to the proper `*_service_txd_queue`, and add handling in `transport_network/geonetworking.py` and `data_link/multicast.py` if needed.
  - To enable physical-layer packet loss for tests: set `physical_model = True` in `ITS_options.py` and tune `range_scale` / `drop_threshold`.

- **Where to look for bugs**:
  - Thread startup ordering and `start_flag` usage in `ITS_core.py` — ensure tests wait for `start_flag` as threads expect.
  - JSON encoding/decoding in `multicast.py` — malformed dicts will raise exceptions at `json.loads` / `json.dumps`.
  - Cross-Python-version issues: some modules (e.g., `ITS_core.py`) import `Queue` (Python 2 style). Confirm interpreter version used by CI or runtime.

If anything in this summary is unclear or you want the agent to expand a particular section (examples, run checks, or add a small test harness), tell me which part and I will iterate.
