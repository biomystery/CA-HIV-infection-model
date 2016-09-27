##### RANDOM MAP GENERATOR #####
import pygame
import random
import math
import time
import matplotlib.pyplot as plt

CELL_AGE_MAX = 100

class MapGrid():
    def __init__(self, map_width, map_height,moi):

        # set map values
        self.map_width = map_width
        self.map_height = map_width
        self.moi = moi

        # generate outside rooms
        self.outside_terrain_grid = self._generate_init_virus_grid(self.map_width, self.map_height,self.moi)

        # age

    def _index_transfer(self, map_width, map_height, one_index):
        '''transfer 1d index (one_index) to 2d'''
        x = one_index % map_width
        y = one_index / map_width
        return [x,y]

    def _generate_init_virus_grid(self, map_width, map_height, moi):
        '''
        creates a random distirubted virus in the map with moi from 0 to 1
        '''
        new_map_grid = [[0]* map_width for i in xrange(map_height)] # create our new list
        num_grids = map_height*map_width
        virus_seq = random.sample(range(num_grids),int(moi*num_grids))
        
        # get the each virus index in 2d form
        for virus in virus_seq:
            virus_ind = self._index_transfer(map_width,map_height,virus)
            new_map_grid[virus_ind[0]][virus_ind[1]] = 1

        return new_map_grid


    def _generate_outside_terrain(self, empty_outside_terrain_grid, number_of_generations):
        '''
        creates a bubble effect with cellular automaton
        '''
        grid = empty_outside_terrain_grid
        number_of_generations = number_of_generations

        for x in range(number_of_generations):
            next_grid = []
            for column_index, column in enumerate(grid):
                next_column = []
                next_grid.append(next_column)
                for tile_index, tile in enumerate(column):
                    

                    # get the surrounding tile values for each tile
                    top_left = grid[column_index - 1][tile_index - 1]
                    top_mid = grid[column_index][tile_index - 1]
                    try:
                        top_right = grid[column_index + 1][tile_index - 1]
                    except IndexError:
                        top_right = 0
                    
                    center_left = grid[column_index - 1][tile_index]
                    center_mid = grid[column_index][tile_index]
                    try:
                        center_right = grid[column_index + 1][tile_index]
                    except IndexError:
                        center_right = 0

                    try:
                        bottom_left = grid[column_index - 1][tile_index + 1]
                    except IndexError:
                        bottom_left = 0
                    try:
                        bottom_mid = grid[column_index][tile_index + 1]
                    except IndexError:
                        bottom_mid = 0
                    try:
                        bottom_right = grid[column_index + 1][tile_index + 1]
                    except IndexError:
                        bottom_right = 0


                    neighbors = [top_mid, center_left , center_mid, center_right ,
                                 bottom_mid, top_left , top_right , bottom_left , bottom_right]

                    number_of_A1 = neighbors.count(1)
                    number_of_A2 = neighbors.count(2)

                    if tile ==0: #healthy
                        if number_of_A1 > 0 and random.random()< 0.11:
                            next_cell = 1
                        elif number_of_A2 >=4:
                            next_cell = 1
                        else:
                            next_cell = tile
                    elif tile == 1:
                        next_cell = 2 
                    elif tile ==2:
                        if random.random()<0.05/2:
                            next_cell = 3
                        else:
                            next_cell = tile
                    elif tile == 3:#dead
                        next_cell = tile
                        '''if random.random()<.01:
                            if random.random() < .00001:
                                next_cell = 1 
                            else:
                                next_cell = 0 #replace by healthy
                        else:
                            next_cell = tile # remain dead'''    


                    # create the new cell
                    next_column.append(next_cell)
            grid = next_grid
        return next_grid



                    
if __name__ == '__main__':
    # general map stats
    map_width = 100
    map_height = 100
    no_cells = map_width*map_height
    
    moi = 0.1
    # start with one generation
    tile_size = 8
    unit_size = 8
        
    map_grid = MapGrid(map_width, map_height,moi) #init a random grid filled with 0s and 1s 

    pygame.init()

    screen = pygame.display.set_mode((map_width * tile_size,map_height * tile_size))#return Surface

    zero_tile = pygame.Surface((unit_size, unit_size))
    zero_tile.fill((255,0,0))# health: red
    one_tile = pygame.Surface((unit_size,unit_size))
    one_tile.fill((0,255,0)) # green 
    two_tile = pygame.Surface((unit_size,unit_size))
    two_tile.fill((0,255,0)) # green
    three_tile = pygame.Surface((unit_size,unit_size))
    three_tile.fill((0,0,0)) # dead red
    colors = {0: zero_tile, 1: one_tile,2: two_tile , 3: three_tile} # 0: healthy-blue, 1: infected-A1-yellow, 2:

    background = pygame.Surface((map_width * tile_size,map_height * tile_size))

    clock = pygame.time.Clock()#an object to help track time 

    first_gen = True
    timer = 1
    
    running = True

    # counters:
    generation  = 0    

    # plot setting
    fig = plt.figure()
    plt.axis = ([0,100,0,1])
    plt.ion()
    plt.show()

    
    while running == True:
        clock.tick(1)

        for event in pygame.event.get():#get the events from queue
            if event.type == pygame.QUIT:
                running = False

        if first_gen:
            themap = map_grid.outside_terrain_grid
        else:
            themap = map_grid._generate_outside_terrain(themap, 1) #update 1 generation 

        I_counter = 0 
        Dead_counter = 0
            
        for column_index, column in enumerate(themap):
            for tile_index, tile in enumerate(column):
                screen.blit(colors[tile], (tile_index * tile_size, column_index * tile_size))
                if tile == 1 or tile ==2:
                    I_counter += 1 
                elif tile == 3:
                    Dead_counter += 1
                    
        I_frac = I_counter/float(no_cells - Dead_counter)
        generation += 1

        pygame.display.flip()
        
        if first_gen:
            timer -= 1
            if timer < 0:
                first_gen = False

        pygame.display.set_caption('G: ' + str(generation)  
                                   +' IF: '+str(I_frac) )

        # plot
        plt.scatter(generation,I_frac)
        plt.draw()

        # save windows
        if generation%5 == 0:
            filename = "c2c"+ str(generation) +".jpeg"
            pygame.image.save(screen,filename)
        if generation == 1000:
            pygame.quit()

