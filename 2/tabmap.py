import pydot
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('pid')
argparser.add_argument('name')
pid = argparser.parse_args().pid
# src = open('/proc/' + pid + '/maps', 'r')
src = open(pid, 'r')
name = argparser.parse_args().name

def insert_range(branch: dict, mode: str, depth: int, addrs: tuple) -> None:
        assert mode in ('->', '<-', 'here')

        if depth == 5:
                return
        
        addr_pair = addrs[depth]

        if mode == '->':
                subtree = branch.setdefault(addr_pair[0],
                                            {'state': {'start': True,
                                                       'end': False},
                                             'branch': {}})
                subtree['state']['start'] = True
                insert_range(subtree['branch'], '->', depth + 1, addrs)
        elif mode == '<-':
                subtree = branch.setdefault(addr_pair[1],
                                            {'state': {'start': False,
                                                       'end': True},
                                             'branch': {}})
                subtree['state']['end'] = True
                insert_range(subtree['branch'], '<-', depth + 1, addrs)
        else: # mode == 'here'
                if addr_pair[0] == addr_pair[1]:
                        subtree = branch.setdefault(addr_pair[0],
                                                    {'state': {'start': False,
                                                               'end': False},
                                                     'branch': {}})
                        insert_range(subtree['branch'], 'here', depth + 1,
                                     addrs)
                        return
                
                subtree = branch.setdefault(addr_pair[0],
                                            {'state': {'start': True,
                                                       'end': False},
                                             'branch': {}})
                subtree['state']['start'] = True
                insert_range(subtree['branch'], '->', depth + 1, addrs)

                subtree = branch.setdefault(addr_pair[1],
                                            {'state': {'start': False,
                                                       'end': True},
                                             'branch': {}})
                subtree['state']['end'] = True
                insert_range(subtree['branch'], '<-', depth + 1, addrs)

def extract_pgd_index(addr: int) -> int:
        return addr >> 39

def extract_pud_index(addr: int) -> int:
        addr &= 0b111111111111111111111111111111111111111 # x39
        return addr >> 30

def extract_pmd_index(addr: int) -> int:
        addr &= 0b111111111111111111111111111111 # x30
        return addr >> 21

def extract_pte_index(addr: int) -> int:
        addr &= 0b111111111111111111111 # x21
        return addr >> 12

def extract_page_offset(addr: int) -> int:
        return addr & 0b111111111111 # x12

root = {'state': {'start': False, 'end': False}, 'branch': {}}
for line in src:
        start_str, end_str = line.strip().split(' ')[0].split('-')
        start, end = int(start_str, 16), int(end_str, 16)
        pgd = extract_pgd_index(start), extract_pgd_index(end)
        pud = extract_pud_index(start), extract_pud_index(end)
        pmd = extract_pmd_index(start), extract_pmd_index(end)
        pte = extract_pte_index(start), extract_pte_index(end)
        offs = extract_page_offset(start), extract_page_offset(end)

        addrs = pgd, pud, pmd, pte, offs
        insert_range(root['branch'], 'here', 0, addrs)

graph = pydot.Dot("tabmap", graph_type="digraph", rankdir='LR')
nodes = [[], [], [], [], []]

def node_name(depth: int, node_id: str) -> str:
        return str(depth) + '~' + node_id

def add_field(label_str: str, text: str, colored: bool,
              port: str = None) -> str:
        label_str += '<TR><TD '
        if port is not None:
                label_str += 'PORT="' + port + '" '
        if colored:
                label_str += 'BGCOLOR="orange"'
        else:
                label_str += 'BGCOLOR="white"'
        label_str += '> ' + text + ' </TD></TR>'
        return label_str

def map_nodes(node_id: str, table: dict, depth: int) -> None:
        keys = sorted(table.keys())
        label = ''
        i = 0
        while i < len(keys):
                key = keys[i]
                entry = table[key]

                if i == 0:
                        if entry['state']['end'] == True:
                                label = add_field(label, '↑', True)
                                if key != 0:
                                        label = add_field(label, '...', True)
                        else:
                                if key != 0:
                                        label = add_field(label, '...', False)
                label = add_field(label, hex(key)[2:], True, hex(key)[2:])
                if i == len(keys) - 1:
                        if entry['state']['start'] == True:
                                if depth == 4:
                                        if key != 0b111111111111:
                                                label = add_field(label, '...',
                                                                  True)
                                else:
                                        if key != 0b111111111:
                                                label = add_field(label, '...',
                                                                  True)
                                label = add_field(label, '↓', True)
                        else:
                                if depth == 4:
                                        if key != 0b111111111111:
                                                label = add_field(label, '...',
                                                                  False)
                                else:
                                        if key != 0b111111111:
                                                label = add_field(label, '...',
                                                                  False)
                else:
                        if keys[i + 1] != key + 1:
                                if entry['state']['start'] == True:
                                        label = add_field(label, '...', True)
                                else:
                                        label = add_field(label, '...', False)
                
                if depth != 4:
                        map_nodes(node_id + '-' + hex(key)[2:],
                                  entry['branch'], depth + 1)

                i += 1

        label = ('<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">' + label +
                 '</TABLE>>')

        graph.add_node(pydot.Node(node_name(depth, node_id),
                                  shape='"plaintext"', label=label))

def map_edges(node_id: str, table: dict, depth: int) -> None:
        if depth == 4:
                return

        for key, entry in table.items():
                graph.add_edge(pydot.Edge(node_name(depth, node_id) + ':"' + hex(key)[2:] +'"',
                                          node_name(depth + 1, node_id + '-' + hex(key)[2:])))
                map_edges(node_id + '-' + hex(key)[2:], entry['branch'], depth + 1)

map_nodes('root', root['branch'], 0)
map_edges('root', root['branch'], 0)

# graph.write_raw(name + '.dot')
graph.write_png(name + '.png')
