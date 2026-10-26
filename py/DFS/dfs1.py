graf = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

visited = set() # kenapa harus set()?
tujuan = "F"

def dfs(node, graf, visited):
    if node not in visited:
        print(node, end=" ") # maksud node, end=" "?
        visited.add(node)
        if node == tujuan:
            print(f"\n Sudah ketemu di {node}")
            return True
        for masuk in graf[node]:
            if dfs(masuk, graf, visited): # maksudnya apa bang mesi?
                return True 
        
dfs("A", graf, visited)