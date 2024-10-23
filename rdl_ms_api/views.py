from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def app_info(request):
    if request.method == 'GET':
        data={
            "version":"1.7.3",
            "buildNumber":"11",
            "forceToUpdate":True,
            "removeCacheOnUpdate":False,
            "removeDataOnUpdate":False,
            "removeCacheAndDataOnUpdate":False,
            "downloadLink":"https://github.com/IsmailHosenIsmailJames/ODMS_app_rdl_radiant/releases/download/v1.7.3/app-release.apk",
            "downloadLinkList":[
                {
                    "architecture":"x86_64",
                    "link":"https://github.com/IsmailHosenIsmailJames/ODMS_app_rdl_radiant/releases/download/v1.7.3/app-x86_64-release.apk"
                },
                {
                    "architecture":"armeabi-v7a",
                    "link":"https://github.com/IsmailHosenIsmailJames/ODMS_app_rdl_radiant/releases/download/v1.7.3/app-armeabi-v7a-release.apk"
                },
                {
                    "architecture":"arm64-v8a",
                    "link":"https://github.com/IsmailHosenIsmailJames/ODMS_app_rdl_radiant/releases/download/v1.7.3/app-arm64-v8a-release.apk"
                }
            ]
        }
    return Response({"success": True, "result": data}, status=status.HTTP_200_OK)