from TicTac import Tic
import Materials
from Geom import *
import Display
import Interface_Gmsh
import Simulations
import Folder

import matplotlib.pyplot as plt

Display.Clear()

# L'objectif de ce script est de voir l'influence du chamgement de taille du probleme

# Il peut etre interessant de faire varier le domaine la taille et la position du trou

# Options
comp = "Elas_Isot"
split = "Miehe" # ["Bourdin","Amor","Miehe","Stress"]
regu = "AT1" # "AT1", "AT2"
contraintesPlanes = True

nom="_".join([comp, split, regu])

nomDossier = "PlateWithHole_Dimension"

folder = Folder.New_File(nomDossier, results=True)

# Data
coef = 1e-3

L=15*coef
H=30*coef
h=H/2
ep=1*coef
diam=6*coef
r=diam/2

E=12e9
v=0.2
SIG = 10 #Pa

gc = 1.4
l_0 = 0.12 *coef*1.5

# Création du maillage
clD = l_0*5
clC = l_0

list_SxxA = []
list_SyyA = []
list_SxyA = []
list_SxxB = []
list_SyyB = []
list_SxyB = []

param_name='H'
param1 = H
param2 = L
list_cc = np.linspace(1/2,5,30)

for cc in list_cc:

    H = param1*cc
    # L = param2*cc
    h=H/2
    print(cc)
    point = Point()
    domain = Domain(point, Point(x=L, y=H), clD)
    circle = Circle(Point(x=L/2, y=H-h), diam, clC)

    interfaceGmsh = Interface_Gmsh.Interface_Gmsh(affichageGmsh=False, verbosity=False)
    mesh = interfaceGmsh.Mesh_2D(domain, [circle], "TRI3")

    # Display.Plot_Maillage(mesh)

    # Récupérations des noeuds de chargement
    B_lower = Line(point,Point(x=L))
    B_upper = Line(Point(y=H),Point(x=L, y=H))
    nodes0 = mesh.Nodes_Line(B_lower)
    nodesh = mesh.Nodes_Line(B_upper)
    node00 = mesh.Nodes_Point(Point())   

    # Noeuds en A et en B
    nodeA = mesh.Nodes_Point(Point(x=L/2, y=H-h+diam/2))
    nodeB = mesh.Nodes_Point(Point(x=L/2+diam/2, y=H-h))

    comportement = Materials.Elas_Isot(2, E=E, v=v, planeStress=True, thickness=ep)
    phaseFieldModel = Materials.PhaseField_Model(comportement, split, regu, gc, l_0)

    simu = Simulations.Simu_PhaseField(mesh, phaseFieldModel, verbosity=False)

    simu.add_dirichlet(nodes0, [0], ["y"])
    simu.add_dirichlet(node00, [0], ["x"])
    simu.add_surfLoad(nodesh, [-SIG], ["y"])

    # Display.Plot_BoundaryConditions(simu)

    simu.Solve()

    list_SxxA.append(simu.Get_Result("Sxx", True)[nodeA])
    list_SyyA.append(simu.Get_Result("Syy", True)[nodeA])
    list_SxyA.append(simu.Get_Result("Sxy", True)[nodeA])

    list_SxxB.append(simu.Get_Result("Sxx", True)[nodeB])
    list_SyyB.append(simu.Get_Result("Syy", True)[nodeB])
    list_SxyB.append(simu.Get_Result("Sxy", True)[nodeB])

Display.Section("Résultats")

Display.Plot_Mesh(mesh,folder=folder, title=f"mesh_{param_name}")
Display.Plot_Result(simu, "Sxx", nodeValues=True, coef=1/SIG, title=r"$\sigma_{xx}/\sigma$", folder=folder, filename='Sxx')
Display.Plot_Result(simu, "Syy", nodeValues=True, coef=1/SIG, title=r"$\sigma_{yy}/\sigma$", folder=folder, filename='Syy')
Display.Plot_Result(simu, "Sxy", nodeValues=True, coef=1/SIG, title=r"$\sigma_{xy}/\sigma$", folder=folder, filename='Sxy')

fig, ax = plt.subplots()

ax.plot(list_cc, np.array(list_SxxA)/SIG,label='SxxA/SIG')
ax.plot(list_cc, np.array(list_SxyA)/SIG,label='SxyA/SIG')
ax.plot(list_cc, np.array(list_SyyA)/SIG,label='SyyA/SIG')
ax.plot(list_cc, np.array(list_SxxB)/SIG,label='SxxB/SIG')
ax.plot(list_cc, np.array(list_SxyB)/SIG,label='SxyB/SIG')
ax.plot(list_cc, np.array(list_SyyB)/SIG,label='SyyB/SIG')
ax.grid()
plt.legend()
ax.set_title(param_name)
ax.set_xlabel('coef')

Display.Save_fig(folder, param_name)

Tic.Resume()

plt.show()





