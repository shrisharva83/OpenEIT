## Code dependencies for offline.py

`offline.py` depends on the following Python modules and packages inside this repository

### `offline.py`

Main script for offline EIT reconstruction. It imports:

- `numpy` as `np`  
- `matplotlib.pyplot` as `plt`  
- `OpenEIT.dashboard`  
- `OpenEIT.reconstruction`

### `OpenEIT/dashboard/`

- Python package that provides dashboard-related helpers and configuration used by `offline.py` for plotting and data handling.  
- Only the Python code under `OpenEIT/dashboard` is required in this minimal repository; web assets and hardware backend services from the original project have been removed.[web:27]  

### `OpenEIT/reconstruction/` (including bundled `pyeit`)

Core EIT reconstruction code used by `offline.py`

- Mesh generation  
- Forward model and Jacobian computation  
- Reconstruction algorithms (GREIT, Gauss–Newton, back-projection)  
