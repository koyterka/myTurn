import requests
import ast

URL = "http://192.168.1.10:5000"
ENDPOINT_NEW_USER = "/add-user-to-sip-exten-conf/"
ENDPOINT_SIP_FILE = "/sip-file-lookup"
ENDPOINT_USER_STATUS_RDY = "/update-status-rdy/"
ENDPOINT_USER_STATUS_BUSY = "/update-status-busy/"
ENDPOINT_PEER = "/get-peer/"
ENDPOINT_USER_IP = "/user-ip/"


def get_delete_info(req, info):
    print("{info}")
    print("request.url:", req.url)
    print("request.status_code:", req.status_code)
    print("request.headers:", req.headers)
    print("request.text:", req.text)
    print("request.request.headers:", req.request.headers)


def post_info(req):
    print("POST")
    print("request.url:", req.url)
    print("request.status_code:", req.status_code)
    print("request.headers:", req.headers)
    print("request.text:", req.text)
    print("request.body:", req.request.body)
    print("request.request.headers:", req.request.headers)


def post_new_user(user_name):
    final_endpoint = URL + ENDPOINT_NEW_USER + str(user_name)
    req = requests.post(final_endpoint)
    post_info(req)


def get_sip_file():
    final_endpoint = URL + ENDPOINT_SIP_FILE
    req = requests.get(final_endpoint)
    get_delete_info(req, "GET")


def update_user_status_rdy(user_name):
    final_endpoint = URL + ENDPOINT_USER_STATUS_RDY + str(user_name)
    req = requests.put(final_endpoint)
    get_delete_info(req, "PUT")


def update_user_status_busy(user_name):
    final_endpoint = URL + ENDPOINT_USER_STATUS_BUSY + str(user_name)
    req = requests.put(final_endpoint)
    get_delete_info(req, "PUT")


def get_peer(user_name):
    final_endpoint = URL + ENDPOINT_PEER + str(user_name)
    req = requests.get(final_endpoint)
    get_delete_info(req, "GET")


def status():
    final_endpoint = URL + "/user-status"
    req = requests.get(final_endpoint)
    get_delete_info(req, "GET")


def status2():
    final_endpoint = URL + "/pair-status"
    req = requests.get(final_endpoint)
    get_delete_info(req, "GET")


def get_user_status(user):
    final_endpoint = URL + "/user-status/" + user
    req = requests.get(final_endpoint)
    get_delete_info(req, "GET")


def de(user_name):
    final_endpoint = URL + "/delete-user/" + str(user_name)
    req = requests.delete(final_endpoint)
    get_delete_info(req, "GET")









def get_user_status_value(u_name):
    final_endpoint = URL + "/user-status/" + u_name
    req = requests.get(final_endpoint)
    return req.text


def get_peer_info(user_name):
    final_endpoint = URL + ENDPOINT_PEER + str(user_name)
    req = requests.get(final_endpoint)
    d = ast.literal_eval(req.text)
    return d

def get_user_ip(u_name):
    final_endpoint = URL + ENDPOINT_USER_IP + u_name
    req = requests.get(final_endpoint)
    return req.text


if __name__ == '__main__':
    u_name = "zyj1"
    u2_name = "zyj2"
    u3_name = "zyj3"

    print(get_user_ip(u_name))
    post_new_user(u_name)
    post_new_user(u2_name)
    post_new_user(u3_name)

    update_user_status_rdy(u_name)
    update_user_status_rdy(u2_name)
    update_user_status_rdy(u3_name)

    get_peer(u_name)
    get_peer(u2_name)
    get_peer(u3_name)