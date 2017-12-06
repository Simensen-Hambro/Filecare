## Node, browse  (read only)
Node *4f10f01 is visited, its children are returned along with the nodes on the path to 4f10f01 (levels). GET,URL:

    /browse/93c60f2c-2216-460b-ac77-58cd44f10f01/
Response:


    {
    "size": "0 B",
    "id": "93c60f2c-2216-460b-ac77-58cd44f10f01",
    "filename": "com.apple.launchd.OmRLGg2T30",
    "children": [
        {
            "size": "0 B",
            "filename": "Listeners",
            "id": "52c38a6a-6884-4878-a3cd-34704d11d6e6",
            "directory": false,
            "url": "http://0.0.0.0:8000/intermediate/52c38a6a-6884-4878-a3cd-34704d11d6e6/"
        }
    ],
    "url": "http://0.0.0.0:8000/browse/93c60f2c-2216-460b-ac77-58cd44f10f01/",
    "levels": [
        {
            "size": "41 kB",
            "filename": "tmp",
            "id": "50b7dba5-a9ca-4f91-9d45-2931c5ab1611",
            "directory": true,
            "url": "http://0.0.0.0:8000/browse/50b7dba5-a9ca-4f91-9d45-2931c5ab1611/"
        },
        {
            "size": "0 B",
            "filename": "com.apple.launchd.OmRLGg2T30",
            "id": "93c60f2c-2216-460b-ac77-58cd44f10f01",
            "directory": true,
            "url": "http://0.0.0.0:8000/browse/93c60f2c-2216-460b-ac77-58cd44f10f01/"
        }
        ]
    }

Size, ID, filename and URL are for the current node. Levels provides a basis for breadcrumbs.

A child node that is a file (directory=False) will have the following URL instead, and redirects to the actual file download:

    /intermediate/cb3b1cd3-1f62-4a85-bd94-4de34ca785cd/"

## Shared node, create
POST, URL:

    /share/

Payload:

    {
    "node":"50b7dba5-a9ca-4f91-9d45-2931c5ab1611",
    }

GET, URL:

    /share/1b709aea-d219-467e-b1d4-9691cb96804f/
    
The payload may also contain a expiration date for the share. 

Response:

    {
    "token": "1b709aea-d219-467e-b1d4-9691cb96804f",
    "expiration": "2017-12-07T19:06:08.677176Z",
    "children": [],
    "levels": [
        {
            "size": "41 kB",
            "filename": "tmp",
            "id": "50b7dba5-a9ca-4f91-9d45-2931c5ab1611",
            "directory": true,
            "url": "http://0.0.0.0:8000/share/1b709aea-d219-467e-b1d4-9691cb96804f/50b7dba5-a9ca-4f91-9d45-2931c5ab1611/"
        },
        {
            "size": "0 B",
            "filename": "powerlog",
            "id": "52975e76-0c9c-436f-b5fb-ff6b4b24a298",
            "directory": true,
            "url": "http://0.0.0.0:8000/share/1b709aea-d219-467e-b1d4-9691cb96804f/52975e76-0c9c-436f-b5fb-ff6b4b24a298/"
        }
    ],
    "user": 1,
    "url": "http://0.0.0.0:8000/share/1b709aea-d219-467e-b1d4-9691cb96804f/"
    }
   
