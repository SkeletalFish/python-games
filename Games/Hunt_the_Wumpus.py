import random
import re
import os
import queue
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
    def __init__(self,name=""):
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
            print("Contents: " + contents)
        print(LINE_BREAK)

    def validate(self,verbosity=0):
        ## Must be exactly one Wumpus in a room containing only the Wumpus
        ## Must be exactly one Gold in a room containing only the Gold
        ## Must be exactly one Exit in a room containing only the Exit
        ## Exit must not be connected to any room containing a Pit, the Wumpus or Bats
        ## Must be connected
        ## Wumpus must be reachable from the Exit
        ## Gold must be reachable from the Exit
        ## For every Strongly Connected Component
        ##   Must be at least one empty room
        ##   Bats must be accessible from every empty room (in this or a connected SCC)
        ##   Room containing Bats must only contain Bats

    def edit(self):
        ## map edit/create loop, including validation
        pass

    def load(self,cave_name):
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

    def save(self,cave_name):
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

    def find_exit(self):
        for room_id,room_data in self.rooms.items():
            if EXIT in room_data[ROOM_CONTENTS]:
                break
        return room_id

    def find_wumpus(self):
        for room_id,room_data in self.rooms.items():
            if WUMPUS in room_data[ROOM_CONTENTS]:
                break
        return room_id

    def find_gold(self):
        for room_id,room_data in self.rooms.items():
            if GOLD in room_data[ROOM_CONTENTS]:
                break
        return room_id
    
    def find_bats(self,room_ids=None):
        for room_id,room_data in self.rooms.items():
            if room_ids == None:
                if BATS in room_data[ROOM_CONTENTS]:
                    yield room_id
            else:
                if BATS in room_data[ROOM_CONTENTS] and room_id in room_ids:
                    yield room_id
    
    def find_pits(self,room_ids=None):
        for room_id,room_data in self.rooms.items():
            if room_ids == None:
                if PIT in room_data[ROOM_CONTENTS]:
                    yield room_id
            else:
                if PIT in room_data[ROOM_CONTENTS] and room_id in room_ids:
                    yield room_id

    def render(self,file_name=None,show_player=False,player_location=None):
        if file_name == None:
            file_name = self.name+".gv"
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
        order = [start]
        found = None
        
        q = queue.LifoQueue()
        q.put(start)
        while not q.empty() and found == None:
            node = q.get()
            if item in self.rooms[node][ROOM_CONTENTS]:
                found = node
            else:
                for edge in edges:
                    if edge[0] == node:
                        if BATS in self.rooms[edge[0]][ROOM_CONTENTS]:
                            room_found = False
                            while not room_found:
                                move_to = random.choice(list(self.rooms.keys()))
                                if WUMPUS not in self.rooms[move_to][ROOM_CONTENTS] and PIT not in self.rooms[move_to][ROOM_CONTENTS] and BATS not in self.rooms[move_to][ROOM_CONTENTS]:
                                    room_found = True
                            visited = [move_to]
                            order.append("->")
                            order.append(move_to)
                            q = queue.LifoQueue()
                            q.put(move_to)
                        elif edge[1] not in visited and PIT not in self.rooms[edge[1]][ROOM_CONTENTS]:
                            q.put(edge[1])
                            visited.append(edge[1])
                            order.append(edge[1])
        
        return found,order
    
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
            elif self.status == "carried":
                found = False
                while not found:
                    move_to = random.choice(list(self.cave.rooms.keys()))
                    if WUMPUS not in self.cave.rooms[move_to][ROOM_CONTENTS] and PIT not in self.cave.rooms[move_to][ROOM_CONTENTS] and BATS not in self.cave.rooms[move_to][ROOM_CONTENTS]:
                        found = True
                        self.move(move_to)
        
                
if __name__ == "__main__":
    while True:
        cave = CaveSystem()
        #cave.add_room(1)
        #cave.add_room(2)
        #cave.add_room(3)
        #cave.add_room(4)
        #cave.add_room(5)
        #cave.add_room(6)
        #cave.add_tunnel(1,2,True)
        ##cave.add_tunnel(1,4)
        #cave.add_tunnel(4,5)
        ##cave.add_tunnel(2,3,True)
        #cave.add_tunnel(2,3)
        ##cave.add_tunnel(3,1,True)
        #cave.add_tunnel(1,6)
        #cave.add_tunnel(6,4)
        #cave.add_contents(BATS,3)
        #cave.add_contents(GOLD,4)
        #cave.add_contents(WUMPUS,5)
        #cave.add_contents(EXIT,1)
        #cave.add_contents(PIT,6)
        #cave.load("test_cave")
        #cave.save("test_cave")
        #cave.load("cave_1")
        for i in range(1,21):
            cave.add_room(i)
        cave.add_tunnel(1,2)
        cave.add_tunnel(1,5)
        cave.add_tunnel(1,6)
        cave.add_tunnel(2,8)
        cave.add_tunnel(2,3)
        cave.add_tunnel(3,10)
        cave.add_tunnel(3,4)
        cave.add_tunnel(4,12)
        cave.add_tunnel(4,5)
        cave.add_tunnel(5,14)
        cave.add_tunnel(6,7)
        cave.add_tunnel(7,8)
        cave.add_tunnel(8,9)
        cave.add_tunnel(9,10)
        cave.add_tunnel(10,11)
        cave.add_tunnel(11,12)
        cave.add_tunnel(12,13)
        cave.add_tunnel(13,14)
        cave.add_tunnel(14,15)
        cave.add_tunnel(15,6)
        cave.add_tunnel(7,17)
        cave.add_tunnel(9,18)
        cave.add_tunnel(11,19)
        cave.add_tunnel(13,20)
        cave.add_tunnel(15,16)
        cave.add_tunnel(16,17)
        cave.add_tunnel(17,18)
        cave.add_tunnel(18,19)
        cave.add_tunnel(19,20)
        cave.add_tunnel(16,20)
        cave_ok = False
        attempt = 0
        print("Attempting to Generate Cave Contents...")
        while not cave_ok:
            attempt += 1
            print("Attempt:",attempt)
            cave.add_contents(EXIT,random.randint(1,20))
            room_ok = False
            while not room_ok:
                test_room = random.randint(1,20)
                if cave.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in cave.rooms[test_room][ROOM_LINKS]:
                        if cave.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        room_ok = True
                        cave.add_contents(WUMPUS,test_room)
            room_ok = False
            while not room_ok:
                test_room = random.randint(1,20)
                if cave.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in cave.rooms[test_room][ROOM_LINKS]:
                        if cave.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        room_ok = True
                        cave.add_contents(GOLD,test_room)
            rooms_left = list(range(1,21))
            counter = 0
            while rooms_left != [] and counter < 4:
                test_room = random.choice(rooms_left)
                rooms_left.remove(test_room)
                if cave.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in cave.rooms[test_room][ROOM_LINKS]:
                        if cave.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        cave.add_contents(PIT,test_room)
                        counter += 1
            rooms_left = list(range(1,21))
            counter = 0
            while rooms_left != [] and counter < 2:
                test_room = random.choice(rooms_left)
                rooms_left.remove(test_room)
                if cave.rooms[test_room][ROOM_CONTENTS] == []:
                    link_ok = True
                    for link in cave.rooms[test_room][ROOM_LINKS]:
                        if cave.rooms[link][ROOM_CONTENTS] != []:
                            link_ok = False
                    if link_ok:
                        cave.add_contents(BATS,test_room)
                        counter += 1

            cave_ok = cave.validate(0)
        print("Attempt Successful")
        cave.save("cave_1")
        #cave.display() # Only if debug
        #cave.render() # Only if debug
        #validation = cave.validate(3) # Only if debug
        validation = cave.validate(2) # Only if not debug
        run_game = False
        for each in validation:
            if isinstance(each,str):
                print(each)
        if each == True:
            run_game = True
        if run_game:
            player = Player(cave.find_exit(),cave)
            step_number = 0
            #cave.render(cave.name+"_"+str(step_number)+".gv",True,player.location) # Only if debug
            step_number += 1
            player.display_info()
            while player.status == "alive":
                player.choose_action()
                #cave.render(cave.name+"_"+str(step_number)+".gv",True,player.location) # Only if debug
                step_number += 1
                player.display_info()
        input("Press enter to start again, Ctrl-C to quit")
