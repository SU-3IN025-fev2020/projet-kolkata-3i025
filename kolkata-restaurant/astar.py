import heapq

def h_value(node, goal):
    return abs(node[0]-goal[0]) + abs(node[1]-goal[1])

def astar(size, start, goal, wallStates):
    frontiere = [(h_value(start,goal), 0, start, start)]
    reserve = {}
    best = start

    if start == goal:
        return [goal]

    while frontiere != [] and best != goal:
        (min_f, curr_g, best, parent) = heapq.heappop(frontiere)

        voisins = [(best[0]+x_inc, best[1]+y_inc) for x_inc, y_inc in [(0,1),(0,-1),(1,0),(-1,0)] if ((best[0]+x_inc,best[1]+y_inc) not in wallStates) and best[0]+x_inc>=0 and best[0]+x_inc<=size and best[1]+y_inc>=0 and best[1]+y_inc<=size]
        for node in voisins:
            if node not in reserve.keys():
                heapq.heappush(frontiere, (curr_g+1+h_value(node, goal), curr_g+1, node, best))

        reserve[best] = parent

    path = []; node = goal
    while node != start:
        try:
            path.insert(0, node)
            node = reserve[node]
        except KeyError:
            print("reserve : ", reserve)
            print("start : ", start)
            print("goal : ", goal)
            exit(1)

    return path

