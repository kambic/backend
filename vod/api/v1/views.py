"""
-------------------------------
Function-Based API Views (FBV)
-------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sample_api_view(request):

    if request.method == 'GET':
        data = {"message": "This is a GET response"}
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = {"message": "This is a POST response"}
        return Response(data, status=status.HTTP_201_CREATED)

-------------------------------
Class-Based API Views (CBV)
-------------------------------
class SampleAPIView(APIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "This is a GET response from CBV"}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        ...

    def put(self, request, *args, **kwargs):
        ...

    def delete(self, request, *args, **kwargs):
        ...
"""

# views.py

from rest_framework import viewsets

from .serializers import *

import shutil
from pathlib import Path
from django.http import FileResponse
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import mimetypes


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    lookup_field = 'slug'


class VueFinderViewSet(viewsets.ViewSet):
    BASE_DIR = Path('/export/isilj/fenix2')

    def get_path(self, path: str):
        if not path.startswith("local://public"):
            raise ValueError("Invalid path prefix")
        rel_path = path[len("local://public") :].lstrip("/")
        return self.BASE_DIR / rel_path

    def to_vuefinder_item(self, fs_path: Path, rel_path: str):
        stat = fs_path.stat()
        is_dir = fs_path.is_dir()

        return {
            "name": fs_path.name,
            "path": f"local://public/{rel_path}".replace("//", "/"),
            "type": "dir" if is_dir else "file",
            "extension": "" if is_dir else fs_path.suffix.lstrip("."),
            "size": 0 if is_dir else stat.st_size,
            "last_modified": int(stat.st_mtime),
        }

    def list(self, request, *args, **kwargs):
        print(args, kwargs)
        path = request.query_params.get("path", "local://public/")
        preview = request.query_params.get("preview")
        try:
            fs_path = self.get_path(path)
            if not fs_path.exists():
                return Response({"error": "Path not found"}, status=status.HTTP_404_NOT_FOUND)

            if fs_path.is_file():
                return FileResponse(open(fs_path, "rb"), content_type=mimetypes.guess_type(fs_path)[0]) if preview else FileResponse(open(fs_path, "rb"), as_attachment=True, filename=fs_path.name)

            items = []
            for item in sorted(fs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                rel_item_path = str(fs_path.relative_to(self.BASE_DIR) / item.name)
                items.append(self.to_vuefinder_item(item, rel_item_path))

            return Response(
                {
                    "adapter": "local",
                    "path": path.rstrip("/"),
                    "dirname": fs_path.name if fs_path != self.BASE_DIR else "public",
                    "files": items,
                    "storages": ["local"],
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def upload(self, request):
        path = request.data.get("path", "local://public/")
        fs_path = self.get_path(path)
        fs_path.mkdir(parents=True, exist_ok=True)
        uploaded_files = []

        for file in request.FILES.getlist("files"):
            file_path = fs_path / file.name
            default_storage.save(str(file_path), file)
            rel_path = str(file_path.relative_to(self.BASE_DIR))
            uploaded_files.append(self.to_vuefinder_item(file_path, rel_path))

        return Response({"files": uploaded_files})

    @action(detail=False, methods=["delete"])
    def delete(self, request):
        paths = request.data.get("items", [])
        deleted = []
        for item_path in paths:
            try:
                fs_path = self.get_path(item_path)
                if fs_path.is_dir():
                    shutil.rmtree(fs_path)
                else:
                    fs_path.unlink()
                deleted.append(item_path)
            except Exception:
                continue
        return Response({"deleted": deleted})

    @action(detail=False, methods=["patch"])
    def patch(self, request):
        action_type = request.data.get("action")
        if action_type == "rename":
            old_path = self.get_path(request.data["item"])
            new_path = old_path.parent / request.data["newName"]
            old_path.rename(new_path)
            return Response({"path": f"local://public/{new_path.relative_to(self.BASE_DIR)}"})

        elif action_type in ["move", "copy"]:
            target = self.get_path(request.data["target"])
            results = []
            for item_path in request.data["items"]:
                src = self.get_path(item_path)
                dst = target / src.name
                if action_type == "move":
                    shutil.move(str(src), str(dst))
                else:
                    if src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                results.append(f"local://public/{dst.relative_to(self.BASE_DIR)}")
            return Response({"paths": results})

        return Response({"error": "Unknown action"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"])
    def put(self, request):
        action_type = request.data.get("action")
        if action_type == "create-folder":
            path = self.get_path(request.data["path"])
            folder = path / request.data["name"]
            folder.mkdir()
            return Response(self.to_vuefinder_item(folder, str(folder.relative_to(self.BASE_DIR))))

        elif action_type == "save":
            path = self.get_path(request.data["path"])
            path.write_text(request.data["content"], encoding="utf-8")
            return Response(self.to_vuefinder_item(path, str(path.relative_to(self.BASE_DIR))))

        return Response({"error": "Unknown action"}, status=status.HTTP_400_BAD_REQUEST)
