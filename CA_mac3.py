import pygame
import random
import math
import time
import pdb
import matplotlib.pyplot as plt

# global parameters
V_AGE = 1
I_AGE = 100
PROB_INFECT = .1
VIRUS_BURN_NO = 1

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

# virus list 
class MapGrid():
    def __init__(self, map_width, map_height,moi):
        # set map values
        self.map_width = map_width
        self.map_height = map_width
        self.moi = moi

        # generate outside rooms
        self.Virus_list,self.init_grids = self._generate_init_grids(self.map_width,self.map_height,self.moi)
        self.ICell_set = {}# key is (x,y), value is age
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

    def _virus_update(self,grids,ind):
        '''Update the virus which is free'''
        pre_loc = self.Virus_list[ind].loc
        self.Virus_list[ind].move(self.map_width,self.map_height)
        tmp_loc = self.Virus_list[ind].loc
        if tmp_loc != pre_loc:
            if grids[pre_loc[0]][pre_loc[1]] == 1:
                grids[pre_loc[0]][pre_loc[1]] = 0
            elif grids[pre_loc[0]][pre_loc[1]] == 4:
                grids[pre_loc[0]][pre_loc[1]] = 3
        if grids[tmp_loc[0]][tmp_loc[1]] == 0:
            grids[tmp_loc[0]][tmp_loc[1]] = 1
        elif grids[tmp_loc[0]][tmp_loc[1]] == 3:
            grids[tmp_loc[0]][tmp_loc[1]] = 4
        
        return grids

    def _update_whole_CA(self, pre_grids):
        '''
        Update the whole CA model here. 
        '''
        global VIRUS_BURN_NO
        global I_AGE 
        global PROB_INFECT
        global V_AGE

        grids = pre_grids 
        # 1. Update the ICell age, death and virus production 
        for ICell in self.ICell_set:
            self.ICell_set[ICell] += 1

            if self.ICell_set[ICell] >= I_AGE: #ICell explode to Virus
                self.ICell_set[ICell] = 1000

                for tmp in range(VIRUS_BURN_NO): #budding virus copy number
                    self.Virus_list.append(Virus(list(ICell),-1))

                grids[ICell[0]][ICell[1]] = 1
                
            else:
                grids[ICell[0]][ICell[1]] = 2

        # remove dead 
        self.Dead_set = self.Dead_set | {k for k,v in self.ICell_set.items() if v==1000}
        self.ICell_set = {k:v for k,v in self.ICell_set.items() if v!=1000}

        for xy in self.Dead_set:
            grids[xy[0]][xy[1]] = 0

        # 2. Update Virus
        for i in range(len(self.Virus_list)):
            loc_tmp =self.Virus_list[i].loc
            if self.Virus_list[i].age!=-1:
                self.Virus_list[i].age +=1 # update age 

                if grids[loc_tmp[0]][loc_tmp[1]] ==4: # T+V already
                    p_tmp = random.random() # random number to determine infection
                    if p_tmp > PROB_INFECT: #if infected
                        # add this cell to I Cells (age 0)
                        self.ICell_set[tuple(loc_tmp)] = 0
                        
                        grids[loc_tmp[0]][loc_tmp[1]] = 2 # Update grid to Infected state 
                        self.Virus_list[i].age = V_AGE # mark this virus to remove   
                    else: # not infected
                        grids = self._virus_update(grids,i)
                else: # not T+V 
                    grids = self._virus_update(grids,i)

            else: # just born, set age to 0
                self.Virus_list[i].age += 1
                grids[loc_tmp[0]][loc_tmp[1]] = 1 # Update grid to Infected state                 
                
        self.Virus_list = self._remove(V_AGE,self.Virus_list)

        return grids


if __name__ == '__main__':
    # general map stats
    map_width = 500
    map_height = 500
    moi = 0.1
    no_cells = float(map_width*map_height)
    
    # start with one generation
    tile_size = 1
    unit_size = 1
        
    map_grid = MapGrid(map_width, map_height,moi) #init a random grid filled with 0s and 1s 
    
    pygame.init()

    screen = pygame.display.set_mode((map_width * tile_size,map_height * tile_size))#return Surface

    zero_tile = pygame.Surface((unit_size, unit_size))
    zero_tile.fill((0,0,0))#blue, nothing
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

    # plot setting
    fig = plt.figure()
    plt.axis = ([0,100,0,1])
    plt.ion()
    plt.show()
    
    # running 
    while running == True:
        clock.tick(1)

        for event in pygame.event.get():#get the events from queue
            if event.type == pygame.QUIT:
                running = False

        if first_gen:
            themap = map_grid.init_grids
        else:
            themap1 = map_grid._update_whole_CA(themap) #update 1 generation 
            themap = themap1 
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
        I_frac = float(len(map_grid.ICell_set)/(no_cells-len(map_grid.Dead_set)))          

        generation += 1
        pygame.display.set_caption('G: ' + str(generation) + ' VF: ' + str(virus_frac)
                                  +' IF: '+str(I_frac) )

        # plot
        plt.scatter(generation,I_frac)
        plt.draw()

    pygame.quit()
