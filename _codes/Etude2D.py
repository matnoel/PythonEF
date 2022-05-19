# %%

from Geom import Domain, Point
import Dossier
import PostTraitement

from Materiau import Elas_Isot, Materiau
from Geom import *
from Interface_Gmsh import Interface_Gmsh
from Mesh import Mesh
from Simu import Simu
import Affichage


import numpy as np
import matplotlib.pyplot as plt

from TicTac import TicTac

Affichage.Clear()

ticTot = TicTac()

# Data --------------------------------------------------------------------------------------------

plotResult = True

saveParaview = True

dim = 2

# Paramètres géométrie
L = 120;  #mm
h = 13
b = 13

P = 800 #N
lineLoad = P/h #N/mm
surfLoad = P/h/b #N/mm2

# Paramètres maillage
taille = h/10

comportement = Elas_Isot(dim, epaisseur=b, useVoigtNotation=True)

# Materiau
materiau = Materiau(comportement)

# Construction du modele et du maillage --------------------------------------------------------------------------------
elemType = "TRI3" # ["TRI3", "TRI6", "QUAD4", "QUAD8"]

domain = Domain(Point(), Point(x=L, y=h))
Line0 = Line(Point(), Point(y=h))
LineL = Line(Point(x=L), Point(x=L, y=h))

interfaceGmsh = Interface_Gmsh()
mesh = interfaceGmsh.Rectangle(domain=domain, elemType=elemType, tailleElement=taille, isOrganised=True)

# Affichage.Plot_Maillage(mesh)
# plt.show()

# Récupère les noeuds qui m'interessent

noeuds_en_0 = mesh.Get_Nodes_Line(Line0)        # noeuds_en_0 = mesh.Get_Nodes_Conditions(conditionX=lambda x: x == 0)
noeuds_en_L = mesh.Get_Nodes_Line(LineL)        # noeuds_en_L = mesh.Get_Nodes_Conditions(conditionX=lambda x: x == L)

# ------------------------------------------------------------------------------------------------------
Affichage.NouvelleSection("Traitement")

simu = Simu(mesh, materiau)

# # Affichage etc
# fig, ax = Affichage.Plot_Maillage(simu, deformation=True)
# Affichage.Plot_NoeudsMaillage(simu, ax, noeuds_en_0, c='red')
# Affichage.Plot_NoeudsMaillage(simu, ax, noeuds_en_L, c='blue', showId=True)
# Affichage.Plot_Maillage(simu, deformation=True)
# Affichage.Plot_NoeudsMaillage(simu, showId=True)

# Renseigne les condtions limites

# Affichage.Plot_NoeudsMaillage(simu.mesh, showId=True)
# plt.show()

simu.add_dirichlet("displacement", noeuds_en_0, ["x","y"], [0, 0], description="Encastrement")

# simu.add_surfLoad("displacement",noeuds_en_L, ["y"], [surfLoad])
simu.add_lineLoad("displacement",noeuds_en_L, ["y"], [-lineLoad])

# Assemblage du système matricielle
simu.Assemblage_u()

dep = simu.Solve_u(resolution=2, useCholesky=False)

simu.Save()

# Post traitement --------------------------------------------------------------------------------------
Affichage.NouvelleSection("Post traitement")

simu.Resume()

folder = Dossier.NewFile("Etude2D", results=True)

if saveParaview:
        filename = Dossier.NewFile("Etude2D\\solution2D", results=True)
        PostTraitement.Save_Simulation_in_Paraview(folder, simu)

if plotResult:

        tic = TicTac()
        
        Affichage.Plot_Maillage(simu, deformation=True, folder=folder)
        Affichage.Plot_Result(simu, "dy", deformation=True, valeursAuxNoeuds=True)        
        Affichage.Plot_Result(simu, "Svm", deformation=True, valeursAuxNoeuds=True)        
        Affichage.Plot_Result(simu, "Svm", deformation=True, valeursAuxNoeuds=False, affichageMaillage=False, folder=folder)        
        
        tic.Tac("Post Traitement","Affichage des figures", plotResult)

ticTot.Tac("Temps script","Temps total", True)        

TicTac.getResume()        

if plotResult:
        plt.show()

# %%
