from django.shortcuts import render
from filecare.models import Node

def list_view(request, uuid):
	node = Node.objects.get(uuid=uuid)

	children = Node.objects.filter(parent=node)

	context = {
		'node': node,
		'children': children,
	}

	return render(request, 'filecare/index.html', context)