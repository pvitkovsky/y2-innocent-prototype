from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    if "gw.yad2.co.il/recommendations" in flow.request.url:
        print("Captured JSON:", flow.response)