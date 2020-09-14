# xmas-oddballmatch

EEG processing pipeline for xmas-oddballmatch.

## Run via `make`
### Convert to BIDS
Run `make convert` to create a new BIDS directory. Raw file paths and target path must be specified in `configuration.yaml`.
### Proeprocessing
Run `make peprocess [sub=<subject id>]` to run preprocessing pipeline. Parameters must be specified in `configuration.yaml`.
### Generate reports
Run `make report [sub=<subject id>]` to create reports.