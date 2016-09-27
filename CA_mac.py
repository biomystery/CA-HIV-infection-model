import pygame
import random
import math
import time

# global parameters
V_AGE = 10
I_AGE = 10
PROB_INFECT = .5
VIRUS_BURN_NO = 5

class Virus():
    '''Virus Class:
    Two attributes: location and age ([0,10])
    also able to : move(width, height) 
    '''
    def __init__(self,loc,age):
        self.loc = loc
        self.age = age
        
    def move(self,width,height):
        self.loc[0] += random.choice([-1,0,1])
        self.loc[1] += random.choice([-1,0,1])
        self.loc[0] = 0 if self.loc[0]<0 else self.loc[0]
        self.loc[1] = 0 if self.loc[1]<0 else self.loc[1]        
        self.loc[0] = width-1 if self.loc[0]>width-1 else self.loc[0]
        self.loc[1] = height-1 if self.loc[1]>height-1 else self.loc[1]        

# Infected cells         
class ICell(): 
    '''Infected Cell (ICell) class:
    only have two attributes: location and age
    '''
    def __init__(self,loc,age):
        self.loc = loc
        self.age = age

# virus list 
class MapGrid():
    def __init__(self, map_width, map_height,moi):
        # set map values
        self.map_width = map_width
        self.map_height = map_width
        self.moi = moi

        # generate outside rooms
        self.Virus_list,self.init_grids = self._generate_init_grids(self.map_width,self.map_height,self.moi)
        self.ICell_list = []
        self.Dead_set = set([])

    def _generate_init_grids(self, map_width, map_height, moi):
        '''
        creates a random distirubted virus in the map with moi from 0 to 1
        '''
        global V_AGE
        Virus_list = []

        # init 1: fill the grids with T (state 3)
        new_map_grid = [[3]* map_width for i in xrange(map_height)] 

        # init 2: random distribute moi virus.
        num_grids = map_height*map_width
        virus_seq = random.sample(range(num_grids),int(moi*num_grids)) #1D

        for virus in virus_seq: # 1D-> 2D
            virus_ind = [virus%map_width,virus/map_height]
            new_map_grid[virus_ind[0]][virus_ind[1]] = 4
            Virus_list.append(Virus(virus_ind,random.choice(range(V_AGE)))) # random asign age

        # return grids and virus_list
        return Virus_list,new_map_grid 

    def _remove(self,age_limit,class_list):
        '''Input class which have age'''
        return filter(lambda a:a.age!=age_limit,class_list)

    def _update_whole_CA(self, init_grids):
        '''
        Update the whole CA model here. number_of_generations is used 
        to determine 
        '''
        global VIRUS_BURN_NO
        global I_AGE 
        global PROB_INFECT
        global V_AGE

        # 1. Update the ICell age, death and virus production 
        for i in range(len(self.ICell_list)):
            self.ICell_list[i].age += 1
            if self.ICell_list[i].age >= I_AGE: #ICell explode to Virus
                self.ICell_list[i].age = 1000
                self.Dead_set.add(tuple(self.ICell_list[i].loc))
                    
                for tmp in range(VIRUS_BURN_NO): #budding virus copy number
                    self.Virus_list.append(Virus(self.ICell_list[i].loc,0))
                    
        self.ICell_list = self._remove(1000,self.ICell_list)
            
        # 2. Update Virus ages & move
        for i in range(len(self.Virus_list)):
            self.Virus_list[i].move(self.map_width,self.map_height)
            self.Virus_list[i].age += 1
        
        self.Virus_list = self._remove(V_AGE,self.Virus_list)

        # 3. Set the grids, default states: Target cell only (3)
        grids = [[3 for col in row] for row in init_grids] 

        # update1: check the dead ones, add the dead ones
        for xy in self.Dead_set: 
            grids[xy[0]][xy[1]] = 0

        # update2: infected cell
        for i in range(len(self.ICell_list)):
            tmp_loc = self.ICell_list[i].loc
            if grids[tmp_loc[0]][tmp_loc[1]] == 0:
                self.ICell_list[i].age = 1000
                print "I moved to Empty"
            else:
                grids[tmp_loc[0]][tmp_loc[1]] = 2

        self.ICell_list = self._remove(1000,self.ICell_list) #clear all the dead Cells

        # update3: put the virus in after move, enounter cell or not?
        for i in range(len(self.Virus_list)): 
            
            loc_tmp =self.Virus_list[i].loc
            p_tmp = random.random() # random number to determine infection
            
            if grids[loc_tmp[0]][loc_tmp[1]] ==3: #meet target cell
                if p_tmp > PROB_INFECT: #not infected
                    grids[loc_tmp[0]][loc_tmp[1]] = 4 # V + T
                else: # infected
                    self.ICell_list.append(ICell(loc_tmp,0)) # add this cell to I Cells (age 0)
                    grids[loc_tmp[0]][loc_tmp[1]] = 2 # Set the grid Infected state
                    self.Virus_list[i].age = V_AGE # mark this virus to remove
                
            elif grids[loc_tmp[0]][loc_tmp[1]] ==0: # no Target Cell
                grids[loc_tmp[0]][loc_tmp[1]] = 1 # V only
            

        # after update2, remove the virus who successfully infect T         
        self.Virus_list = self._remove(V_AGE,self.Virus_list) 
            
        return grids


if __name__ == '__main__':
    # general map stats
    map_width = 50
    map_height = 50
    moi = 0.05
    no_cells = float(map_width*map_height)
    
    # start with one generation
    tile_size = 10
    unit_size = 9
        
    map_grid = MapGrid(map_width, map_height,moi) #init a random grid filled with 0s and 1s 
    
    pygame.init()

    screen = pygame.display.set_mode((map_width * tile_size,map_height * tile_size))#return Surface

    zero_tile = pygame.Surface((unit_size, unit_size))
    zero_tile.fill((255,255,255))#blue, nothing
    one_tile = pygame.Surface((unit_size,unit_size))
    one_tile.fill((255,255,0)) # yellow , virus 
    two_tile = pygame.Surface((unit_size,unit_size))
    two_tile.fill((0,255,0)) # green, infected cell
    three_tile = pygame.Surface((unit_size,unit_size))
    three_tile.fill((255,0,0)) # red, target cell
    four_tile = pygame.Surface((unit_size,unit_size))
    four_tile.fill((255,165,0)) # orange, T + V
    colors = {0: zero_tile, 1: one_tile,2: two_tile , 3: three_tile, 4:four_tile} 

    background = pygame.Surface((map_width * tile_size,map_height * tile_size))

    clock = pygame.time.Clock()#an object to help track time 

    first_gen = True
    timer = 1
    
    running = True
    generation  = 0
    while running == True:
        clock.tick(1)

        for event in pygame.event.get():#get the events from queue
            if event.type == pygame.QUIT:
                running = False

        if first_gen:
            themap = map_grid.init_grids
        else:
            themap = map_grid._update_whole_CA(themap) #update 1 generation 

        # visualization  
        for column_index, column in enumerate(themap):
            for tile_index, tile in enumerate(column):
                screen.blit(colors[tile], (tile_index * tile_size, column_index * tile_size))

        pygame.display.flip()

        if first_gen:
            timer -= 1
            if timer <= 0:
                first_gen = False

        virus_frac = float(len(map_grid.Virus_list)/no_cells)       
        generation += 1
        pygame.display.set_caption('Generation: ' + str(generation) + ' Virus fraction: '
                                   + str(virus_frac))

    pygame.quit()
