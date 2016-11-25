import random
import re
import os
import queue
# Make graphviz optional
try:
    from graphviz import Digraph
except ImportError:
    Digraph = False

ROOM_CONTENTS = 0
ROOM_LINKS = 1
ROOM_REVERSED = 2
ROOM_VISITED = 3
WUMPUS = "Wumpus"
PIT = "Pit"
GOLD = "Gold"
ARROW = "Arrow"
EXIT = "Exit"
BATS = "Bats"
SECTION_BREAK = "###############################################################"
LINE_BREAK = "==============================================================="
FILE_PATH = os.path.dirname(__file__)

def yesno(prompt):
    input_ok = False
    while input_ok == False:
        output = input(prompt)
        output = output.upper()
        if output == "Y" or output == "N":
            input_ok = True
        else:
            print("Please enter Y or N.")
    return output

def transpose(cave):
    for room_id,room_data in cave.items():
        for link in room_data[ROOM_LINKS]:
            cave[link][ROOM_REVERSED].append(room_id)
    return cave

def connected(cave,room_id,reverse=False):
    cave[room_id][ROOM_VISITED] = True
    if not reverse:
        for link in cave[room_id][ROOM_LINKS]:
            if cave[link][ROOM_VISITED] == False:
                cave = connected(cave,link,reverse)
        return cave
    if reverse:
        for link in cave[room_id][ROOM_REVERSED]:
            if cave[link][ROOM_VISITED] == False:
                cave = connected(cave,link,reverse)
        return cave

def reset_visited(cave):
    for room_id,room_data in cave.items():
        room_data[ROOM_VISITED] = False
    return cave

def create_graph(rooms):
    V = []
    E = []
    for room_id,room_data in rooms.items():
        V.append(room_id)
        for link in room_data[ROOM_LINKS]:
            edge = (room_id,link)
            E.append(edge)
    graph = (V,E)
    return graph

def scc(graph):
    ## See Kosaraju's Algorithm
    vertices = graph[0]
    edges = graph[1]
    visited = []
    L = []
    components = {}

    def recur_visit(vertex):
        if vertex not in visited:
            visited.append(vertex)
            for edge in edges:
                if edge[0] == vertex:
                    recur_visit(edge[1])
            L.append(vertex)

    def recur_assign(u,root):
        found = False
        for id,component in components.items():
            if u in component:
                found = True
        if not found:
            if root not in components:
                components[root] = []
            components[root].append(u)
            for edge in edges:
                if edge[1] == u:
                    recur_assign(edge[0],root)
    
    for vertex in vertices:
        recur_visit(vertex)

    i = 0
    for each in reversed(L):
        i+=1
        recur_assign(each,each)

    return components
        
class Main():
    def __init__(self):
        print("Main Loop Under Construction")
        print("Run Game from \\Games\\Hunt_the_Wumpus.py")
    ## Introduction
    ## Game mode selection
    ##  Map Selection
    ##   Create New
    ##   Load Existing
    ## Game play loop

class CaveSystem():
    def __init__(self,name=None):
        self.rooms = {}
        self.name = name
        
    def add_room(self,id):
        self.rooms[id] = [[],[]]
        
    def remove_room(self,id):
        self.remove_tunnel(id)
        del self.rooms[id]
        
    def get_room(self,id=None):
        if id == None:
            return self.rooms
        else:
            return self.rooms[id]
        
    def add_tunnel(self,parent_id,child_id,one_way=False):
        if child_id not in self.rooms[parent_id][ROOM_LINKS]:
           self.rooms[parent_id][ROOM_LINKS].append(child_id)
        if not one_way:
            if parent_id not in self.rooms[child_id][ROOM_LINKS]:
                self.rooms[child_id][ROOM_LINKS].append(parent_id)
            
    def remove_tunnel(self,parent_id,child_id=None,one_way=False):
        if child_id == None:
            for key in self.rooms:
                if parent_id in self.rooms[key][ROOM_LINKS]:
                    self.rooms[key][ROOM_LINKS].remove(parent_id)
        else:
            self.rooms[parent_id][ROOM_LINKS].remove(child_id)
            self.rooms[child_id][ROOM_LINKS].remove(parent_id)
            
    def get_tunnel(self,id=None):
        if id != None:
            return self.rooms[id][ROOM_LINKS]
        else:
            for key in self.rooms:
                for room in self.rooms[key][ROOM_LINKS]:
                    yield [key,room]

    def add_contents(self,item,room_id):
        self.rooms[room_id][ROOM_CONTENTS].append(item)

    def remove_contents(self,item,room_id):
        if item in self.rooms[room_id][ROOM_CONTENTS]:
            self.rooms[room_id][ROOM_CONTENTS].remove(item)
            
    def display(self):
        print(LINE_BREAK)
        if self.name == "":
            print("Unnamed Cave")
        else:
            print("Name:",self.name)
        for room_id,room_data in self.rooms.items():
            print(LINE_BREAK)
            print("Room ID:",room_id)
            output = ""
            links = ""
            for link in room_data[ROOM_LINKS]:
                links += str(link)+", "
            links = links[:-2]
            print("Links To: " + links)
            contents = ""
            for item in room_data[ROOM_CONTENTS]:
                contents += str(item)+", "
            contents = contents[:-2]
            if contents == "":
                contents = "Empty"
            print("Contents: " + contents)
        print(LINE_BREAK)

    def validate(self,verbosity=0):
        ## verbosity = 0 -> Output boolean 'valid'
        ##           = 1 -> Output 'Map Failed' error and boolean 'valid' 
        ##           = 2 -> Output all errors or 'Map Ok' and boolean 'valid'
        ##           = 3 -> Output all
        
        valid = True
        
        ## Add visited status
        ## Transpose graph
        cave_1 = self.rooms
        for room_id,room_data in cave_1.items():
            room_data.append([])
            room_data.append(False)
        cave_1 = transpose(cave_1)
        
        wumpus_status = 0
        gold_status = 0
        exit_status = 0
        bat_status = 0
        failed_partitions = []
        
        for room_id,room_data in self.rooms.items():
            ## Must be exactly one Wumpus in a room containing only the Wumpus
            if room_data[ROOM_CONTENTS] == [WUMPUS] and wumpus_status == 0:
                wumpus_status = 1
            elif room_data[ROOM_CONTENTS] == [WUMPUS] and wumpus_status >= 1:
                wumpus_status = 2
            elif WUMPUS in room_data[ROOM_CONTENTS] and room_data[ROOM_CONTENTS] != [WUMPUS]:
                wumpus_status = 3

            ## Must be exactly one Gold in a room containing only the Gold
            if room_data[ROOM_CONTENTS] == [GOLD] and gold_status == 0:
                gold_status = 1
            elif room_data[ROOM_CONTENTS] == [GOLD] and gold_status >= 1:
                gold_status = 2
            elif GOLD in room_data[ROOM_CONTENTS] and room_data[ROOM_CONTENTS] != [GOLD]:
                gold_status = 3
                
            ## Must be exactly one Exit in a room containing only the Exit
            if room_data[ROOM_CONTENTS] == [EXIT] and exit_status == 0:
                exit_status = 1
            elif room_data[ROOM_CONTENTS] == [EXIT] and exit_status >= 1:
                exit_status = 2
            elif EXIT in room_data[ROOM_CONTENTS] and room_data[ROOM_CONTENTS] != [EXIT]:
                exit_status = 3

            ## Room containing Bats must only contain Bats
            if room_data[ROOM_CONTENTS] == [BATS] and bat_status == 0:
                bat_status = 1
            elif BATS in room_data[ROOM_CONTENTS] and room_data[ROOM_CONTENTS] != [BATS]:
                bat_status = 2
                
        ## Exit must not be connected to any room containing a Pit, the Wumpus or Bats
        if exit_status == 1:
            room_ok = True
            room_check = list(self.find_items([EXIT],False))[0]
            for link in self.rooms[room_check][ROOM_LINKS]:
                if PIT in self.rooms[link][ROOM_CONTENTS] or WUMPUS in self.rooms[link][ROOM_CONTENTS] or BATS in self.rooms[link][ROOM_CONTENTS]:
                    room_ok = False
            if not room_ok:
                exit_status = 4
        
        ## Must be connected
        is_connected = False
        for room_id in cave_1:
            cave_1 = reset_visited(cave_1)
            check = connected(cave_1,room_id,False)
            temp_connected = True
            for room_id,room_data in check.items():
                if room_data[ROOM_VISITED] == False:
                    temp_connected = False
            if temp_connected == True:
                is_connected = True
                break

        partitions = None
        if is_connected:
            partitions = scc(create_graph(self.rooms))
        ## For every Strongly Connected Component if more than one
            if len(partitions) > 1:
                for root_id,partition in partitions.items():
                    ##   Must be at least one empty room
                    ids_empty = list(self.find_items([],True,partition))
                    gold_loc = self.find_items([GOLD,ARROW,EXIT],False,partition)
                    if gold_loc != None:
                        ids_empty += gold_loc
                    if len(ids_empty) == 0:
                        if [partition,"Fail - No Empty rooms"] not in failed_partitions:
                            failed_partitions.append([partition,"Fail - No Empty rooms"])
                    else:
                        ##   Bats must be accessible from every empty room (in this or a connected SCC)
                        for room_id in partition:
                            test = self.df_walk(room_id,BATS)
                            if test == False:
                                if [partition,"Fail - Unable to reach Bats from room_id "+str(room_id)] not in failed_partitions:
                                    failed_partitions.append([partition,"Fail - Unable to reach Bats from room_id "+str(room_id)])
                        
            
        ## Wumpus must be reachable from the Exit
        ## Gold must be reachable from the Exit
        check_wumpus = self.df_walk(list(self.find_items([EXIT],False))[0],WUMPUS)
        check_gold = self.df_walk(list(self.find_items([EXIT],False))[0],GOLD)

        ## return error statements
        if wumpus_status == 0:
            if verbosity >= 2: yield "Fail - No Wumpus found"
            valid = False
        elif wumpus_status == 1:
            if verbosity >= 3: yield "Pass - Wumpus Ok"
        elif wumpus_status == 2:
            if verbosity >= 2: yield "Fail - More than one Wumpus found"
            valid = False
        elif wumpus_status == 3:
            if verbosity >= 2: yield "Fail - Wumpus not alone in room"
            valid = False
            
        if gold_status == 0:
            if verbosity >= 2: yield "Fail - No Gold found"
            valid = False
        elif gold_status == 1:
            if verbosity >= 3: yield "Pass - Gold Ok"
        elif gold_status == 2:
            if verbosity >= 2: yield "Fail - More than one Gold found"
            valid = False
        elif gold_status == 3:
            if verbosity >= 2: yield "Fail - Gold not alone in room"
            valid = False
            
        if exit_status == 0:
            if verbosity >= 2: yield "Fail - No Exit found"
            valid = False
        elif exit_status == 1:
            if verbosity >= 3: yield "Pass - Exit Ok"
        elif exit_status == 2:
            if verbosity >= 2: yield "Fail - More than one Exit found"
            valid = False
        elif exit_status == 3:
            if verbosity >= 2: yield "Fail - Exit not alone in room"
            valid = False
        elif exit_status == 4:
            if verbosity >= 2: yield "Fail - Exit next to hazard"
            valid = False
            
        if bat_status == 0:
            pass # No bats
        elif bat_status == 1:
            if verbosity >= 3: yield "Pass - Bats alone in room"
        elif bat_status == 2:
            if verbosity >= 2: yield "Fail - Bats not alone in room"
            valid = False

        if is_connected:
            if verbosity >= 3: yield "Pass - Connected"
        else:
            if verbosity >= 2: yield "Fail - Not Connected"
            valid = False

        if partitions != None:
            if len(partitions) > 1:
                if len(failed_partitions) == 0:
                    if verbosity >= 3: yield "Pass - Partitions Ok"
                else:
                    for each in failed_partitions:
                        if verbosity >= 2: yield str(each[1])+" in Partition "+str(each[0])
                    valid = False
                    
        if check_wumpus == None:
            valid = False
            if verbosity >= 2: yield "Unable to reach Wumpus"
        else:
            if verbosity >= 3: yield "Wumpus reached in room " + str(check_wumpus)
            
        if check_gold == None:
            valid = False
            if verbosity >= 2: yield "Unable to reach Gold"
        else:
            if verbosity >= 3: yield "Gold reached in room " + str(check_gold)

        if valid == True:
            if verbosity >= 2: yield "Pass - Map Ok"
        else:
            if verbosity >= 1: yield "Fail - Map Not Ok"

        if verbosity >= 0: yield valid

    def edit(self):
        ## map edit/create loop, including validation
        pass

    def load(self,cave_name=None):
        if cave_name == None:
            cave_name = self.name
            if self.name == None:
                raise Exception("Error - Cave has no name")
        ## import map saved in .txt format, including validation
        f = open(FILE_PATH + "\\Data\\Wumpus\\Maps\\" + cave_name + ".txt","r")
        for line in f:
            temp = line.split(";")
            temp_id = temp[0]
            self.add_room(int(temp_id))
        f.close()
            
        f = open(FILE_PATH + "\\Data\\Wumpus\\Maps\\" + cave_name + ".txt","r")
        for line in f:
            temp = line.split(";")
            temp_id = temp[0]
            try:
                temp_links = temp[1]
            except:
                temp_links = ""
            try:
                temp_contents = temp[2]
            except:
                temp_contents = ""
            temp_links = temp_links.split(",")
            temp_contents = temp_contents.split(",")
            for link in temp_links:
                self.add_tunnel(int(temp_id),int(link))
            for item in temp_contents:
                self.add_contents(item.strip("\n"),int(temp_id))
        f.close()
        
        self.name = cave_name

    def save(self,cave_name=None):
        if cave_name == None:
            cave_name = self.name
            if self.name == None:
                raise Exception("Error - Cave has no name")
        ## save map as .txt
        f = open(FILE_PATH + "\\Data\\Wumpus\\Maps\\" + cave_name + ".txt","w")
        for room_id,room_data in self.rooms.items():
            file_line = str(room_id) + ";"
            for link in room_data[ROOM_LINKS]:
                file_line += str(link) + ","
            file_line = file_line[:-1]
            file_line += ";"
            for item in room_data[ROOM_CONTENTS]:
                if item != ARROW:
                    file_line += str(item) + ","
            file_line = file_line[:-1]
            file_line += "\n"
            f.write(file_line)
        f.close()
        self.name = cave_name

    def find_items(self,items,exact=True,room_ids=None):
        if room_ids == None:
            room_list = self.rooms.keys()
        else:
            room_list = room_ids
        for room_id in room_list:
            if exact:
                if self.rooms[room_id][ROOM_CONTENTS] == items:
                    yield room_id
            else:
                for item in self.rooms[room_id][ROOM_CONTENTS]:
                    if item in items:
                        yield room_id
                        break
                    
    def render(self,file_name=None,show_player=False,player_location=None):
        if file_name == None:
            file_name = FILE_PATH + "\\Data\\Wumpus\\Screens\\" + self.name+".gv"
        if Digraph:
            dot = Digraph(comment=self.name)
            for room_id,room_data in self.rooms.items():
                cont = ""
                for item in room_data[ROOM_CONTENTS]:
                    cont += item+", "
                if show_player and room_id == player_location:
                    cont += "Player, "
                if cont == "":
                    cont = "Empty, "
                cont = cont[:-2]
                dot.node(str(room_id),str(room_id)+"\n"+str(cont))
            for room_id,room_data in self.rooms.items():
                for link in room_data[ROOM_LINKS]:
                    dot.edge(str(room_id),str(link))
            dot.render(file_name,view=True)
        else:
            print("Graphviz not installed")

    def df_walk(self,start,item):
        graph = create_graph(self.rooms)
        vertices = graph[0]
        edges = graph[1]
        visited = [start]
        order = []
        found = None
        
        q = queue.LifoQueue()
        q.put(start)
        while not q.empty() and found == None:
            node = q.get()
            order.append(node)
            if item in self.rooms[node][ROOM_CONTENTS]:
                found = node
            else:
                for edge in edges:
                    if edge[0] == node:
                        if BATS in self.rooms[edge[0]][ROOM_CONTENTS]:
                            room_found = False
                            move_to = self.carry(edge[0])
                            visited = [move_to]
                            order.append("->")
                            q = queue.LifoQueue()
                            q.put(move_to)
                        elif edge[1] not in visited and PIT not in self.rooms[edge[1]][ROOM_CONTENTS]:
                            q.put(edge[1])
                            visited.append(edge[1])
        return found,order

    def add_rooms(self,count):
        for i in range(1,count+1):
            self.add_room(i)

    def add_random_contents(self,verbose=True):
        cave_ok = False
        attempt = 0
        if verbose: print("Attempting to Generate Cave Contents...")
        while not cave_ok:
            attempt += 1
            if verbose: print("Attempt:",attempt)
            self.add_contents(EXIT,random.randint(1,20))
            room_ok = False
            while not room_ok:
                test_room = random.randint(1,20)
                if self.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in self.rooms[test_room][ROOM_LINKS]:
                        if self.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        room_ok = True
                        self.add_contents(WUMPUS,test_room)
            room_ok = False
            while not room_ok:
                test_room = random.randint(1,20)
                if self.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in self.rooms[test_room][ROOM_LINKS]:
                        if self.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        room_ok = True
                        self.add_contents(GOLD,test_room)
            rooms_left = list(range(1,21))
            counter = 0
            while rooms_left != [] and counter < 4:
                test_room = random.choice(rooms_left)
                rooms_left.remove(test_room)
                if self.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in self.rooms[test_room][ROOM_LINKS]:
                        if self.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        self.add_contents(PIT,test_room)
                        counter += 1
            rooms_left = list(range(1,21))
            counter = 0
            while rooms_left != [] and counter < 2:
                test_room = random.choice(rooms_left)
                rooms_left.remove(test_room)
                if self.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in self.rooms[test_room][ROOM_LINKS]:
                        if self.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        self.add_contents(BATS,test_room)
                        counter += 1

            cave_ok = self.validate(0)
        if verbose: print("Attempt Successful")

    def carry(self,cur_location):
        found = False
        while not found:
            partitions = scc(create_graph(self.rooms))
            if len(partitions) > 1:
                temp = partitions.copy()
                print(temp)
                print(partitions)
                for partition_root,partition in partitions.items():
                    if cur_location in partition:
                        del temp[partition_root]
                room_list = []
                for partition_root,partition in temp.items():
                    room_list += partition
            else:
                for partition_root,partition in partitions.items():
                    room_list += partition
            move_to = random.choice(room_list)
            if WUMPUS not in self.rooms[move_to][ROOM_CONTENTS] and PIT not in self.rooms[move_to][ROOM_CONTENTS] and BATS not in self.rooms[move_to][ROOM_CONTENTS]:
                found = True
                return move_to

    def build_preset(self,preset_name=None,verbose=True):
        if preset_name == None:
            preset_name = self.name
            if self.name == None:
                raise Exception("Error - Cave has no name")
        if preset_name == "dodecahedron":
            cave.name = preset_name
            print("Building Preset '"+preset_name+"'")
            self.add_rooms(20)
            self.add_tunnel(1,2)
            self.add_tunnel(1,5)
            self.add_tunnel(1,6)
            self.add_tunnel(2,8)
            self.add_tunnel(2,3)
            self.add_tunnel(3,10)
            self.add_tunnel(3,4)
            self.add_tunnel(4,12)
            self.add_tunnel(4,5)
            self.add_tunnel(5,14)
            self.add_tunnel(6,7)
            self.add_tunnel(7,8)
            self.add_tunnel(8,9)
            self.add_tunnel(9,10)
            self.add_tunnel(10,11)
            self.add_tunnel(11,12)
            self.add_tunnel(12,13)
            self.add_tunnel(13,14)
            self.add_tunnel(14,15)
            self.add_tunnel(15,6)
            self.add_tunnel(7,17)
            self.add_tunnel(9,18)
            self.add_tunnel(11,19)
            self.add_tunnel(13,20)
            self.add_tunnel(15,16)
            self.add_tunnel(16,17)
            self.add_tunnel(17,18)
            self.add_tunnel(18,19)
            self.add_tunnel(19,20)
            self.add_tunnel(16,20)
            self.add_random_contents(verbose)
        elif preset_name == "debug1":
            cave.name = preset_name
            self.add_room(1)
            self.add_room(2)
            self.add_room(3)
            self.add_room(4)
            self.add_room(5)
            self.add_room(6)
            self.add_tunnel(1,2,True)
            self.add_tunnel(1,4)
            self.add_tunnel(4,5)
            self.add_tunnel(2,3,True)
            self.add_tunnel(2,3)
            self.add_tunnel(6,4)
            self.add_contents(BATS,3)
            self.add_contents(GOLD,4)
            self.add_contents(WUMPUS,5)
            self.add_contents(EXIT,1)
            self.add_contents(PIT,6)
        else:
            print("Error - Preset '"+preset_name+"' not found")        
    
class Player():
    def __init__(self,room_id,cave):
        self.location = room_id
        self.gold = False
        self.arrows = 1
        self.cave = cave
        self.links = self.cave.rooms[self.location][ROOM_LINKS]
        self.room = self.cave.rooms[self.location][ROOM_CONTENTS]
        self.status = "alive"
        self.wumpus_killed = False
        
    def choose_action(self):
        print("Choose an action:")
        print("'shoot <room_id>', 'grab <gold/arrow>', 'drop', 'move <room_id>'")
        input_ok = False
        while not input_ok:
            action = input("")
            if re.match("(shoot\s)(\d\d*)",action):
                move = int(re.match("(shoot\s)(\d*)",action).group(2))
                if move in self.links:
                    input_ok = True
                    self.shoot(move)
                else:
                    print("Invalid input")
            elif re.match("(grab\s)(\w\w*)",action):
                move = re.match("(grab\s)(\w*)",action).group(2)
                if move == "gold":
                    input_ok = True
                    self.grab(GOLD)
                elif move == "arrow":
                    input_ok = True
                    self.grab(ARROW)
                else:
                    print("Invalid input")
            elif action == "drop":
                self.drop()
                input_ok = True
            elif re.match("(move\s)(\d\d*)",action):
                move = int(re.match("(move\s)(\d*)",action).group(2))
                if move in self.links:
                    input_ok = True
                    self.move(move)
                else:
                    print("Invalid input")
            else:
                print("Invalid input")
                
    def move(self,room_id):
        if room_id in self.cave.rooms:
            old_room = self.location
            new_room = room_id
            self.links = self.cave.rooms[self.location][ROOM_LINKS]
            self.room = self.cave.rooms[self.location][ROOM_CONTENTS]
            self.location = room_id
            self.links = self.cave.rooms[self.location][ROOM_LINKS]
            self.room = self.cave.rooms[self.location][ROOM_CONTENTS]
            if self.status != "carried":
                if old_room in self.cave.rooms[new_room][ROOM_LINKS]:
                    print("You walked into room",room_id)
                else:
                    print("You dropped into room",room_id)
            else:
                print("Bats carried you to room",room_id)
            self.update_status()
        else:
            print("Invalid room id",room_id)

    def grab(self,item):
        if item in self.room:
            if item == GOLD:
                print("You picked up a sack of gold")
                self.gold = True
            if item == ARROW:
                print("You picked up an arrow")
                self.arrows += 1
            self.cave.remove_contents(item,self.location)
        else:
            print("You did not find anything")
        self.update_status()

    def drop(self):
        if self.gold:
            print("Yout dropped a sack of gold")
            self.cave.add_contents(GOLD,self.location)
        else:
            print("You are not carrying any gold")
        self.update_status()

    def shoot(self,room_id):
        if self.arrows == 0:
            print("You have no arrows")
        else:
            self.arrows -= 1
            print("You fire an arrow")
            if WUMPUS in self.cave.rooms[room_id][ROOM_CONTENTS]:
                print("You hear a scream")
                self.wumpus_killed = True
                self.cave.remove_contents(WUMPUS,room_id)
            else:
                print("Nothing happens")
                self.cave.add_contents(ARROW,room_id)
        self.update_status()

    def display_info(self):
        self.update_status(False)
        if self.status == "alive":
            print(SECTION_BREAK)
            print("You are in room",self.location)
            available = ""
            for each in self.links:
                available += str(each)+", "
            available = available[:-2]
            temp = available.rsplit(", ",1)
            available = " & ".join(temp)
            if len(self.links) == 1:
                print("You can move to room",available)
            elif len(self.links) == 0:
                print("You are unable to move")
            else:
                print("You can move to rooms",available)
            if self.gold:
                print("You are carrying a sack of gold")
            else:
                print("You have not found any gold")
            if self.arrows == 0:
                print("You have no arrows remaining")
            elif self.arrows == 1:
                print("You have 1 arrow left")
            else:
                print("You have",self.arrows,"arrows left")
            if GOLD in self.room:
                print("You see a glitter")
            if EXIT in self.room:
                print("You see a light")
            if ARROW in self.room:
                print("You see an arrow in the floor")
            found_bats = False
            found_pit = False
            found_wumpus = False
            for id,data in self.cave.rooms.items():
                if id in self.links and BATS in data[ROOM_CONTENTS] and found_bats == False:
                    print("You hear flapping")
                    found_bats = True
                if id in self.links and PIT in data[ROOM_CONTENTS] and found_pit == False:
                    print("You feel a breeze")
                    found_pit = True
                if id in self.links and WUMPUS in data[ROOM_CONTENTS] and found_wumpus == False:
                    print("You smell a wumpus")
                    found_wumpus = True
            print(LINE_BREAK)

    def get_status(self):
        return self.status

    def update_status(self,verbose=True):
        self.links = self.cave.rooms[self.location][ROOM_LINKS]
        self.room = self.cave.rooms[self.location][ROOM_CONTENTS]
        if WUMPUS in self.room and self.gold:
            self.status = "eaten"
        elif WUMPUS in self.room and not self.gold:
            wumpus_action = random.choice(self.links + ["stay"])
            if wumpus_action != "stay":
                self.cave.remove_contents(WUMPUS,self.location)
                self.cave.add_contents(WUMPUS,wumpus_action)
                self.status = "alive"
            else:
                self.status = "eaten"
        elif PIT in self.room:
            self.status = "pit"
        elif EXIT in self.room and self.gold and self.wumpus_killed:
            self.status = "escaped"
        elif BATS in self.room:
            self.status = "carried"
        else:
            found_wumpus = False
            for id,data in self.cave.rooms.items():
                if id in self.links and WUMPUS in data[ROOM_CONTENTS] and found_wumpus == False:
                    found_wumpus = True
            if found_wumpus and self.gold:
                self.status = "jumped"
            else:
                self.status = "alive"
        if verbose:
            if self.status == "eaten":
                print("You have been eaten by the wumpus")
            elif self.status == "jumped":
                print("The wumpus jumped on you")
            elif self.status == "pit":
                print("You have fallen in a pit")
            elif self.status == "escaped":
                print("You have killed the Wumpus and escaped with the gold")
        if self.status == "carried":
            # Carry player to empty room in a different partition
            self.move(self.cave.carry(self.location))
                
if __name__ == "__main__":
    while True:
        cave = CaveSystem("debug1")
        cave.build_preset()
        cave.save()
        cave.display() # Only if debug
        cave.render() # Only if debug
        validation = cave.validate(3) # Only if debug
        #validation = cave.validate(2) # Only if not debug
        run_game = False
        for each in validation:
            if isinstance(each,str):
                print(each)
        if each == True:
            run_game = True
        if run_game:
            player = Player(list(cave.find_items([EXIT],False))[0],cave)
            step_number = 0
            cave.render(cave.name+"_"+str(step_number)+".gv",True,player.location) # Only if debug
            step_number += 1
            player.display_info()
            while player.status == "alive":
                player.choose_action()
                cave.render(cave.name+"_"+str(step_number)+".gv",True,player.location) # Only if debug
                step_number += 1
                player.display_info()
        input("Press enter to start again, Ctrl-C to quit")
