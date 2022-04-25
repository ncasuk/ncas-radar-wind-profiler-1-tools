ncas-radar-wind-profiler-1-tools
================================

This repo contains code for plotting data from ncas-radar-wind-profiler-1 netCDF files.

Requirements
------------

* python 3.7 or above
* python modules:
  * netCDF4
  * matplotlib
  * numpy
  * datetime

Installation
------------

To install, either clone the repo `git clone https://github.com/ncasuk/ncas-radar-wind-profiler-1-tools.git` or download and extract a release version.

Download the required modules using `conda install --file conda_requirements.txt` or `pip install -r requirements.txt`

Usage
-----

Navigate into the [ncas_radar_wind_profiler_1_plotting] directory and type  `python wind_profiler_plots.py`.

Within `wind_profiler_plots.py`, the following may need adjusting:
* `nc_file_path="/gws/..."`: replace file path with path to netCDF files
* `plots_path="/gws/..."`: replace file path with where to save plots

This script will make plots for both "high-mode" and "low-mode". If plots for only one mode are desired, comment out the other mode at the bottom of the file.

[ncas_radar_wind_profiler_1_plotting]: ncas_radar_wind_profiler_1_plotting
