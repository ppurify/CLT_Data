import pandas as pd
import matplotlib.pyplot as plt
import os
import re
#Display the DataFrame to the user
from IPython.display import display

class Container:
    number = -1
    def __init__(self, idx, seq, group, emerg, weight):
        Container.number += 1
        self.number = Container.number
        self.idx = idx  # 입력 순서
        self.weight = weight
        self.emerg = emerg
        self.seq = seq
        self.newValue = (weight if emerg == 0 else 24 + weight)
        self.level = 0   # container 의 level
        self.row = 0     # 정답 행
        self.col = 0     # stack 번호 정답 열
        self.group = group
        self.order = 0   # 정렬 되었을 때 순서      
        self.fit = False  # 기본값 False
        self.relocation_count = 0  # Relocation count initialized to 0
    def __str__(self):
        return "("+str(self.number)+","+str(self.newValue)+","+str(self.level)+")"

class Stack:
    def __init__(self, capacity):
        self.capacity = capacity
        self.array = [None] * self.capacity
        self.top = -1
    def is_full(self):
        return self.top == self.capacity - 1
    def push(self, idx):
        if not self.is_full():
            self.top += 1            
            self.array[self.top] = idx            
        else:
            print("full")
    def is_empty(self):
        return self.top == -1
    def pop(self):
        if not self.is_empty():
            self.top -= 1
            x = self.array[self.top + 1]
            self.array[self.top + 1] = None
            return x
    def below(self):
        return self.top
    def peek(self):
        if not self.is_empty():
            return self.array[self.top]
        else:
            return None
    def size(self):
        return self.top + 1

# Function to check if a stack can accept a new container
def can_place_in_stack(x, _num_rows, _initial_bay):
    false_count = 0
    for y in range(_num_rows):
        if _initial_bay[y][x] is not None and not _initial_bay[y][x].fit:
            false_count += 1
        if false_count >= 3:
            return False
    return True

# Function to move a container to a new position and update its fit status
def move_container_and_update_fit(container, new_position, _initial_bay, _lvlPlace):
    old_y, old_x = container.row, container.col
    new_y, new_x = new_position

    # Update initial_bay
    _initial_bay[old_y][old_x] = None
    _initial_bay[new_y][new_x] = container

    # Update container's position
    container.row = new_y
    container.col = new_x

    # Increment relocation count
    container.relocation_count += 1

    # Update fit status if the new position matches one in lvlPlace
    level = container.level
    if [new_x, new_y] in _lvlPlace[level]:
        container.fit = True

    # Print the move
    print(f"Moved container {int(container.idx)} from ({old_x}, {old_y}) to ({new_x}, {new_y}) with fit={container.fit}")

    # Print the updated bay state
    print_bay_state(_initial_bay)

# Function to find the new position for a container
def find_new_position(container, _initial_bay, _num_rows, _num_cols):
    level = container.level
    current_x = container.col

    # Find available positions based on the level
    if 1 <= level <= 4:
        for x in range(0, current_x):
            if _initial_bay[_num_rows - 1][x] is not None and not _initial_bay[_num_rows - 1][x].fit:
                continue
            for y in range(_num_rows):
                if _initial_bay[y][x] is None and can_place_in_stack(x, _num_rows, _initial_bay):
                    return (y, x)
    elif 5 <= level <= 9:
        for x in range(_num_cols - 1, current_x, -1):
            if _initial_bay[_num_rows - 1][x] is not None and not _initial_bay[_num_rows - 1][x].fit:
                continue
            for y in range(_num_rows):
                if _initial_bay[y][x] is None and can_place_in_stack(x, _num_rows, _initial_bay):
                    return (y, x)
    return None

# Function to move a container
def move_container(container, _initial_bay, _lvlPlace, _num_rows, _num_cols):
    new_position = find_new_position(container, _initial_bay, _num_rows, _num_cols)
    if new_position:
        move_container_and_update_fit(container, new_position, _initial_bay, _lvlPlace)

# Function to print the current bay state
def print_bay_state(_initial_bay):
    print("\nCurrent Bay State:")
    for i in range(len(_initial_bay) - 1, -1, -1):
        for j in range(len(_initial_bay[i])):
            if _initial_bay[i][j] is not None:
                container = _initial_bay[i][j]
                print(f"({int(container.idx)},{container.level},{container.fit})", end=" | ")
            else:
                print("Empty", end=" | ")
        print()

# Function to print the final bay state
def print_final_bay_state(_real_bay):
    print("\nFinal Bay State (real_bay):")
    for i in range(len(_real_bay) - 1, -1, -1):
        for j in range(len(_real_bay[i])):
            if _real_bay[i][j] is not None:
                container = _real_bay[i][j]
                print(f"({int(container.idx)},{container.level},{container.fit})", end=" | ")
            else:
                print("Empty", end=" | ")
        print()

# Function to move top false containers to a valid position based on new_lvlPlace
def move_top_false_containers(_num_rows, _num_cols, _real_bay, _new_lvlPlace, _initial_bay):
    while True:
        moved = False
        for x in range(_num_cols):
            for y in range(_num_cols - 1, -1, -1):
                if _real_bay[y][x] is not None:
                    container = _real_bay[y][x]
                    if y+1 >= _num_cols or _real_bay[y+1][x] is None:
                        if not container.fit:
                            level = container.level
                            if _new_lvlPlace[level]:
                                for pos in _new_lvlPlace[level]:
                                    nx, ny = pos
                                    if ny == 0 or _real_bay[ny-1][nx] is not None:
                                        if _real_bay[ny][nx] is None and can_place_in_stack(nx, _num_rows, _initial_bay):
                                            _real_bay[y][x] = None
                                            _real_bay[ny][nx] = container
                                            container.row = ny
                                            container.col = nx
                                            container.fit = True
                                            container.relocation_count += 1
                                            _new_lvlPlace[level].remove(pos)
                                            moved = True
                                            print(f"Moved top false container {int(container.idx)} to ({nx}, {ny})")
                                            print_final_bay_state(_real_bay)
                                            break
                            break
            if moved:
                break
        if not moved:
            break
        
# Function to place containers based on the given rules
def place_containers(_con, _num_rows, _num_cols, _container_df, _real_bay, _new_lvlPlace, _initial_bay):
    for container in _con:
        if container.idx in _container_df['idx'].values:
            level = container.level
            placed = False

            if _new_lvlPlace[level]:
                for pos in _new_lvlPlace[level]:
                    x, y = pos
                    if y == 0 or _real_bay[y-1][x] is not None:
                        if _real_bay[y][x] is None and can_place_in_stack(x, _num_rows, _initial_bay):
                            _real_bay[y][x] = container
                            container.row = y
                            container.col = x
                            container.fit = True
                            _new_lvlPlace[level].remove(pos)
                            placed = True
                            print(f"Placed container {int(container.idx)} at ({x}, {y})")
                            print_final_bay_state(_real_bay)
                            move_top_false_containers(_num_rows, _num_cols, _real_bay, _new_lvlPlace, _initial_bay)
                            break

            if not placed:
                min_level_diff = float('inf')
                best_position = None
                empty_stacks = [x for x in range(_num_rows) if all(_real_bay[y][x] is None for y in range(_num_rows))]
                
                for x in range(_num_rows):
                    for y in range(_num_rows - 1, -1, -1):
                        if _real_bay[y][x] is not None:
                            top_container = _real_bay[y][x]
                            level_diff = abs(top_container.level - level)
                            if level_diff < min_level_diff:
                                if y + 1 < _num_rows and _real_bay[y + 1][x] is None and can_place_in_stack(x, _num_rows, _initial_bay):
                                    min_level_diff = level_diff
                                    best_position = (y + 1, x)
                            break
                        elif y == 0:
                            level_diff = abs(0 - level)
                            if level_diff < min_level_diff:
                                min_level_diff = level_diff
                                best_position = (0, x)

                if best_position:
                    y, x = best_position
                    _real_bay[y][x] = container
                    container.row = y
                    container.col = x
                  
                    print(f"Placed container {int(container.idx)} at ({x}, {y}) on top of container with closest level")
                    print_final_bay_state(_real_bay)
                    move_top_false_containers(_num_rows, _num_cols, _real_bay, _new_lvlPlace, _initial_bay)

# Function to count containers violating the weight level rule
def count_weight_violations(_num_rows, _num_cols, _real_bay):
    violations = 0
    for x in range(_num_cols):
        for y in range(_num_rows - 1):
            if _real_bay[y][x] is not None and _real_bay[y + 1][x] is not None:
                if _real_bay[y][x].level > _real_bay[y + 1][x].level:
                    violations += 1
    return violations
    
# Function to visualize the final bay state
def visualize_final_bay_state(_con, _num_rows, _num_cols, _real_bay):
    fig, ax = plt.subplots(figsize=(12, 8))
    cmap = plt.get_cmap("Purples")
    max_level = max(container.level for container in _con)

    for y in range(_num_rows):
        for x in range(_num_cols):
            if _real_bay[y][x] is not None:
                container = _real_bay[y][x]
                color_intensity = (container.level + 1) / (max_level + 1)
                color = cmap(color_intensity)
                rect = plt.Rectangle((x, y), 1, 1, color=color, edgecolor='black')
                ax.add_patch(rect)
                fit_status = 'T' if container.fit else 'F'
                ax.text(x + 0.5, y + 0.5, f'({container.idx},{container.level},{fit_status})', color='white', ha='center', va='center')

    ax.set_xlabel("Stack (col)")
    ax.set_ylabel("Tier (row)")
    ax.set_title("Final Bay State Visualization")
    ax.set_xticks(range(_num_cols))
    ax.set_yticks(range(_num_rows))
    ax.set_xlim(0, _num_cols)
    ax.set_ylim(0, _num_rows)
    ax.set_yticklabels(range(_num_rows))

    plt.show()
    
def get_input_file(_folder_path):
    # Read all csv file and divide by initial and new container
    initial_file_list = []
    new_file_list = []
    ex_num = []
        
    for file_name in os.listdir(_folder_path):
        if file_name.startswith('Initial'):
            initial_file_list.append(file_name)
        elif file_name.startswith('Container'):
            new_file_list.append(file_name)
        
        match = re.search(r'ex(\d{1,2})', file_name)
        if match:
            ex_num.append(int(match.group(1)))

    print('Done Read All CSV Files')
    print('Total Number of CSV Files : ', len(initial_file_list),'\n')
    return initial_file_list, new_file_list, ex_num

def heuristic_2(_initial_file_path, _new_file_path, _num_rows, _num_cols):
    
    # Load the data
    initial_state_df = pd.read_csv(_initial_file_path)
    container_df = pd.read_csv(_new_file_path)

    # Sort container_df by seq in ascending order
    container_df = container_df.sort_values(by='seq', ascending=True)
    data1 = initial_state_df[['idx', 'group', 'emerg', 'weight', 'size(ft)']]
    zeros = [0 for _ in range(len(initial_state_df))]
    data1.insert(1, 'seq', zeros)
    data = pd.concat([data1, container_df], axis=0)
                        
                        
    con = []  # container 순서 리스트

    for i in range(len(data)):
        nowcon = data.iloc[i]
        c = Container(nowcon.idx, nowcon.seq, nowcon.group, nowcon.emerg, nowcon.weight)
        con.append(c)

    tempvalue = [d.newValue for d in con]

    # 최소 최대값 레벨 구하는 방법
    wmin = min(tempvalue)
    wmax = max(tempvalue)
    intv = 8
    interval = (wmax - wmin) // intv
    grade = [0, wmin]

    for i in range(2, intv + 1):
        grade.append(grade[i - 1] + interval)
    grade.append(wmax)

    level = []
    for i in range(len(tempvalue)):
        for j in range(len(grade)):
            if tempvalue[i] < grade[j]:
                level.append(j - 1)
                break
            elif tempvalue[i] == grade[j]:
                level.append(j)
                break

    for i in range(len(level)):
        con[i].level = level[i]
    for i in range(len(con)):
        print(con[i])

    ordCon = sorted(con, key=lambda x: x.level)  # 정렬된 순서
    for i in range(len(con)):
        print(ordCon[i])

    row = 5  # 높이
    col = 6  # stack bay
    bay = []
    lvlPlace = [[] for _ in range(10)]

    for i in range(row):
        now = [0] * col
        bay.append(now)

    idx = 0
    idy = 0
    c = 0
    for i in range(row + col - 1):
        if c == len(con): break
        if idx < row - 1:
            for j in range(idx + 1):
                if c == len(con): break
                bay[idx - j][j] = ordCon[c].level
                conid = int(ordCon[c].number)
                con[conid].row = idx - j
                con[conid].col = j
                c += 1          
            idx += 1
        elif idx >= row - 1:        
            for j in range(0, row):
                if c == len(con): break
                if idy + j == col:
                    break
                else:
                    bay[idx - j][idy + j] = ordCon[c].level
                    conid = int(ordCon[c].number)
                    con[conid].row = idx - j
                    con[conid].col = idy + j
                    c += 1  
            idy += 1

    bay.append([-1] * 6)
    # 정답 bay 출력
    for i in range(len(con)):    
        x = con[i].number  # 정렬 된 순서
        print(int(x), "level", con[int(x)].level, con[int(x)].col, con[int(x)].row)
        lv = con[int(x)].level
        lvlPlace[lv].append([con[int(x)].col, con[int(x)].row])
    print()

    for i in range(row, -1, -1):
        for j in range(col):
            print(bay[i][j], end=" ")
        print()

    for i in range(1, len(lvlPlace)):    
        lvlPlace[i].sort(key=lambda x: (-x[0], x[1]), reverse=False)
    
    for i in range(1, 10):
        print(i, end=": ")
        for j in range(len(lvlPlace[i])):
            print(lvlPlace[i][j], end=",")
        print()


    # Initialize the bay with None
    initial_bay = [[None for _ in range(col)] for _ in range(row)]

    # Create a dictionary to map idx to container objects
    con_dict = {container.idx: container for container in con}

    # Populate the initial bay with the container weights from the initial state
    for index, row in initial_state_df.iterrows():
        x = int(row['loc_x']) - 1  # Adjust x to be zero-based
        z = int(row['loc_z'])
        idx = int(row['idx'])
        weight = row['weight']  # Keep the weight as it is in the CSV
    
        if idx in con_dict:
            container = con_dict[idx]
            container.row = z
            container.col = x
            initial_bay[z][x] = container

    # Determine the fit status of each container
    for container in con:
        if container.idx in container_df['idx'].values:
            container.fit = False  # Container_ex.csv 에서 읽어온 idx들은 fit 값을 False로 설정
        elif [container.col,container.row] in lvlPlace[container.level]:
            container.fit = True

    # Print the initial state with weight, level, and fit status
    print("\nInitial State:")
    for i in range(len(initial_bay) - 1, -1, -1):
        for j in range(len(initial_bay[i])):
            if initial_bay[i][j] is not None:
                container = initial_bay[i][j]
                print(f"({int(container.idx)},{container.level},{container.fit})", end=" | ")
            else:
                print("Empty", end=" | ")
        print()

    # Printing the containers' positions and fit status
    print("\nContainer Positions and Fit Status:")
    for container in con:
        print(f"Container {int(container.idx)}: Level {container.level}, Position ({container.row}, {container.col}), Fit: {container.fit}")

    # Process each stack from top to bottom
    for x in range(_num_cols):
        y = _num_cols - 1
        while y >= 0:
            if initial_bay[y][x] is not None and (y == _num_cols - 1 or initial_bay[y + 1][x] is None):
                container = initial_bay[y][x]
                if not (container.fit and container.row == 0):  # Exclude the containers that fit and have y-coordinate as 0
                    move_container(container, initial_bay, lvlPlace, _num_rows, _num_cols)
            y -= 1

    print("\nInitial relocation done.")
    print_bay_state(initial_bay)

    # Create new_lvlPlace and update it
    new_lvlPlace = [[] for _ in range(10)]

    # Remove fit containers' positions from lvlPlace
    for container in con:
        if container.fit:
            level = container.level
            position = [container.col,container.row]
            if position in lvlPlace[level]:
                lvlPlace[level].remove(position)

    # Store remaining positions in new_lvlPlace
    for i in range(10):
        for pos in lvlPlace[i]:
            new_lvlPlace[i].append(pos)

    # Print the new_lvlPlace
    print("\nNew lvlPlace:")
    for i in range(1, 10):
        print(f"Level {i}: {new_lvlPlace[i]}")

    # Create real_bay as the final state of the bay after processing
    real_bay = [[None for _ in range(_num_cols)] for _ in range(_num_cols)]

    # Populate real_bay with the container positions from initial_bay
    for y in range(_num_cols):
        for x in range(_num_cols):
            real_bay[y][x] = initial_bay[y][x]



    # Print the final bay state
    print_final_bay_state(real_bay)

    # Execute the container placement
    place_containers(con, _num_rows, _num_cols, container_df, real_bay, new_lvlPlace, initial_bay)

    # Assuming 'real_bay' is the final state of the bay after processing
    # Create a list to store the final data
    final_data = []

    # Append containers from the initial state in their original order
    for index, row in initial_state_df.iterrows():
        idx = int(row['idx'])
        container = con_dict[idx]
        final_data.append({
            'idx': container.idx,
            'seq': container.seq,
            'group': 0,
            'emerg': container.emerg,
            'weight': container.weight,
            'new_value': container.newValue,
            'relocation': container.relocation_count,
            'loc_x': container.col + 1,
            'loc_y': 0,
            'loc_z': container.row,
            'size(ft)': 20,
        })

    # Append containers from the container CSV sorted by 'seq'
    for container in sorted(con, key=lambda x: x.seq):
        if container.idx not in initial_state_df['idx'].values:
            final_data.append({
                'idx': container.idx,
                'seq': container.seq,
                'group': 0,
                'emerg': container.emerg,
                'weight': container.weight,
                'new_value': container.newValue,
                'relocation': container.relocation_count,
                'loc_x': container.col + 1,
                'loc_y': 0,
                'loc_z': container.row,
                'size(ft)': 20,
            })

    # Create a DataFrame from the final data
    final_df = pd.DataFrame(final_data)

    # Specify the columns order to match the provided example
    final_df = final_df[['idx', 'seq', 'group', 'emerg', 'weight', 'new_value', 'relocation', 'loc_x', 'loc_y', 'loc_z', 'size(ft)']]

    # Save the DataFrame to a CSV file
    output_file_name = 'C:/minyeong/output/Initial_7,New_18/Relocation_ex28.csv'
    final_df.to_csv(output_file_name, index=False)

    print(f"CSV file has been saved as {output_file_name}")


    display(final_df)


    # Call the function to visualize the final bay state
    visualize_final_bay_state(con, _num_rows, _num_cols, real_bay)

    # Count and print the number of weight level violations
    violations = count_weight_violations(_num_rows, _num_cols, real_bay)
    print(f"Number of containers violating the weight level rule: {violations}")


def main():
    # Parameters for the bay dimensions
    num_rows = 5  # height
    num_cols = 6  # stack bay

    stack_num = 6
    tier_num = 5
    container_num = 20
    method = 'Heuristic_2'

    input_folder = f'Input_Data_{container_num}(stack_{stack_num}_tier_{tier_num})'
    output_folder = f'{method}/Output_Data_{container_num}(stack_{stack_num}_tier_{tier_num})'
    
    initial_folder_list = os.listdir(input_folder)
    
    for _initial_folder in initial_folder_list:
        
        _new_folder_list = os.listdir(os.path.join(input_folder, _initial_folder))
        
        for _new_folder in _new_folder_list:
            
            input_folder_path = os.path.join(input_folder, _initial_folder, _new_folder)
            output_folder_path = os.path.join(output_folder, 'Heuristic_2', _initial_folder, _new_folder)
            
            print('Input Folder Path : ', input_folder_path)
            print('Output Folder Path : ', output_folder_path)
            
            initial_file_names, new_file_names, experiment_idx_list = get_input_file(input_folder_path)
            
            initial_file_num = len(initial_file_names)
            
            if initial_file_num != len(new_file_names):
                print('!!! Error : Check Data folder !!!')
            
            else:
                
                for file_idx in range(initial_file_num):
                    
                    initial_file = os.path.join(os.getcwd(), input_folder_path, initial_file_names[file_idx])
                    new_file = os.path.join(os.getcwd(), input_folder_path, new_file_names[file_idx])
                    experiment_idx = experiment_idx_list[file_idx]
                
                    print('---------------- Info of Input Data ----------------')
                    print('File path of initial container : ', initial_file)
                    print('File path of new container : ', new_file)
                    print(f"Now repeat time : {experiment_idx}")
                    print(f"Result Folder : {output_folder_path}\n")   
                    
                    output_file_path = os.path.join(output_folder_path, f'Configuration_ex{experiment_idx}.csv')
                    
                    # Check exist file in folder
                    if not os.path.exists(output_file_path):
                        heuristic_2(initial_file, new_file, num_rows, num_cols)
                        
                    else:
                        print(f'Already exist result file : {output_file_path}\n')

main()        