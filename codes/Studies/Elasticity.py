# Import necessary libraries and modules
from enum import Enum
import matplotlib.pyplot as plt

from Interface_Gmsh import Interface_Gmsh, ElemType
from Geom import *
import Display
import Simulations
import Materials
import TicTac
import Folder

Display.Clear()

# ----------------------------------------------
# Configuration
# ----------------------------------------------
# Define dimension and mesh size parameters
dim = 2
N = 20 if dim == 2 else 10

# Create a folder to store simulation results
folder = Folder.New_File(f"Elasticity{dim}D", results=True)

# Define an enumeration class for different simulation types
class SimulationType(str, Enum):
    BEAM = "BEAM",
    EQUERRE = "EQUERRE",
    TEF2 = "TEF2"

# Set the simulation type to be used (one of CPEF, EQUERRE, or TEF2)
simulationType = SimulationType.EQUERRE

# Define material properties
coef = 1
E = 210000  # MPa (Young's modulus)
v = 0.3     # Poisson's ratio

# ----------------------------------------------
# Simulations
# ----------------------------------------------
# Create an instance of the Gmsh interface
interface = Interface_Gmsh()

# Start the simulation for different simulation types
if simulationType == SimulationType.BEAM:    
    dim = 3
    h = 1
    stpFile = Folder.Join([Folder.Get_Path(), "codes", "_parts", "beam.stp"])
    mesh = interface.Mesh_Import_part(stpFile, dim, 5)
    
    material = Materials.Elas_Isot(dim, E=E, v=v)
    simu = Simulations.Simu_Displacement(mesh, material)

    simu.add_dirichlet(mesh.Nodes_Conditions(lambda x, y, z: x == 0), [0, 0, 0], ['x', 'y', 'z'])
    simu.add_surfLoad(mesh.Nodes_Conditions(lambda x, y, z: x == 120), [800/13**2], ["y"])

elif simulationType == SimulationType.EQUERRE:
    L = 120  # mm (length)
    h = L*0.3

    # Define points and crack geometry for the mesh
    pt1 = Point(isOpen=True, r=-10)
    pt2 = Point(x=L)
    pt3 = Point(x=L, y=h)
    pt4 = Point(x=h, y=h, r=10)
    pt5 = Point(x=h, y=L)
    pt6 = Point(y=L)
    pt7 = Point(x=h, y=h)
    contour = PointsList([pt1, pt2, pt3, pt4, pt5, pt6], h/N)

    inclusions = [Circle(Point(x=h/2, y=h*(i + 1)), h/4, meshSize=h/N, isHollow=True) for i in range(3)]
    inclusions.extend([Domain(Point(x=h, y=h/2 - h*0.1), Point(x=h*2.1, y=h/2 + h*0.1), isHollow=False, meshSize=h/N)])

    if dim == 2:
        mesh = interface.Mesh_2D(contour, inclusions, ElemType.QUAD4)
    elif dim == 3:
        mesh = interface.Mesh_3D(contour, inclusions, extrude=[0, 0, -h], nLayers=4, elemType=ElemType.HEXA8)

    noeudsGauche = mesh.Nodes_Conditions(lambda x, y, z: x == 0)
    nodesRight = mesh.Nodes_Conditions(lambda x, y, z: x == L)

    material = Materials.Elas_Isot(dim, planeStress=True, thickness=h, E=E, v=v)
    simu = Simulations.Simu_Displacement(mesh, material)

    if dim == 2:
        simu.add_dirichlet(noeudsGauche, [0, 0], ["x", "y"])
        simu.add_lineLoad(nodesRight, [-800/h], ["y"])
    else:
        simu.add_dirichlet(noeudsGauche, [0, 0, 0], ["x", "y", "z"])
        simu.add_surfLoad(nodesRight, [-800/(h*h)], ["y"])

elif simulationType == SimulationType.TEF2:
    coef = 1e6
    E = 15000*coef  # Pa (Young's modulus)
    v = 0.25          # Poisson's ratio
    g = 9.81          # m/s^2 (acceleration due to gravity)

    h = 180  # m (thickness)

    pt1 = Point()
    pt2 = Point(x=h)
    pt3 = Point(y=h)
    contour = PointsList([pt1, pt2, pt3], h/N)

    ro = 2400  # kg/m^3 (density)
    w = 1000   # kg/m^3 (density)

    if dim == 2:
        mesh = interface.Mesh_2D(contour, [], ElemType.QUAD4)
    elif dim == 3:
        mesh = interface.Mesh_3D(contour, [], extrude=[0, 0, -2*h], nLayers=3, elemType=ElemType.HEXA8)

    noeudsBas = mesh.Nodes_Conditions(lambda x, y, z: y == 0)
    noeudsGauche = mesh.Nodes_Conditions(lambda x, y, z: x == 0)

    material = Materials.Elas_Isot(dim, planeStress=False, thickness=h, E=E, v=v)
    simu = Simulations.Simu_Displacement(mesh, material)

    if dim == 2:
        simu.add_dirichlet(noeudsBas, [0, 0], ["x", "y"])
    else:
        simu.add_dirichlet(noeudsBas, [0, 0, 0], ["x", "y", "z"])

    simu.add_volumeLoad(mesh.nodes, [-ro*g], ["y"], description="[-ro*g]")
    simu.add_surfLoad(noeudsGauche, [lambda x, y, z: w*g*(h - y)], ["x"], description="[w*g*(h-y)]")

simu.Solve()
simu.Save_Iter()

# ----------------------------------------------
# PostProcessing
# ----------------------------------------------
Display.Plot_Mesh(mesh, folder=folder)
Display.Plot_Model(mesh)
Display.Plot_BoundaryConditions(simu, folder)

print(simu)

Display.Plot_Result(simu, "Svm", nodeValues=True, coef=1/coef, nColors=20, folder=folder)

TicTac.Tic.Plot_History(details=False)

plt.show()