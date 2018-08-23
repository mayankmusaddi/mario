import time,random,os
from action import *

floorPos = 23	
g= -20

class Element:
	def __init__(self,x,y,*designs):
		self.x = x
		self.y = y
		self.designArr=[]
		self.design=[]
		self.height=0
		self.width=0
		if len(designs) > 0:
			for file in designs:
				self.designArr.append(Write.toArray(file))
			self.design=self.designArr[0]
			self.height = len(self.design)
			self.width = len(self.design[0])

class Character(Element):
	def __init__(self,life,x,y,*designs):
		self.life=life
		self.posture=0
		self.dn=1
		self.velocity=0
		self.jumpTime=time.time()
		self.spawnTime = time.time()
		self.cannotCross=[]
		super(Character,self).__init__(x,y,*designs)

	def motion(self):
		self.posture+=self.dn
		if self.posture is (len(self.designArr)-1) or self.posture is 0:
			self.dn*=-1
		if len(self.designArr) is 1:
			self.posture = 0
		self.design=self.designArr[self.posture]

	def moveRight(self,structure):
		self.motion()
		self.x+=1
		if not self.tangible(structure):
			self.x-=1
			return False
		return True


	def moveLeft(self,structure):
		self.motion()
		self.x-=1
		if not self.tangible(structure):
			self.x+=1
			return False
		return True

	def moveUp(self,structure):
		self.y-=1
		if not self.tangible(structure):
			self.y+=1
			return False
		return True

	def moveDown(self,structure):
		self.y+=1
		if not self.tangible(structure):
			self.y-=1
			return False
		return True

	def tangible(self,structure):
		cy=round(self.y)
		for line in structure.design[ round(self.y) : round(self.y+self.height) ] :

			if '-' in line[self.x:self.x+self.width]:
				self.velocity=23
				return True

			for character in self.cannotCross:
				if character in line[self.x:self.x+self.width]:
					return False
			cy+=1
		return True

	def gravity(self,structure):

		if self.y >= floorPos :
			self.life -=1
			if self.life > 0:
				self.spawn(structure)

		t = time.time()-self.jumpTime
		by = self.y
		self.y -= t*(self.velocity + (0.5 * g * t)) 
		self.velocity += g*t
		self.jumpTime=time.time()
		if self.y < 0:
			self.y=0

		if not self.tangible(structure):
			self.y=by
			self.velocity = 0
			return False
		return True

class Missile(Character):
	def __init__(self,life,x,y,*designs):
		super(Missile,self).__init__(life,x,y,*designs)

	def attack(self,enemy):
		if self.x+self.width == enemy.x and self.y+self.height > enemy.y and enemy.y+enemy.height > self.y:
			enemy.life-=1
			self.life-=1

class Fire(Character):
	def __init__(self,life,x,y,*designs):
		super(Fire,self).__init__(life,x,y,*designs)

	def attack(self,enemy):
		if self.x == enemy.x and self.y+self.height > enemy.y and enemy.y+enemy.height > self.y:
			enemy.life-=1
			self.life-=1

class Goomba(Character):
	def __init__(self,life,x,y,*designs):
		self.direction = -1
		self.slow = 0.5
		super(Goomba,self).__init__(life,x,y,*designs)

	def move(self,structure):
		if time.time()-self.spawnTime > self.slow:
			if self.direction == -1:
				if not self.moveLeft(structure):
					self.direction = 1
			else:
				if not self.moveRight(structure):
					self.direction = -1
			self.spawnTime = time.time()

class Boss(Character):
	def __init__(self,life,x,y,*designs):
		self.slow = 2
		self.fires=[]
		self.fireTime=time.time()
		self.health = "  ####################################"
		super(Boss,self).__init__(life,x,y,*designs)

	def move(self,structure):
		if time.time()-self.spawnTime > self.slow:
			self.y = random.randrange(12)
			self.spawnTime = time.time()

	def gravity(self,structure):
		pass

	def attack(self):
		if time.time()-self.fireTime > self.slow*2:
			for i in range(4,7):
				fire = Fire(1,self.x - abs(i%5 - 2),self.y+i,"./designs/fire.txt")
				fire.cannotCross=['T','|','/','\\','`']
				self.fires.append(fire)
			self.fireTime = time.time()

class Mario(Character):
	def __init__(self,life,x,y,*designs):
		self.kills=0
		self.coins=0
		self.gun = False
		self.missiles=[]
		super(Mario,self).__init__(life,x,y,*designs)

	def kill(self,enemy,structure):
		if (round(self.y)+self.height-1 == round(enemy.y)) and self.x+self.width > enemy.x and enemy.x+enemy.width > self.x:
			enemy.life-=1
		elif self.y+self.height > enemy.y and enemy.y+enemy.height > self.y and self.x+self.width > enemy.x and enemy.x+enemy.width > self.x :
			self.life-=1
			self.spawn(structure)

	def attack(self):
		if self.gun is True:
			missile= Missile(1,self.x+5,self.y+2	,"./designs/missile.txt")
			missile.cannotCross=['T','|','/','\\','`']
			self.missiles.append(missile)

	def spawn(self,structure):
		self.x=structure.pos+2
		self.y=0
		self.velocity=0

	def tangible(self,structure):
		cy=round(self.y)
		for line in structure.design[ round(self.y) : round(self.y+self.height) ] :

			cx=self.x
			for character in line[self.x:self.x+self.width]:
				space = Element(cx,cy,"./designs/empty.txt")
				if character is '0' or character is '?':
					self.coins+=1
					structure.place(space)
				if character is 'H':
					self.life+=1
					structure.place(space)
				if character is '>':
					self.gun = True
					structure.place(space)
				cx+=1

			if '-' in line[self.x:self.x+self.width]:
				self.velocity=26
				return True

			for character in self.cannotCross:
				if character in line[self.x:self.x+self.width]:
					return False
			cy+=1
		return True	

class Level(Element):

	def __init__(self,x,y,*designs):
		super(Level,self).__init__(x,y,*designs)
		self.pos=0

	def moveForward(self):
		arrR=[]
		for line in self.design :
			l = line[1:]+line[:1]
			arrR.append(l)
		self.design = arrR

	def print(self):
		for line in self.design:
			print(line[self.pos:self.pos+80])

	def place(self,toPlace):
		arrP=[]
		cy=0
		for line in self.design:
			if ( cy>=toPlace.y and cy< toPlace.y+len(toPlace.design)):
				l = line[:toPlace.x] + toPlace.design[cy-toPlace.y] + line[ (toPlace.x+len(toPlace.design[cy-toPlace.y])) :]
			else:
				l = line
			arrP.append(l)
			cy+=1
		self.design=arrP

	def printOnTop(self,*characters):
		temp = self.design
		for toPlace in characters:
			arrP=[]
			cy=0
			for line in temp:
				if ( cy >= round(toPlace.y) and cy< round(toPlace.y)+len(toPlace.design)):
					l = line[ : toPlace.x ] + toPlace.design[ cy-round(toPlace.y) ] + line[ (toPlace.x+len(toPlace.design[ cy-round(toPlace.y) ])) :]
				else:
					l = line
				arrP.append(l)
				cy+=1
			temp = arrP
		os.system("clear")
		for line in temp:
			print(line[self.pos: self.pos+80])