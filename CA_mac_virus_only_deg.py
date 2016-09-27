##### RANDOM MAP GENERATOR #####
import pygame
import random
import math
import time


class Virus():
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

class Cell():
    def __init__(self,loc):
        self.loc = loc
        
# virus list 

class MapGrid():
    def __init__(self, map_width, map_height,moi):

        # set map values
        self.map_width = map_width
        self.map_height = map_width
        self.moi = moi

        # generate outside rooms
        self.Virus_list,self.outside_terrain_grid = self._generate_init_grids(self.map_width,self.map_height,self.moi)


    def _generate_init_grids(self, map_width, map_height, moi):
        '''
        creates a random distirubted virus in the map with moi from 0 to 1
        '''
        Virus_list = []

        new_map_grid = [[3]* map_width for i in xrange(map_height)] # create our new list        
        num_grids = map_height*map_width
        virus_seq = random.sample(range(num_grids),int(moi*num_grids))

        # get the each virus index in 2d form
        for virus in virus_seq:
            virus_ind = [virus%map_width,virus/map_height]
            new_map_grid[virus_ind[0]][virus_ind[1]] = 4
            Virus_list.append(Virus(virus_ind,random.choice([0,1,2,3,4])))
        return Virus_list,new_map_grid

    def _generate_grids(self,grids,Virus_list):
        grids = [[3 for col in row] for row in grids] # create our new list        
        for i in range(len(Virus_list)):
            grids[Virus_list[i].loc[0]][Virus_list[i].loc[1]] = 4
        return grids
                
        

    def _generate_outside_terrain(self, empty_outside_terrain_grid, number_of_generations):
        '''
        creates a bubble effect with cellular automaton
        '''
        grid = empty_outside_terrain_grid
        number_of_generations = number_of_generations

        for x in range(number_of_generations):
            for ind in range(len(self.Virus_list)):
                self.Virus_list[ind].move(self.map_width,self.map_height)
                self.Virus_list[ind].age += 1
            self.Virus_list = filter(lambda a:a.age !=5,self.Virus_list)
        return self._generate_grids(grid,self.Virus_list)

if __name__ == '__main__':
    # general map stats
    map_width = 100
    map_height = 100
    moi = 0.05
    no_cells = float(map_width*map_height)
    
    # start with one generation
    tile_size = 5
    unit_size = 4
        
    map_grid = MapGrid(map_width, map_height,moi) #init a random grid filled with 0s and 1s 
    
    pygame.init()

    screen = pygame.display.set_mode((map_width * tile_size,map_height * tile_size))#return Surface

    zero_tile = pygame.Surface((unit_size, unit_size))
    zero_tile.fill((0,0,255))#blue, nothing
    one_tile = pygame.Surface((unit_size,unit_size))
    one_tile.fill((255,205,0)) # yellow , virus 
    two_tile = pygame.Surface((unit_size,unit_size))
    two_tile.fill((0,128,0)) # green, infected cell
    three_tile = pygame.Surface((unit_size,unit_size))
    three_tile.fill((196,2,51)) # red, target cell
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
            themap = map_grid.outside_terrain_grid
        else:
            themap = map_grid._generate_outside_terrain(themap, 1) #update 1 generation 

        # visualization  
        for column_index, column in enumerate(themap):
            for tile_index, tile in enumerate(column):
                screen.blit(colors[tile], (tile_index * tile_size, column_index * tile_size))

        pygame.display.flip()

        if first_gen:
            timer -= 1
            if timer < 0:
                first_gen = False
        generation += 1
        pygame.display.set_caption('Generation: ' + str(generation) + ' Virus fraction: '
                                   + str(float(len(map_grid.Virus_list)/no_cells)))
    pygame.quit()
