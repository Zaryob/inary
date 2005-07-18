# the most simple minded digraph class ever

class digraph(object):

    def __init__(self):
        self.__v = set()
        self.__adj = {}
        self.__vdata = {}
        #self.__edata = {}
        
    def vertices(self):
        "return set of vertex descriptors"
        return self.__v

    def edges(self):
        "return a list of edge descriptors"
        l = []
        for u in self.__v:
            for v in self.__u:
                l.append( (u,v) )
        return l

    def from_list(self, el):
        "convert a list of edges (u,v) to graph"
        for (u,v) in el:
            self.add_edge(u,v)

    def add_vertex(self, u, data = None):
        "add vertex u, optionally with data"
        assert not u in self.__v
        self.__v.add(u)
        self.__adj[u] = set()
        if data:
            self.__vdata[u] = data

    def add_edge(self, u, v, edata = None):
        "add edge u -> v"
        if not u in self.__v:
            self.add_vertex(u)
        if not v in self.__v:
            self.add_vertex(v)
        self.__adj[u].add(v)
        #if edata != None:

    def set_vertex_data(self, u, data):
        self.__vdata[u] = data

    def vertex_data(self, u):
        return self.__vdata[u]

    def has_vertex(self, u):
        return u in self.__v

    def has_edge(self, u,v):
        if u in self.__v:
            return v in self.__adj[u]
        else:
            return False

    def adj(self, u):
        return self.__adj[u]

    def dfs(self, finish_hook = None):
        self.color = {}
        self.p = {}
        self.d = {}
        self.f = {}
        for u in self.__v:
            self.color[u] = 'w'
            self.p[u] = None
        self.time = 0
        for u in self.__v:
            if self.color[u] == 'w':
                self.dfs_visit(u, finish_hook)

    def dfs_visit(self, u, finish_hook):
        self.color[u] = 'g'
        self.d[u] = self.time = self.time + 1
        for v in self.adj(u):
            if self.color[v] == 'w':
                self.p[v] = u
                self.dfs_visit(v, finish_hook)
        self.color[u] = 'b'
        if finish_hook:
            finish_hook(u)
        self.f[u] = self.time = self.time + 1

    def topological_sort(self):
        l = []
        self.dfs(lambda u: l.append(u))
        return l

