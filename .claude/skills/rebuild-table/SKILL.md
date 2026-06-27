---
name: rebuild-table
description: Rebuild the cherry end-table FreeCAD model and regenerate its preview after any change to scripts/build_end_table.py. Use whenever a table dimension/parameter changes, or when asked to rebuild, regenerate, validate, or preview the model.
---

# Rebuild the end table

Run this after editing the parameter block at the top of
`scripts/build_end_table.py`. All commands run from the project root.

## Steps

1. **Build the model + mesh:**
   ```
   & "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" scripts\build_end_table.py
   ```
   Confirm it prints `Saved: ...\model\end_table.FCStd` and an
   `Overall (in): L=.. W=.. H=..` line. Sanity-check those dims against the
   change you just made.

2. **Validate the solids are watertight** (recommended after structural edits):
   ```
   & "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" -c "import FreeCAD,Part; d=FreeCAD.openDocument(r'model\end_table.FCStd'); [print(o.Name,'valid='+str(o.Shape.isValid()),'solids='+str(len(o.Shape.Solids))) for o in d.Objects]"
   ```
   Every part should report `valid=True solids=1`.

3. **Regenerate the preview and look at it:**
   ```
   python scripts\preview_end_table.py
   ```
   Writes `renders\end_table_preview.png`; open/Read it to eyeball the change.

## After a geometry change, also

- Update the affected numbers in `docs/END_TABLE_SPECS.md` and the
  `docs/plans.html` cut list / dimensions / stability notes so the docs match
  the model (the parameter block in `build_end_table.py` is the source of truth).
- Commit the model + scripts + docs. Regenerable outputs (`.stl`, preview PNG)
  are gitignored on purpose.
- Re-run the photoreal chair render (`scripts/gemini_render.py`, needs
  `GEMINI_API_KEY`) **only when asked** — it costs an API call.

## Notes

- IDE "cannot find module FreeCAD / Part" errors are false positives: those
  modules exist only inside FreeCAD's bundled interpreter, not standalone Python.
- `freecadcmd` may return a non-zero exit code when its stdout pipe is truncated
  (e.g. piped through `Select-Object`); that is harmless if it printed `Saved:`.
