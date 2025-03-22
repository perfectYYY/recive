import unittest
import hashlib
import time
import jwt
import requests


class TestDataServer(unittest.TestCase):
    # 初始化测试
    def setUp(self):
        self.base_url = "http://127.0.0.1:5001"
        self.device_id = "20845"
        self.secret = "abcde"

    ############################测试：1.取Ticket票##############################################
    def test_get_ticket_missing_device_id(self):
        response = requests.get(f"{self.base_url}/getTicket")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 201)

    def test_get_ticket_unknown_device_id(self):
        response = requests.get(f"{self.base_url}/getTicket?deviceId=unknown")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 202)

    def test_get_ticket_success(self):
        response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 200)
        self.assertIn("ticket", response.json()["data"])
        self.token=response.json()["data"]["ticket"]

    # ############################测试：2.取Token##############################################
    def test_get_token_missing_parameters(self):
        response = requests.post(f"{self.base_url}/getToken", json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 201)

    def test_get_token_unknown_device_id(self):
        data = {"deviceId": "unknown", "signature": "test", "ticket": "test"}
        response = requests.post(f"{self.base_url}/getToken", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 202)

    def test_get_token_invalid_signature(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        data = {"deviceId": self.device_id, "signature": "invalid_signature", "ticket": ticket}
        response = requests.post(f"{self.base_url}/getToken", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 203)

    def test_get_token_success(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        signature = hashlib.md5((ticket + self.device_id + self.secret).encode('utf-8')).hexdigest()
        data = {"deviceId": self.device_id, "signature": signature, "ticket": ticket}
        response = requests.post(f"{self.base_url}/getToken", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 200)
        self.assertIn("token", response.json()["data"])

    # ############################测试：3.上传血压数据##############################################
    def test_upload_data_missing_parameters(self):
        response = requests.post(f"{self.base_url}/uploadData", json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 201)

    def test_upload_data_unknown_device_id(self):
        data = {"deviceId": "unknown", "token": "test", "data": {"time": int(time.time()), "high": 120, "low": 80}}
        response = requests.post(f"{self.base_url}/uploadData", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 202)

    def test_upload_data_invalid_token(self):
        data = {"deviceId": self.device_id, "token": "invalid_token", "data": {"time": int(time.time()), "high": 120, "low": 80}}
        response = requests.post(f"{self.base_url}/uploadData", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 204)

    def test_upload_data_expired_token(self):
        expired_payload = {"deviceId": self.device_id, "expiredTime": int(time.time()) - 120}
        expired_token = jwt.encode(expired_payload, self.secret, algorithm="HS256")
        data = {"deviceId": self.device_id, "token": expired_token, "data": {"time": int(time.time()), "high": 120, "low": 80}}
        response = requests.post(f"{self.base_url}/uploadData", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 206)

    def test_upload_data_invalid_blood_pressure(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        signature = hashlib.md5((ticket + self.device_id + self.secret).encode('utf-8')).hexdigest()
        token_response = requests.post(f"{self.base_url}/getToken", json={"deviceId": self.device_id, "signature": signature, "ticket": ticket})
        token = token_response.json()["data"]["token"]
        data = {"deviceId": self.device_id, "token": token, "data": {"time": "2023-01-01", "high": 80, "low": 120}}
        response = requests.post(f"{self.base_url}/uploadData", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 205)

    def test_upload_data_success(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        signature = hashlib.md5((ticket + self.device_id + self.secret).encode('utf-8')).hexdigest()
        token_response = requests.post(f"{self.base_url}/getToken", json={"deviceId": self.device_id, "signature": signature, "ticket": ticket})
        token = token_response.json()["data"]["token"]
        data = {"deviceId": self.device_id, "token": token, "data": {"time": "2023-01-01", "high": 120, "low": 80}}
        response = requests.post(f"{self.base_url}/uploadData", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 200)
        self.assertIn("receivedTime", response.json()["data"])

    # ############################测试：4.刷新Token##############################################
    def test_refresh_token_missing_parameters(self):
        response = requests.post(f"{self.base_url}/refreshToken", json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 201)

    def test_refresh_token_unknown_device_id(self):
        data = {"deviceId": "unknown", "signature": "test", "token": "test"}
        response = requests.post(f"{self.base_url}/refreshToken", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 202)

    def test_refresh_token_invalid_signature(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        data = {"deviceId": self.device_id, "signature": "invalid_signature", "token": "test", "ticket": ticket}
        response = requests.post(f"{self.base_url}/refreshToken", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 203)

    def test_refresh_token_max_refresh(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        signature = hashlib.md5((ticket + self.device_id + self.secret).encode('utf-8')).hexdigest()
        token_response = requests.post(f"{self.base_url}/getToken", json={"deviceId": self.device_id, "signature": signature, "ticket": ticket})
        token = token_response.json()["data"]["token"]
        signature = hashlib.md5((token + self.device_id + self.secret).encode('utf-8')).hexdigest()
        refresh_response = requests.post(f"{self.base_url}/refreshToken", json={"deviceId": self.device_id, "signature": signature, "token": token})
        token=refresh_response.json()["data"]["token"]
        signature = hashlib.md5((token + self.device_id + self.secret).encode('utf-8')).hexdigest()
        second_refresh_response = requests.post(f"{self.base_url}/refreshToken", json={"deviceId": self.device_id, "signature": signature, "token": token})
        self.assertEqual(second_refresh_response.status_code, 200)
        self.assertEqual(second_refresh_response.json()["code"], 207)

    def test_refresh_token_success(self):
        ticket_response = requests.get(f"{self.base_url}/getTicket?deviceId={self.device_id}")
        ticket = ticket_response.json()["data"]["ticket"]
        signature = hashlib.md5((ticket + self.device_id + self.secret).encode('utf-8')).hexdigest()
        token_response = requests.post(f"{self.base_url}/getToken", json={"deviceId": self.device_id, "signature": signature, "ticket": ticket})
        token = token_response.json()["data"]["token"]
        signature = hashlib.md5((token + self.device_id + self.secret).encode('utf-8')).hexdigest()
        refresh_response = requests.post(f"{self.base_url}/refreshToken", json={"deviceId": self.device_id, "signature": signature, "token": token})
        self.assertEqual(refresh_response.status_code, 200)
        self.assertEqual(refresh_response.json()["code"], 200)
        self.assertIn("token", refresh_response.json()["data"])

if __name__ == '__main__':
    unittest.main()