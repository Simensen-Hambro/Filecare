from django.shortcuts import render

from filecare.models import Node


def list_view(request, uuid):
    node = Node.objects.get(uuid=uuid)

    children = Node.objects.filter(parent=node).order_by('-directory', 'absolute_path')


    links = []
    if node.parent:
        parent = node

        while parent:
            if parent.parent:
                links.insert(0, {'name': parent.get_filename(), 'uuid': parent.uuid})
                parent = parent.parent
            else:
                links.insert(0, {'name': 'Root', 'uuid': parent.uuid})
                break

    else:
        links.insert(0, {'name': 'Root', 'uuid': node.uuid})

    context = {
        'node': node,
        'children': children,
        'links': links,
    }

    return render(request, 'filecare/index.html', context)


def list_root(request):
    node = Node.objects.filter(parent=None).first()
    children = Node.objects.filter(parent=node)



    context = {
        'node': node,
        'children': children,

    }

    return render(request, 'filecare/browse.html', context)


