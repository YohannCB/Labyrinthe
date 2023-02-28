from random import randint
import pygame
from pygame.locals import *
import sys


class Case:
	def __init__(self):
		self.murs = {"H": True, "B": True, "G": True, "D": True}
		self.visitee = False

	def draw(self, window, i, j, s):
		col = (196, 196, 196)
		x = 20 + s * i
		y = 20 + s * j
		if self.murs["H"]:
			pygame.draw.line(window, col, (x, y), (x + s, y))
		if self.murs["B"]:
			pygame.draw.line(window, col, (x, y + s), (x + s, y + s))
		if self.murs["G"]:
			pygame.draw.line(window, col, (x, y), (x, y + s))
		if self.murs["D"]:
			pygame.draw.line(window, col, (x + s, y), (x + s, y + s))
		if self.visitee:
			self.affiche_cercle(window, (96, 96, 96), i, j)

	def affiche_cercle(self, window, col, i, j, s):
		x = 20 + s * i
		y = 20 + s * j
		r = pygame.Rect(x + 2, y + 2, s - 4, s - 4)
		pygame.draw.circle(window, col, (x + s // 2, y + s // 2), s // 5)


class Labyrinthe:
	def __init__(self, largeur, hauteur, cote):
		self.largeur = largeur
		self.hauteur = hauteur
		self.cote = cote  # pour l'affichage
		self.cases = [[Case() for _ in range(hauteur)] for _ in range(largeur)]

		# Ajuste la taille de la pile d'exécution
		sys.setrecursionlimit(max(largeur * hauteur, 100000))

		i = randint(0, largeur - 1)
		j = randint(0, hauteur - 1)

		# initialisation du labyrinthe
		passages = self._generation(i, j)

		for i, j, vi, vj in passages:
			c = self.cases[i][j]
			v = self.cases[vi][vj]
			if i == vi:
				if vj == j + 1:
					c.murs["B"] = False
					v.murs["H"] = False
				else:
					c.murs["H"] = False
					v.murs["B"] = False
			if j == vj:
				if vi == i + 1:
					c.murs["D"] = False
					v.murs["G"] = False
				else:
					c.murs["G"] = False
					v.murs["D"] = False

		# initialisation des cases
		for i in range(largeur):
			for j in range(hauteur):
				self.cases[i][j].visitee = False

	def est_valide(self, i, j):
		""" renvoie True ssi i et j sont des indices valides """
		return 0 <= i < self.largeur and 0 <= j < self.hauteur

	def _voisine(self, i, j):
		voisines = []
		for di, dj in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
			vi, vj = i + di, j + dj
			if self.est_valide(vi, vj) and not self.cases[vi][vj].visitee:
				voisines.append((i + di, j + dj))
		if voisines == []:
			return
		idx = randint(0, len(voisines) - 1)
		return voisines[idx]

	def _generation(self, i, j, passages=[]):
		c = self.cases[i][j]
		c.visitee = True

		v = self._voisine(i, j)
		while v is not None:
			vi, vj = v
			passages.append((i, j, vi, vj))
			self._generation(vi, vj, passages)
			v = self._voisine(i, j)
		return passages

	def affiche(self, window):
		larg = self.largeur
		haut = self.hauteur
		for j in range(haut):
			for i in range(larg):
				c = self.cases[i][j]
				c.draw(window, i, j, self.cote)

	def affiche_cercle(self, window, col, i, j):
		c = self.cases[i][j]
		c.affiche_cercle(window, col, i, j, self.cote)

	def case_voisine(self, i, j):
		if self.est_valide(i, j):
			return self.cases[i][j]
		return None


class Main:
	def __init__(self, labyrinthe, solver):
		self.labyrinthe = labyrinthe
		self.solver = solver

		# initialisation de pygame
		pygame.init()
		self.window = pygame.display.set_mode((800, 600))
		self.clock = pygame.time.Clock()

		# maintien de la fenÃªtre
		self.hold()

	def affiche(self):
		self.window.fill((0, 0, 0))
		self.labyrinthe.affiche(self.window)
		self.solver.affiche(self.window)
		pygame.display.flip()

	def hold(self):
		""" hold() -> None
            Maintient la fenÃªtre ouverte jusqu'Ã  sa fermeture
            ou la pression de la touche 'Echap'."""
		lock = True
		while lock:
			events_list = pygame.event.get()
			for event in events_list:
				if event.type == QUIT:
					lock = False
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						lock = False

			self.solver._step()
			self.affiche()

			self.clock.tick(30)
		pygame.quit()


class Solver:
	def __init__(self, lab, cible):
		self.labyrinthe = lab
		self.i = 0
		self.j = 0
		self.cible_i, self.cible_j = cible
		self.chemin = []

	def _step(self):
		c = self.labyrinthe.cases[self.i][self.j]
		self.step(c)

	def case_voisine(self, d):
		""" renvoie une case voisine selon la valeur de d"""
		i, j = self.i, self.j
		if d == "H":
			return self.labyrinthe.case_voisine(i, j - 1)
		if d == "B":
			return self.labyrinthe.case_voisine(i, j + 1)
		if d == "G":
			return self.labyrinthe.case_voisine(i - 1, j)
		if d == "D":
			return self.labyrinthe.case_voisine(i + 1, j)

	def step(self, case):
		if self.i == self.cible_i and self.j == self.cible_j:
			return
		#case.visitee = True
		directions = ["H", "B", "G", "D"]
		n = randint(0, 3)
		d = directions[n]
		if not case.murs[d]:
			#self.chemin.append((self.i, self.j))
			if d == "H":
				self.j -= 1
			if d == "B":
				self.j += 1
			if d == "G":
				self.i -= 1
			if d == "D":
				self.i += 1

	def affiche(self, window):
		self.labyrinthe.affiche_cercle(window, (128, 255, 128), self.i, self.j)
		for i, j in self.chemin:
			self.labyrinthe.affiche_cercle(window, (128, 224, 128), i, j)
		self.labyrinthe.affiche_cercle(window, (255, 255, 128), self.cible_i,
		                               self.cible_j)


lab = Labyrinthe(5, 5, 40)
sol = Solver(lab, (3, 2))

#lab = Labyrinthe(40, 40, 10)
#sol = Solver(lab, (20, 20))
Main(lab, sol)
