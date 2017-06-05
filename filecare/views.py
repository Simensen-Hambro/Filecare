from django.shortcuts import render
from filecare.models import Node

def list_view(request, uuid):
	node = Node.objects.get(uuid=uuid)

	children = Node.objects.filter(parent=node).order_by('-directory', 'absolute_path')

	context = {
		'node': node,
		'children': children,
	}

	return render(request, 'filecare/index.html', context)

def list_root(request):
	node = Node.objects.filter(parent=None).first()

	print(node.uuid)

	children = Node.objects.filter(parent=node)
	print(children)

	context = {
		'node': node,
		'children': children,
	}

	return render(request, 'filecare/index.html', context)