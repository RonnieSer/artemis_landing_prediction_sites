# Private data

Place local research data in this directory when working on a trusted machine.
The repository intentionally ignores everything in `data/` except this file, so
remote-sensing rasters, geologic maps, and derived feature tables will not be
committed or pushed to GitHub.

Suggested local layout:

```text
data/
  raw/          # supplied LROC, LOLA, Mini-RF, and reference-map files
  interim/      # aligned, clipped, and cleaned rasters
  processed/    # feature tables and labels used by the models
```

Do not add credentials, NASA team-only files, or unpublished maps to the Git
repository. Keep a separate local inventory of filenames and checksums if the
lab workflow requires provenance tracking.