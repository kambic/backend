"""
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelName
        fields = '__all__'

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return attrs
"""

from rest_framework import serializers

from ...models import *


class FileItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    is_dir = serializers.BooleanField()
    size = serializers.IntegerField(required=False, allow_null=True)
    modified = serializers.DateTimeField(required=False, allow_null=True)


class BreadcrumbItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()  # relative path
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        # Build full API URL for this breadcrumb level
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/files/{obj['path']}/".rstrip('/'))
        return f"/api/files/{obj['path']}/".rstrip('/')


# MIME type mapping for stream protocols
MIME_TYPE_MAPPING = {
    'dash': 'application/dash+xml',
    'hls': 'application/vnd.apple.mpegurl',  # Optional: example for HLS
    'mss': 'application/vnd.ms-sstr+xml',  # Optional: example for MSS
    # Add more mappings as needed
}


class StreamSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField()
    protocol = serializers.SerializerMethodField()  # New field for MIME type

    class Meta:
        model = Stream
        fields = ['uri', 'stream_protocol', 'protocol']

    def get_uri(self, obj):
        return f"http://ew-backend-01.tv.telekom.si{obj.uri}" if obj.uri else None

    def get_protocol(self, obj):
        return MIME_TYPE_MAPPING.get(obj.stream_protocol, obj.stream_protocol)


class EdgeSerializer(serializers.ModelSerializer):
    streams = StreamSerializer(many=True)
    dash = serializers.SerializerMethodField()

    class Meta:
        model = Edge
        fields = ['pk', 'title', 'streams', 'dash']

    def get_dash(self, obj):
        dash_stream = next((stream for stream in obj.streams.all() if stream.stream_protocol == 'dash'), None)
        if dash_stream:
            return StreamSerializer(dash_stream).data
        return None


class ProviderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Provider
        fields = ['url', 'name', 'vidra_task', 'queue', 'slug']
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
