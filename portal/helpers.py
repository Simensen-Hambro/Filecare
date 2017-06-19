def get_branch_path(node, stop_parent=None, share=None):
    links = []
    if stop_parent is not None and (node.pk == stop_parent.pk):
        node.set_url(share)
        links.append(node)
        return links

    if node.parent:
        parent = node
        while parent:
            parent.set_url(share)
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


