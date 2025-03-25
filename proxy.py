from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    print(flow.request.url)
    print(flow.response)
    # if "gw.yad2.co.il/recommendations" in flow.request.url:
    #     print("Captured JSON:", flow.response)
    # if "https://gw.yad2.co.il/realestate/rent?" in flow.request.url:
    #     print("Captured JSON:", flow.response)