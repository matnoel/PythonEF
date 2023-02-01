import pandas as pd

import PostTraitement as PostTraitement
import Affichage as Affichage
import Folder
import numpy as np
import matplotlib.pyplot as plt
import TicTac as TicTac
import Simulations

# L'objectif du script est de récupérer pour chaque simulation la courbe force déplacement
# Didentifier 3 itérations de déplacement (18.5, 24.6, 30) µm 
# Pour ces 3 itérations tracer endommagement

Affichage.Clear()

test = True
loadSimu = True
plotDamage = True
savefig = False

# "PlateWithHole_Benchmark", "PlateWithHole_CompressionFCBA", "Shear_Benchmark", "Tension_Benchmark"
simulation = "PlateWithHole_Benchmark"

if simulation == "PlateWithHole_Benchmark":
    colorBarIsClose = True
else:
    colorBarIsClose = False

folder = Folder.New_File(simulation, results=True)

if test:
    folderSauvegarde = Folder.Join([folder, "Test", "_Post traitement"])
else:
    folderSauvegarde = Folder.Join([folder, "_Post traitement"])

if not savefig:
    folderSauvegarde=""

# ["Bourdin","Amor","Miehe","He","Stress"]
# ["AnisotStrain","AnisotMiehe_PM","AnisotMiehe_MP","AnisotMiehe_NoCross"]
# ["AnisotStress","AnisotStress_NoCross"]
# ["AnisotMiehe_PM","AnisotMiehe_MP"], ["AnisotMiehe_NoCross","AnisotStrain"]

# ["Miehe","AnisotStrain","AnisotMiehe_PM","AnisotMiehe_MP","AnisotMiehe_NoCross"]
# ["AnisotStrain","AnisotMiehe_PM","AnisotMiehe_MP","AnisotMiehe_NoCross","He"]
# ["AnisotStrain","Miehe"]
# ["AnisotStrain","He"]
# ["AnisotStrain", "He", "AnisotStress", "Stress"]

listComp = ["Elas_Isot"] # ["Elas_Isot", "Elas_IsotTrans", "Elas_Anisot"]

# listRegu = ["AT1", "AT2"] # ["AT1", "AT2"]
listRegu = ["AT2"] # ["AT1", "AT2"]

listSimpli2D = ["DP"] # ["CP","DP"]
listSolveur = ["History"]

# listSplit = ["Bourdin","Amor","Miehe","He","Stress","AnisotStrain","AnisotStress","Zhang"]
# listSplit = ["Bourdin","He","AnisotStrain","AnisotStress","Zhang"]
# listSplit = ["He","AnisotStrain","AnisotStress", "Zhang"]
listSplit = ["Bourdin"]

listOptimMesh=[True] # [True, False]

listTol = [1e-0] # [1e-0, 1e-1, 1e-2, 1e-3, 1e-4]

listnL = [0] # [100] [100, 120, 140, 180, 200]

listTheta = [0]
# listTheta = [-0, -10, -20, -30, -45, -60, -70, -80, -90]

# snapshot = [18.5, 24.6, 25, 28, 35]
snapshot = [24.6]

depMax = 80000 # µm 35 ou 80

# Génération des configurations
listConfig = []

for theta in listTheta:
    for comp in listComp:
        for split in listSplit:
            for regu in listRegu:
                for simpli2D in listSimpli2D:
                    for solveur in listSolveur:                                    
                        for tol in listTol:
                            for optimMesh in listOptimMesh:
                                for nL in listnL:
                                    listConfig.append([comp, regu, simpli2D, solveur, split, tol, optimMesh, nL, theta])

Nconfig = len(listConfig)

if simulation == "PlateWithHole_Benchmark":
    v=0.3
else:
    v=0

fig, ax = plt.subplots()

simulationsManquantes = []

for config in listConfig:

    comp = config[0]
    regu = config[1]
    simpli2D = config[2]
    solveur = config[3]
    split = config[4]
    tolConv = config[5]
    optimMesh = config[6]
    nL = config[7]
    theta = config[8]

    tic = TicTac.Tic()

    foldername = Folder.PhaseField_Folder(folder, comp=comp,  split=split, regu=regu, simpli2D=simpli2D, tolConv=tolConv, solveur=solveur, test=test, optimMesh=optimMesh, closeCrack=False, v=v, nL=nL, theta=theta)

    nomSimu = foldername.split(comp+'_')[-1]

    # Charge la force et le déplacement
    try:
        load, displacement = PostTraitement.Load_Load_Displacement(foldername, False)
    except AssertionError:
        if nomSimu not in simulationsManquantes: simulationsManquantes.append(nomSimu)
        print("données indisponibles")
        

    if loadSimu:
        # Charge la simulations
        try:
            simu = Simulations.Load_Simu(foldername, False)
            results = pd.DataFrame(simu._results)
            temps = results["tempsIter"].values.sum()
            temps_str, unite = TicTac.Tic.Get_temps_unite(temps)
            print(len(results),f"-> {temps_str:.3} {unite}")
        except AssertionError:
            if nomSimu not in simulationsManquantes: simulationsManquantes.append(nomSimu)
            print("simulation indisponible")
            

        # Affichage.Plot_Maillage(simu.mesh)

    if plotDamage:

        # titre = split.replace("AnisotStrain","Spectral")

        # Affiche le dernier endommagement
        Affichage.Plot_Result(simu, "damage", nodeValues=True, colorbarIsClose=colorBarIsClose,
        folder=folderSauvegarde, filename=f"{split} tol{tolConv} last", plotMesh=False,
        title=split)
        

        # Récupère les itérations à 18.5, 24.6, 30 et trace l'endommagement
        for dep in snapshot:
            try:
                i = np.where(displacement*1e6>=dep)[0][0]
            except:
                # i n'a pas été trouvé on continue les iterations
                continue
            
            simu.Update_iter(i)

            filenameDamage = f"{nomSimu} et ud = {np.round(displacement[i]*1e6,2)}"
            # titleDamage = filenameDamage

            titleDamage = split
            filenameDamage = f"PlateBench {comp}_{split}_{regu}_{simpli2D}"

            Affichage.Plot_Result(simu, "damage", nodeValues=True, colorbarIsClose=colorBarIsClose, folder=folderSauvegarde, filename=filenameDamage,title=titleDamage)

    # texte = nom.replace(f" pour v={v}", "")
    # texte = nomSimu
    texte = split

     
    # texte = texte.replace("AnisotStrain","Spectral")

    indexLim = np.where(displacement*1e6 <= depMax)[0]
    ax.plot(displacement[indexLim]*1e6, np.abs(load[indexLim]*1e-6), label=texte)

    tic.Tac("Post traitement", split, False)

    if loadSimu:
        try:
            resultats = simu._results
                
            resulats = pd.DataFrame(resulats)
            temps = resulats['tempsIter'].sum(axis=0)
            tempsCoef, unite = TicTac.Tic.Get_temps_unite(temps)
            print(f'{np.round(tempsCoef, 2)} {unite}')
        except:
            # Les informations n'ont pas été renseingées
            pass

ax.set_xlabel("displacement [µm]")
ax.set_ylabel("load [kN/mm]")
ax.grid()
ax.legend()
plt.figure(fig)
Affichage.Save_fig(folderSauvegarde, "load displacement")


print('\n Simulations manquantes :')
[print(simul) for simul in simulationsManquantes]

plt.show()
        


    