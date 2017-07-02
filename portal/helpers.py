def get_branch_path(node, stop_parent=None):
    links = []
    if stop_parent is not None and (node.pk == stop_parent.pk):
        links.append(node)
        return links

    if node.parent:
        parent = node
        while parent:
            if parent.parent:
                links.append(parent)
                parent = parent.parent
            else:
                links.append(parent)
                break

    else:
        links.append(node)
    links.reverse()
    return links


