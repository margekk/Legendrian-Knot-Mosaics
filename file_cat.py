# ~~~~
'''
Python program to catalog legendrian knot mosaics from a file based on Thurston Bennequin, rotation, and smooth knot type invariants.
Mosaics are represented by a base 10 number, which is read from the file and converted into a list.
The program then traverses the knot from a starting tile, calculating tb/rotation along the way.
If every tile has been traversed by the time we return to our starting point, we know that the mosaic represents a knot.

We also build the extended gauss code of the knot during traversal, which is used to calculate the knot's HOMFLY as detailed in the sagemath link below.
The invariants of this new knot are then compared to a list of knots found previously, and it is added to this list if its combination of invatiants have not occurred before.

The total number of mosaics representing knots is printed when the program ends, and the knot catalog is written to a file. 

Note: Every input file should start with an empty mosaic of the same size as the other mosaics, e.g:
000000000
000021034
000210340
...
Files produced by the associated rust program will always start this way.

Note: This program should be run in sagemath, which can be done by calling the program with sage from a terminal as one would with python (sage file_cat.py)

sagemath's Links library is used to calculate homfly polynomials -- see (https://doc.sagemath.org/html/en/reference/knots/sage/knots/link.html) for more details
See the associated rust file for information on how these mosaics are generated.

This material is based upon work supported by the National Science Foundation under Grant No. MPS-2150299
'''

from sage.all import *

#Basic driver function
def main():
    print("file to read from:")
    in_file = input()
    print('output file?:')
    out_file = input()

    legendrian_mosaic.batch_catalog(in_file, out_file) 

class legendrian_mosaic:
    #Valid connections for each tile
    #The first digit in the tuple represents the incoming face, the second the outgoing face.
    #Faces are assigned as below:
    #    1
    # 2 ▇▇ 0
    #    3
    valid_connections = (
        (()),
        ((2,3),(3,2)),
        ((0,3),(3,0)),
        ((0,1),(1,0)),
        ((2,1),(1,2)),
        ((2,0),(0,2)),
        ((1,3),(3,1)),
        ((2,3),(3,2),(1,0),(0,1)),
        ((0,3),(3,0),(2,1),(1,2)),
        ((0,2),(1,3),(2,0),(3,1))
    )

    #Dictionary of homfly polynomials for all prime knots through 8 crossings -- this is sufficient through 5x5 mosiacs
    knot_list = {
        Knots().one().homfly_polynomial() : '0_1',
        Knots().from_table(3,1).homfly_polynomial() : '3_1',
        Knots().from_table(3,1).mirror_image().homfly_polynomial(): 'm(3_1)',
        Knots().from_table(4,1).homfly_polynomial() : '4_1',
        Knots().from_table(5,1).homfly_polynomial() : '5_1',
        Knots().from_table(5,1).mirror_image().homfly_polynomial(): 'm(5_1)',
        Knots().from_table(5,2).homfly_polynomial() : '5_2',
        Knots().from_table(5,2).mirror_image().homfly_polynomial(): 'm(5_2)',
        Knots().from_table(6,1).homfly_polynomial(): '6_1',
        Knots().from_table(6,1).mirror_image().homfly_polynomial(): 'm(6_1)',
        Knots().from_table(6,2).homfly_polynomial(): '6_2',
        Knots().from_table(6,2).mirror_image().homfly_polynomial(): 'm(6_2)',
        Knots().from_table(6,3).homfly_polynomial(): '6_3',
        Knots().from_table(7,1).homfly_polynomial(): '7_1',
        Knots().from_table(7,1).mirror_image().homfly_polynomial(): 'm(7_1)',
        Knots().from_table(7,2).homfly_polynomial(): '7_2',
        Knots().from_table(7,2).mirror_image().homfly_polynomial(): 'm(7_2)',
        Knots().from_table(7,3).homfly_polynomial(): '7_3',
        Knots().from_table(7,3).mirror_image().homfly_polynomial(): 'm(7_3)',
        Knots().from_table(7,4).homfly_polynomial(): '7_4',
        Knots().from_table(7,4).mirror_image().homfly_polynomial(): 'm(7_4)',
        Knots().from_table(7,5).homfly_polynomial(): '7_5',
        Knots().from_table(7,5).mirror_image().homfly_polynomial(): 'm(7_5)',
        Knots().from_table(7,6).homfly_polynomial(): '7_6',
        Knots().from_table(7,6).mirror_image().homfly_polynomial(): 'm(7_6)',
        Knots().from_table(7,7).homfly_polynomial(): '7_7',
        Knots().from_table(7,7).mirror_image().homfly_polynomial(): 'm(7_7)',
        Knots().from_table(8,1).homfly_polynomial(): '8_1',
        Knots().from_table(8,1).mirror_image().homfly_polynomial(): 'm(8_1)',
        Knots().from_table(8,2).homfly_polynomial(): '8_2',
        Knots().from_table(8,2).mirror_image().homfly_polynomial(): 'm(8_2)',
        Knots().from_table(8,3).homfly_polynomial(): '8_3',
        Knots().from_table(8,4).homfly_polynomial(): '8_4',
        Knots().from_table(8,4).mirror_image().homfly_polynomial(): 'm(8_4)',
        Knots().from_table(8,5).homfly_polynomial(): '8_5',
        Knots().from_table(8,5).mirror_image().homfly_polynomial(): 'm(8_5)',
        Knots().from_table(8,6).homfly_polynomial(): '8_6',
        Knots().from_table(8,6).mirror_image().homfly_polynomial(): 'm(8_6)',
        Knots().from_table(8,7).homfly_polynomial(): '8_7',
        Knots().from_table(8,7).mirror_image().homfly_polynomial(): 'm(8_7)',
        Knots().from_table(8,8).homfly_polynomial(): '8_8',
        Knots().from_table(8,8).mirror_image().homfly_polynomial(): 'm(8_8)',
        Knots().from_table(8,9).homfly_polynomial(): '8_9',
        Knots().from_table(8,10).homfly_polynomial(): '8_10',
        Knots().from_table(8,10).mirror_image().homfly_polynomial(): 'm(8_10)',
        Knots().from_table(8,11).homfly_polynomial(): '8_11',
        Knots().from_table(8,11).mirror_image().homfly_polynomial(): 'm(8_11)',
        Knots().from_table(8,12).homfly_polynomial(): '8_12',
        Knots().from_table(8,13).homfly_polynomial(): '8_13',
        Knots().from_table(8,13).mirror_image().homfly_polynomial(): 'm(8_13)',
        Knots().from_table(8,14).homfly_polynomial(): '8_14',
        Knots().from_table(8,14).mirror_image().homfly_polynomial(): 'm(8_14)',
        Knots().from_table(8,15).homfly_polynomial(): '8_15',
        Knots().from_table(8,15).mirror_image().homfly_polynomial(): 'm(8_15)',
        Knots().from_table(8,16).homfly_polynomial(): '8_16',
        Knots().from_table(8,16).mirror_image().homfly_polynomial(): 'm(8_16)',
        Knots().from_table(8,17).homfly_polynomial(): '8_17',
        Knots().from_table(8,17).homfly_polynomial(): 'm(8_17)',
        Knots().from_table(8,18).homfly_polynomial(): '8_18',
        Knots().from_table(8,19).homfly_polynomial(): '8_19',
        Knots().from_table(8,19).mirror_image().homfly_polynomial(): 'm(8_19)',
        Knots().from_table(8,20).homfly_polynomial(): '8_20',
        Knots().from_table(8,20).mirror_image().homfly_polynomial(): 'm(8_20)',
        Knots().from_table(8,21).homfly_polynomial(): '8_21',
        Knots().from_table(8,21).mirror_image().homfly_polynomial(): 'm(8_21)',
    }
    

    @classmethod
    def batch_catalog(cls, in_filename, out_filename):
        knot_catalog = dict() 
        in_file = open(in_filename, 'r')
        out_file = open(out_filename, 'w')
        size = int(len(in_file.readline().strip())**(0.5)) #Determining size of mosaics in file
        knot_count = 0

        mosaic = [0]*(size ** 2)
        satisfied = [False]*(size ** 2) #Represents whether all strands in a tile have been traversed
        crossing_number = [0]*(size ** 2) #The number assigned to a crossing in extended gauss code
        gauss_code = []
        crossing_signs = []
        made_connections = [[] for _ in range(size ** 2)]
        crossing_count = 0
        i = 0
        num = 0
        writhe = 0
        up_cusps = 0
        down_cusps = 0
        curr_tile = 0
        starting_tile = None
        face = 0

        while True:    
            mosaic_string = in_file.readline().strip()
            if len(mosaic_string) == 0:
                break
            for char in mosaic_string:
                num = int(char)
                mosaic[i] = num
                satisfied[i] = num == 0
                if starting_tile == None and num != 0:
                    starting_tile = i
                i += 1
            if starting_tile == None:
                continue

            curr_tile = starting_tile
            face = cls.valid_connections[mosaic[curr_tile]][0][0] 
            while curr_tile != starting_tile or not satisfied[curr_tile]:
                for conn in cls.valid_connections[mosaic[curr_tile]]:
                    if conn[0] == face:
                        made_connections[curr_tile].append(conn)
                        if ((len(made_connections[curr_tile]) == 1) and mosaic[curr_tile] < 7) or (len(made_connections[curr_tile]) == 2):
                            satisfied[curr_tile] = True
                        if conn in [(0,3),(1,2)]:
                            down_cusps += 1
                        if conn in [(3,0),(2,1)]:    
                            up_cusps += 1

                        #Logic for crossings
                        if mosaic[curr_tile] == 9:
                            if satisfied[curr_tile]:
                                if conn[0] % 2 == 1: #Over crossing
                                    gauss_code.append(crossing_number[curr_tile])
                                else:
                                    gauss_code.append(-crossing_number[curr_tile])
                                if conn[0] + made_connections[curr_tile][0][0] == 3: #Positive crossing
                                    writhe += 1
                                    crossing_signs[crossing_number[curr_tile]-1] = 1
                                else: #Negative crossing
                                    writhe -= 1
                                    crossing_signs[crossing_number[curr_tile]-1] = -1
                            else:
                                crossing_count += 1
                                crossing_signs.append(0)
                                if conn[0] % 2 == 1:
                                    crossing_number[curr_tile] = crossing_count
                                    gauss_code.append(crossing_count)
                                else:
                                    crossing_number[curr_tile] = crossing_count
                                    gauss_code.append(-crossing_count)
                        face = (conn[1] + 2) % 4 #incoming face for next tile
                        if face == 0: #Left
                            curr_tile -= 1 
                        elif face == 1: #Down
                            curr_tile += size
                        elif face == 2: #Right
                            curr_tile += 1
                        elif face == 3: #Up
                            curr_tile -= size
                        break
            if all(satisfied):
                knot_count += 1
                #First element is smooth knot type (or HOMFLY polynomial if not found), second element is Thurston-Bennquin number, third element is rotation number
                tup = ('0_1' if len(gauss_code) < 3 else (cls.knot_list.get(Link([[gauss_code],crossing_signs]).homfly_polynomial(), Link([[gauss_code],crossing_signs]).homfly_polynomial())), writhe - (up_cusps + down_cusps) // 2, abs(up_cusps - down_cusps) // 2)
                if not tup in knot_catalog:
                    out_file.write(f"{tup[0]} | {tup[1]:>3} | {tup[2]:>3} | {mosaic_string}\n")
                    out_file.flush()
                    knot_catalog[tup] = mosaic_string
        
            #Resetting variables between mosaics
            gauss_code = []
            crossing_signs = []
            for list in made_connections:
                list.clear()
            crossing_count = 0
            i = 0
            num = 0
            writhe = 0
            up_cusps = 0
            down_cusps = 0
            starting_tile = None
        out_file.close()
        print(knot_count)
main()
