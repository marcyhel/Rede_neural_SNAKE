import pygame
import copy
from rede import *

class Genetico:
	def __init__(self,populacao=50,melhores=10,porcentagem=0.5,voltas=3):
		self.populacao=populacao
		self.qtd_melhores=melhores
		self.porcentagem=porcentagem
		self.individuos=[]
		self.voltas=voltas
		self.voltasDadas=0
		self.tamanhoTabuleiro=60
		self.criaPopulacao()
		self.contGeracao=0
	def criaPopulacao(self):
		for i in range(self.populacao):
			self.individuos.append(Tabuleiro(self.tamanhoTabuleiro,inicia=False))
	def verificaPontos(self):
		cont=0
		for i in self.individuos:
			if( i.cobrinha.pontos>=0):
				cont+=1
			i.update()
		#print('cont')
		if(cont==0):
			print("volta")
			for i in self.individuos:
				i.cobrinha.semiReset()
				i.spawComida()
			self.voltasDadas+=1
	def ordena(self):
		for i in range(len(self.individuos)):
			for j in range(len(self.individuos)):
				if(self.individuos[i].cobrinha.tempo>self.individuos[j].cobrinha.tempo):
					aux=self.individuos[i]
					self.individuos[i]=self.individuos[j]
					self.individuos[j]=aux
		aux=[]
		for i in range(self.populacao-self.qtd_melhores):
			self.individuos.pop()
	def crossOver(self):
		melhores=copy.deepcopy(self.individuos)
		for i in range(self.populacao-self.qtd_melhores):
			novo=Tabuleiro(self.tamanhoTabuleiro)
			#cross
			if(random.random()<=0.7):
				pai=random.sample(melhores,3)
				for i in range(len(novo.cobrinha.rede.neuronios)):
					novo.cobrinha.rede.neuronios[i]=copy.deepcopy(pai[random.randint(0,len(pai)-1)].cobrinha.rede.neuronios[i])
			#mutacao
			if(random.random()<=self.porcentagem):
				for i in range(int(len(novo.cobrinha.rede.neuronios)/random.randint(2,5))+1):
					x=random.randint(0,len(novo.cobrinha.rede.neuronios[i].dado)-1)
					y=random.randint(0,len(novo.cobrinha.rede.neuronios[i].dado[0])-1)
					novo.cobrinha.rede.neuronios[i].dado[x][y]=random.random()* 2-1
			#add individuo
			self.individuos.append(novo)
	def update(self,screen):
		ids = font.render("Geração: "+str(self.contGeracao), True, pygame.Color('white'))
		screen.blit(ids, (50, 200))
		#print(self.voltasDadas,self.voltas)
		if(self.voltasDadas<self.voltas):
			#print(self.voltasDadas,self.voltas)
			self.verificaPontos()
		elif(self.voltasDadas==self.voltas):
			self.voltasDadas=0
			
			self.ordena()
			print("geracao: {}".format(self.contGeracao))
			for i in self.individuos:
				print(i.cobrinha.id,i.cobrinha.tempo)
				i.cobrinha.resetar()
			for i in range(len(self.individuos[0].cobrinha.rede.neuronios)):
				self.individuos[0].cobrinha.rede.salvar('cobrinhaNova'+str(i),self.individuos[0].cobrinha.rede.neuronios[i].dado)
			self.contGeracao+=1
			self.crossOver()
			

			#for i in self.individuos:
			#    print(i.cobrinha.tempo)
		

class Bloco:
	def __init__(self,tam,x,y,tab):
		self.grade=600/tam
		self.posi=[x,y]
		self.tab=tab
	def update(self):
		pass
	def render(self,screen):
		pygame.draw.rect(screen,(50,50,90), pygame.Rect(self.posi[0]*self.grade,self.posi[1]*self.grade,self.grade-1, self.grade-1))
class Comida:
	def __init__(self,tam,x,y,tab):
		self.grade=600/tam
		self.posi=[x,y]
		self.tab=tab
		
	def update(self):
		pass
	def render(self,screen):
		pygame.draw.rect(screen,(50,120,90), pygame.Rect(self.posi[0]*self.grade,self.posi[1]*self.grade,self.grade-1, self.grade-1))
class Cobrinha:
	def __init__(self,tam,tab,inicia=False):
		self.tab=tab
		self.tam=tam
		self.grade=600/tam
		self.corpo=[[5,5],[4,5],[3,5]]
		self.dir=2

		self.rede=RedeNeural()
		self.rede.ativador=RedeNeural.tanh
		self.rede.addNeuronio(11,11)
		self.rede.addNeuronio(11,11)
		self.rede.addNeuronio(11,4)
		self.inicia=inicia
		if(self.inicia):
			self.rede.neuronios[0].dado=self.rede.ler('cobrinhaNova0')
			self.rede.neuronios[1].dado=self.rede.ler('cobrinhaNova1')
			self.rede.neuronios[2].dado=self.rede.ler('cobrinhaNova2')
		self.basePontos=(self.tam*self.tam)/1.8
		self.pontos=self.basePontos
		self.tempo=0
		self.vivo=True

		self.entrada=[]

		self.color=[255,0,0]
		self.cor=[255,0,0]
		self.id=random.randint(0,1000)
		self.resetar()
	
	def crescer(self):
		self.corpo.append(self.corpo[len(self.corpo)-1])
		self.tempo+=1
	def semiReset(self):
		self.pontos=self.basePontos
		self.vivo=True
		self.corpo=[[5,5],[4,5],[3,5]]
		self.dir=2
	def resetar(self):
		self.pontos=self.basePontos
		self.tempo=0
		self.vivo=True
		self.corpo=[[5,5],[4,5],[3,5]]
		self.dir=2
	def setMag(self,seg,mag):
		aux=[]
		aux1=[]
		#mag
		magentude=math.sqrt(seg[0]*seg[0] + seg[1]*seg[1]);
		#normalize
		if(magentude!=0 and magentude!=1):
			for i in seg:
				aux.append(i/magentude)
		else:
			aux=seg
		for i in aux:
			aux1.append(i*mag)
		return aux1
	def ver_parede(self):
		direita=self.corpo[0][0]
	   
		esquerda=self.tam-self.corpo[0][0]
		cima=self.corpo[0][1]
		baixo=self.tam-self.corpo[0][1]
		return cima,baixo,direita,esquerda
	def ver_corpo(self,cima,baixo,dir,esq):
		cimax=0
		
		for i in range(1,cima+1):
			if([self.corpo[0][0],self.corpo[0][1]-i] in self.corpo):
				cimax+=1
				break
			cimax+=1
		
		baixox=0
		
		for i in range(1,baixo+1):
			if([self.corpo[0][0],self.corpo[0][1]+i] in self.corpo):
				baixox+=1
				break
			baixox+=1
		
		dirx=0
		
		for i in range(1,dir+1):
			if([self.corpo[0][0]-i,self.corpo[0][1]] in self.corpo):
				dirx+=1
				break
			dirx+=1
		
		esqx=0
		
		for i in range(1,esq+1):
			if([self.corpo[0][0]+i,self.corpo[0][1]] in self.corpo):
				esqx+=1
				break
			esqx+=1
		
		return cimax,baixox,dirx,esqx
	def envolta(self):
		dire=[-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5]
		if([self.corpo[0][0]-1,self.corpo[0][0]-1] in  self.corpo):
		
			dire[0]=0.5
		if([self.corpo[0][0],self.corpo[0][1]-1] in  self.corpo):
			dire[1]=0.5
		if([self.corpo[0][0]+1,self.corpo[0][1]-1] in  self.corpo):
			dire[2]=0.5
		if([self.corpo[0][0]-1,self.corpo[0][1]] in  self.corpo):
			dire[3]=0.5
		if([self.corpo[0][0]+1,self.corpo[0][1]] in  self.corpo):
			dire[4]=0.5
		if([self.corpo[0][0]-1,self.corpo[0][1]+1] in  self.corpo):
		
			dire[5]=0.5
		if([self.corpo[0][0],self.corpo[0][1]+1] in  self.corpo):
			dire[6]=0.5
		if([self.corpo[0][0]+1,self.corpo[0][1]+1] in  self.corpo):
			dire[7]=0.5


		if([self.corpo[0][0]-1,self.corpo[0][1]-1] not in  self.tab.tatab):
			dire[0]=0.5
		if([self.corpo[0][0],self.corpo[0][1]-1] not in  self.tab.tatab):
			dire[1]=0.5
		if([self.corpo[0][0]+1,self.corpo[0][1]-1]  not in  self.tab.tatab):
			dire[2]=0.5
		if([self.corpo[0][0]-1,self.corpo[0][1]] not in  self.tab.tatab):
			dire[3]=0.5
		if([self.corpo[0][0]+1,self.corpo[0][1]] not in  self.tab.tatab):
			dire[4]=0.5
		if([self.corpo[0][0]-1,self.corpo[0][1]+1]  not in  self.tab.tatab):
			dire[5]=0.5
		if([self.corpo[0][0],self.corpo[0][1]+1] not in  self.tab.tatab):
			dire[6]=0.5
		if([self.corpo[0][0]+1,self.corpo[0][1]+1] not in  self.tab.tatab):
			dire[7]=0.5

		return dire
	def olhos(self):
		self.entrada=[]
		dire = [self.corpo[0][0] - self.tab.comida.posi[0], self.corpo[0][1] - self.tab.comida.posi[1]];
		angulo = (math.atan2(dire[1],dire[0]));
		#dire - entrada
		dire=self.setMag(dire,50)
		dire[0]=math.tanh(dire[0]/100)
		dire[1]=math.tanh(dire[1]/100)
		
		#parede - entrada
		cima,baixo,direita,esquerda = self.ver_parede()

		cimax,baixox,dirx,esqx=self.ver_corpo(cima,baixo,direita,esquerda)

		envol=self.envolta()
		if(cima==0  or baixo==0 or direita==0 or esquerda==0 ):
			self.vivo=False
			self.pontos=0
		#self.entrada=[
		#	math.tanh(self.dir/10),
		#dire[0],
		#dire[1],
		#math.tanh(cima/100),
		#math.tanh(baixo/100),
		#math.tanh(direita/100),
		#math.tanh(esquerda/100),
		#math.tanh(cimax/100),
		#math.tanh(baixox/100),
		#math.tanh(dirx/100),
		#math.tanh(esqx/100),
		#]

		self.entrada=[
			math.tanh(self.dir/10),
		dire[0],
		dire[1],
		envol[0],
		envol[1],
		envol[2],
		envol[3],
		envol[4],
		envol[5],
		envol[6],
		envol[7]]
		#print(dire)

	def verifica(self):
		resposta=self.rede.predict(self.entrada)
		index=0
		aux=resposta.dado[0][0]
		for i in range(len(resposta.dado)):
			if(resposta.dado[i][0]>aux):
				aux=resposta.dado[i][0]
				index=i
		return index
	def haDuplicados(self,lista):
		_lis = []

		# removendo duplicados
		for x in lista:
			if x not in _lis:
				_lis.append(x)

		# comparando os tamanhos
		if len(lista) != len(_lis):
			return True
		else:
			return False
	def update(self):
		self.pontos-=1
		if(self.vivo):
			
			
			#self.tempo+=1
			self.olhos()
			self.dir=self.verifica()

			#if(aux==0 and self.dir!=2):
			#    self.dir=aux
			#if(aux==2 and self.dir!=0):
			#    self.dir=aux
			#if(aux==1 and self.dir!=3):
			#    self.dir=aux
			#if(aux==3 and self.dir!=1):
			#    self.dir=aux
			#if(random.random()<=0.4):
			#    self.dir=random.randint(0,3)
			
			if(self.dir==0  ):
				self.corpo.insert(0,[self.corpo[0][0]-1,self.corpo[0][1]])
			if(self.dir==2):
				self.corpo.insert(0,[self.corpo[0][0]+1,self.corpo[0][1]])
			if(self.dir==1):
				self.corpo.insert(0,[self.corpo[0][0],self.corpo[0][1]+1])
			if(self.dir==3):
				self.corpo.insert(0,[self.corpo[0][0],self.corpo[0][1]-1])
			self.corpo.pop()
			if(self.dir>3):
				print('OPS')
			if(self.corpo[0][0]>=self.tam or self.corpo[0][0]<=0 and self.corpo[0][1]>=self.tam and self.corpo[0][1]<= 0  ):
				#print('perdeu')
				self.vivo=False
				self.pontos=0
				#print(1)
			if(self.haDuplicados(self.corpo)):
				self.vivo=False
				self.pontos=0
				#print(2)
				
			if(self.pontos==0):
				self.vivo=False
				self.pontos=0
				#print(3)
			
		
		
	def render(self,screen):
		self.color=self.cor.copy()
		
		divide=255/len(self.corpo)
		for i in range(len(self.corpo)):
			
			if( self.cor[1]>=255):
				self.cor[1]=255
				
			pygame.draw.rect(screen,(self.color[0],self.color[1],self.color[2]), pygame.Rect(self.corpo[i][0]*self.grade,self.corpo[i][1]*self.grade,self.grade-1, self.grade-1))
			self.color[1]+=divide
			if(len(self.corpo)-2== i):
				self.color[1]+=divide
			
class Tabuleiro:
	def __init__(self,tam,inicia=True):
		self.tam=tam
		self.grade=600/tam
		#print(self.grade)
		self.tab=[]
		self.tatab=[]
		self.iniciaTab()
		self.comida=0
		
		self.cobrinha=Cobrinha(tam,self,inicia=inicia)
		self.spawComida()
	
	def iniciaTab(self):
		for i in range(self.tam):
			aux=[]
			for j in range(self.tam):
				aux.append(Bloco(self.tam,i,j,self))
				self.tatab.append([i,j])
			self.tab.append(aux)
	def spawComida(self):
		while True:
			x=random.randint(1,self.tam-2)
			y=random.randint(1,self.tam-2)
			if([x,y] not in  self.cobrinha.corpo):
				self.comida=Comida(self.tam,x,y,self)
				break
	def comeu(self):
		if(self.comida.posi in  self.cobrinha.corpo):
			self.spawComida()
			self.cobrinha.crescer()
			self.cobrinha.pontos=self.cobrinha.basePontos
		
	def update(self):
		
		self.cobrinha.update()
		self.comeu()
	def render(self,screen):
		for i in range(self.tam):
			
			for j in range(self.tam):
				self.tab[i][j].render(screen)
		self.cobrinha.render(screen)
		self.comida.render(screen)


pygame.init()   
screen = pygame.display.set_mode((600, 600))
font = pygame.font.Font(None, 30)
done = False
clock = pygame.time.Clock()

#tab=Tabuleiro(30)
gene=Genetico()
aux=gene.individuos[0]
def render(screen):
	
	global aux
	for i in range(len(gene.individuos)):
	   for j in range(len(gene.individuos)):
	       if(gene.individuos[i].cobrinha.tempo>gene.individuos[j].cobrinha.tempo):
	           aux=(gene.individuos[i])
	auxVivo=[]
	#aux=[]
	
	
	for i in gene.individuos:
		if(i.cobrinha.pontos>0 and i.cobrinha.vivo):
			auxVivo.append(i)
	for i in auxVivo:
		for j in auxVivo:
			if(i.cobrinha.tempo>j.cobrinha.tempo):
				aux=i
	aux.render(screen)
	
	font = pygame.font.Font(None, 30)
	ids = font.render("ID: "+str(aux.cobrinha.id), True, pygame.Color('white'))
	screen.blit(ids, (50, 80))
	ids = font.render("Pontos: "+str(aux.cobrinha.tempo), True, pygame.Color('white'))
	screen.blit(ids, (50, 110))
	ids = font.render("Tamanho: "+str(len(aux.cobrinha.corpo)), True, pygame.Color('white'))
	screen.blit(ids, (50, 140))

	ids = font.render("Tamanho: "+str(len(aux.cobrinha.corpo)), True, pygame.Color('white'))
	screen.blit(ids, (50, 140))

	font = pygame.font.Font(None, 30)
	ids = font.render(str(int(aux.cobrinha.pontos)), True, pygame.Color('white'))
	screen.blit(ids, (50, 170))
	
	#tab.render(screen)
def update(screen):
	#tab.update()
	gene.update(screen)
while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
			if ( pygame.mouse.get_pressed()[0]):
				pass
				
			if event.type == pygame.KEYDOWN:
				pass
			if event.type == pygame.KEYUP:
				pass
		pygame.display.flip()
		clock.tick(60)
		screen.fill((80,80,80))
		render(screen)
		update(screen)
		font = pygame.font.Font(None, 30)
		fps = font.render("fps: "+str(int(clock.get_fps())), True, pygame.Color('white'))
		screen.blit(fps, (50, 50))