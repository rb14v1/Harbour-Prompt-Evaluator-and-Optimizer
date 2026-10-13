class SimpleCORSMiddleware:
    """Simple CORS middleware that allows any localhost origin"""

    def __init__(self, get_response):
        self.get_response = get_response
        print("[OK] SimpleCORSMiddleware initialized")

    def __call__(self, request):
        response = self.get_response(request)

        origin = request.META.get('HTTP_ORIGIN', '')
        path = request.path

        print(f"[CORS] Path: {path}, Origin: {origin}")

        # Allow any localhost origin
        if origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:'):
            print(f"[CORS] OK Adding headers for origin: {origin}")
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
        else:
            print(f"[CORS] BLOCKED Origin doesn't match: {origin}")

        return response
