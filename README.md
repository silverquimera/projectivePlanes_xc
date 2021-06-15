# projectivePlanes_xc
 
 Tools for building the fractional rectangle covering LP for the incidence graphs of projective planes. This code was used to obtain a rectangle cover bound for the stable set polytope of the projective plane of order q=4. 

## Requierements
 Make sure you have SageMath/9.2 installed. Next, in your `sage` shell use the `requirements.txt` file to load the rest of the packages needed via: 
 ```python
    pip install -r requirements.txt
 ```

## Usage
 First, it is necessary to compute the orbits of the variables and constraints. These orbits are then stored in a file via the command:

 ```python
    sage initFile.py
 ```

 Then, you can generate an .lp file of fractional rectangle covering lp via

 ```python
    sage recFracLP.py
 ```
 Finally, load the .lp into your favorite LP solver.