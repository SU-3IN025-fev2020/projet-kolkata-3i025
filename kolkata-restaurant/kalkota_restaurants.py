# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
from astar import astar
import pygame
import glo
import random 
import numpy as np
import sys
import matplotlib.pyplot as plt

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
	global player,game
	# pathfindingWorld_MultiPlayer4
	name = _boardname if _boardname is not None else 'kolkata_6_10'
	game = Game('Cartes/' + name + '.json', SpriteBuilder)
	game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
	game.populate_sprite_names(game.O)
	game.fps = 5  # frames per second
	game.mainiteration()
	game.mask.allow_overlaping_players = True
	#player = game.player

# Retourne le restaurant le plus frequenté
def plus_frequent(frequentation ,  nb_restaus ):
	_max = 0
	res = 0
	for restau in range(nb_restaus):
		if _max < frequentation[restau]:
			res = restau
			_max = frequentation[restau]
	return res

# Retourne le restaurant le moins frequenté"""
def moins_frequent(frequentation ,  nb_restaus ):
	_min = 100000
	res = 0
	for restau in range(nb_restaus):
		if _min > frequentation[restau]:
			res = restau
			_min = frequentation[restau]
	return res



# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
# Choix du restaurant selon la strategie										       ---- 

# Random : choix aleatoire uniforme.    										       ---- 

# Tetue : choisit toujour le meme restaurant.										       ---- 

# Changeenperdant : choisit aleatoirement quand un restaurant est vide (il y'a que lui) , il choisit le meme a l'iteration suivante.

# Changeenperdant : choisit aleatoirement quand un restaurant n'est pas vide , il choisit le meme a l'iteration suivante.      ---- 

# plusfrequent : choisit le restaurant le plus frequenté aux iteration precedente					       ----

# moinsfrequent : choisit le restaurant le moins frequenté aux iteration precedente"""					       ----
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

def choix_restau(nbRestaus , strategy, preced, etaitseul , frequentation):
	if strategy == "random" or ( (strategy == "tetue"  )  and preced == -1) or (strategy == "changeenperdant" and etaitseul == False) or (strategy == "changeengagnant" and (etaitseul == True or preced == -1)):
		return random.randint(0,nbRestaus-1)
	if strategy == "tetue" or (strategy == "changeenperdant" and etaitseul == True) or (strategy == "changeengagnant" and etaitseul == False ) :
		return preced
	if strategy == "plusfrequent":
		return plus_frequent(frequentation , nbRestaus)
	if strategy == "moinsfrequent":
		return moins_frequent(frequentation , nbRestaus) 
    
def calcul_gain(nbRestaus , frequentation ,gain ):
	etaitseul =[False]* len(gain)
	for i in range(nbRestaus):
		if len(frequentation[i]) == 1:
			gain[frequentation[i][0]] += 1
			etaitseul[frequentation[i][0]] = True
		if len(frequentation[i]) > 1: 
			gain[random.choice(frequentation[i])] += 1

	return etaitseul 

def main(mode = ["random", "tetue"]):  #par defaut on compare les deux strategies de base
	#for arg in sys.argv:
	iterations = 5 # default
	if len(sys.argv) == 2:
		iterations = int(sys.argv[1])
	print ("Iterations: ")
	print (iterations)

	init()

	#-------------------------------
	# Initialisation
	#-------------------------------
	nbLignes = game.spriteBuilder.rowsize
	nbColonnes = game.spriteBuilder.colsize
	#print("lignes", nbLignes)
	#print("colonnes", nbColonnes)
        
    
	players = [o for o in game.layers['joueur']]
	nbPlayers = len(players)

	#choix des strategies
	strategies = [""]*nbPlayers
	for j in range (nbPlayers):
		strategies[j] = mode [j % len(mode)]
		#print ("strategies -- " , strategies)

	# on localise tous les états initiaux (loc du joueur)
	initStates = [o.get_rowcol() for o in game.layers['joueur']]
	#print ("Init states:", initStates)
        
    
	# on localise tous les objets  ramassables (les restaurants)
	goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
	#print ("Goal states:", goalStates)
	nbRestaus = len(goalStates)

	# on localise tous les murs
	wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
	#print ("Wall states:", wallStates)

	# on liste toutes les positions permises
	allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes) if not( (x,y) in wallStates or (x,y) in  goalStates)] 
	#print ("alloawed states:", allowedStates)
	paths = [[]]*nbPlayers
	restau=[-1]*nbPlayers
	frequentation = {i:{j:[] for j in range(nbRestaus)} for i in range(iterations)} #frequentaion a chaque iteration
	taux_freq = {j:0 for j in range(nbRestaus)}  #taux de frequentation aux iteration precedente
	gain = [0]*nbPlayers
	etaitseul = [False]*nbPlayers
	stats = {strategy:{"score" : 0 , "max" : 0, "produit": 1} for strategy in mode} 
	graph_score = {strategy: [0]*iterations for strategy in mode} #utilise pour dessiner le graphe des scores
	posPlayers = initStates
	for i in range(iterations):

		#-------------------------------
		# Placement aleatoire des joueurs, en évitant les obstacles
		#-------------------------------
        

		for j in range(nbPlayers):
			x,y = random.choice(allowedStates)
			players[j].set_rowcol(x,y)
			game.mainiteration()
			posPlayers[j]=(x,y)
			restau[j] = choix_restau(nbRestaus,strategies[j] ,restau[j],etaitseul[j],taux_freq) #choix des restaurants
			frequentation[i][restau[j]].append(j)
			paths[j] = astar(20, posPlayers[j], goalStates[restau[j]], wallStates)

		for res in taux_freq:
			taux_freq[res] = sum ([len (frequentation[k][res]) for k in range(iterations)])
		etaitseul = calcul_gain(nbRestaus,frequentation[i] , gain)
		for j in range(nbPlayers):
			graph_score[strategies[j]][i] += gain[j] 
        
		#Deplacement en Utilisant A*
		print('iteration -- ', i)
		for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
			row,col = posPlayers[j]
			for pos in paths[j]:
				next_row,next_col = pos
				players[j].set_rowcol(next_row,next_col)
				game.mainiteration()

	stats = {strategy:{"score" : 0 , "max" : 0, "produit": 1} for strategy in mode}  
	for j in range(nbPlayers):
		stats[strategies[j]]["score"] += gain[j] # la somme des gains de tt les joueurs utilisant une strategie
		stats[strategies[j]]["max"] = np.max([stats[strategies[j]]["max"],gain[j]]) # le gain max realisée par un joueur pour chaque 													strategie
		stats[strategies[j]]["produit"] *= gain[j] # le produit des gains de tt les joueurs utilisant une strategie
	print(stats)
	pygame.quit()
	

if __name__ == '__main__':
	main(["random" , "tetue"])
	main(["random" , "plusfrequent"])
	main(["random" , "moinsfrequent"])
	main(["random" , "changeenperdant"])
	main(["random" , "changeengagnant"])

	main(["tetue" , "plusfrequent"])
	main(["tetue" , "moinsfrequent"])
	main(["tetue" , "changeenperdant"])
	main(["tetue" , "changeengagnant"])

	main(["plusfrequent" , "changeenperdant"])
	main(["plusfrequent" , "changeengagnant"])
	main(["plusfrequent" , "moinsfrequent"])


	main(["moinsfrequent" , "changeenperdant"])
	main(["moinsfrequent" , "changeengagnant"])

	main(["changeenperdant" , "changeengagnant"])


	
