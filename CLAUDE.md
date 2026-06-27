# Custom End Table Design Project


## Description of the project

* A general outline of how I want the table is in `END_TABLE_SPECS.md`.
* When generating structural choices or calculations, optimize for stability and weight distribution.
* Don't make choices that only an expert woodworker could do.
* You have the following power tools at your disposal.
    * Tablesaw
    * Router
    * Miter Saw
* You have all the regular handtools at your disposal
* We are designing this in FreeCAD (version 1.1, installed at `C:\Program Files\FreeCAD 1.1`).
    * The headless runner is `C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe` — use it to run Python build scripts.
    * Build the model as parametric solids using the `Part` workbench so joinery (e.g. half-laps) can be made with boolean cuts.
    * Deliver a native `.FCStd` document. Mesh exports (STL/STEP) are optional extras.

## Project layout

* `docs/` — `END_TABLE_SPECS.md` (design brief / locked dimensions) and `plans.html` (printable build plans). Keep these in sync with the model.
* `scripts/` — `build_end_table.py` (parametric model), `preview_end_table.py` (CAD preview), `gemini_render.py` (photoreal render). All resolve paths relative to the project root via `Path(__file__).parents[1]`.
* `model/` — generated `end_table.FCStd` (model of record) + `end_table.stl`.
* `renders/` — generated preview/composite images.
* `reference/` — input assets (`chair.jpeg`).

## Build commands (run from project root)

* Model: `& "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" scripts\build_end_table.py` → writes `model/`.
* CAD preview: `python scripts\preview_end_table.py` → writes `renders/end_table_preview.png`.
* Photoreal render (only when asked): `python scripts\gemini_render.py` → writes `renders/table_with_chair_realistic.png`.

The single source of truth for dimensions is the parameter block at the top of `scripts/build_end_table.py`; after changing it, re-run the model + preview and update `docs/`.
