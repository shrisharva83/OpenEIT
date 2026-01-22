## Dependencies for offline.py

offline.py depends on the following Python modules and packages inside this repository

Main script for offline EIT reconstruction. It imports:
- from __future__ import division, absolute_import, print_function
- numpy as np  
- matplotlib.pyplot as plt  
- OpenEIT.dashboard  
- OpenEIT.reconstruction

### OpenEIT/dashboard/

- Python package that provides dashboard-related helpers and configuration used by offline.py for plotting and data handling.  

### OpenEIT/reconstruction/

 EIT reconstruction code used by offline.py

- Mesh generation  
- Forward model and Jacobian computation  
- Reconstruction algorithms (GREIT, Gauss–Newton, back-projection)  

### step 1 creating a virtual environment and activating it in the exact folder where offline.py is present
python -m venv envtest
.\envtest\Scripts\Activate.ps1
### step 2 installing all necessary libraries
pip install numpy matplotlib dash dash-html-components dash-core-components dash-table

### step 3 run the offline.py file
python offline.py
