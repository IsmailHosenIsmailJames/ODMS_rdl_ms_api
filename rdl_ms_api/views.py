from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def app_info(request):
    if request.method == 'GET':
        data={
            "version":"1.7.3",
            "buildNumber":"11",
            "willForceToUpdate":True,
            "downloadLink":"https://github.com/odms/odms/releases/tag/v0.0.1",
            "downloadLinkList":[
                {
                    "architecture":"x86_64",
                    "link":"https://github.com/odms/odms/releases/tag/v0.0.1"
                },
                {
                    "architecture":"armeabi-v7a",
                    "link":"https://github.com/odms/odms/releases/tag/v0.0.1"
                },
                {
                    "architecture":"arm64-v8a",
                    "link":"https://github.com/odms/odms/releases/tag/v0.0.1"
                }
            ]
        }
    return Response({"success": True, "result": data}, status=status.HTTP_200_OK)