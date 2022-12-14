import os
import ndjson
import requests
import logging
import uuid
import tarfile
import io
from json import JSONDecodeError
from typing import Union
from pathlib import Path


logger = logging.getLogger(__name__)


class CriblStream:
    def __init__(self, host, username, password, port=9000):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

        self.token = self.get_token()

    def _call(self, method: str, endpoint: str, pack: str = None, payload: dict = None, data: bytes = None,
              headers: dict = None, params: dict = None, files: dict = None, authenticated: bool = True):
        url = f"http://{self.host}:{self.port}/api/v1{'/p/' + pack if pack else ''}{endpoint}"

        hdr = headers or {}

        if authenticated:
            hdr.update({"authorization": f"Bearer {self.token}"})

        # shortcut for having requests.get, requests.post, request.delete, etc.
        response = getattr(requests, method)(url, headers=hdr, params=params, files=files, data=data, json=payload)

        try:
            return response.json()
        except JSONDecodeError:
            # Live capture gets returned as NDJSON
            return response.json(cls=ndjson.Decoder)
        except Exception:
            return response.content

    def get_token(self):
        payload = {
            "username": self.username,
            "password": self.password
        }

        response = self._call("post", "/auth/login", payload=payload, authenticated=False)

        return response["token"]

    def enable_syslog_input(self):
        config = self._call("get", "/system/inputs/in_syslog")

        config = list(filter(lambda item: item['id'] == 'in_syslog', config['items']))[0]

        config['disabled'] = False

        self._call("patch", "/system/inputs/in_syslog", payload=config)

    def capture_sample(self, duration=3, max_events=10):
        payload = {
            "filter": "__inputId.startsWith('syslog:in_syslog')",
            "duration": duration,
            "maxEvents": max_events,
            "level": "0"
        }

        response = self._call("post", "/system/capture", payload=payload)

        # Wrap response in array if bare object
        if isinstance(response, dict):
            return [response]

        return response

    def save_sample(self, name: str, sample: [dict]):
        payload = {
            "sampleName": name,
            "context": {
                "events": sample
            }
        }

        response = self._call("post", "/system/samples", payload=payload)

        return response['items'][0]['id']

    def delete_sample(self, sample_id: str):
        samples = self._call("get", f"/system/samples/{sample_id}")
        self._call("delete", f"/system/samples/{sample_id}", payload=samples['items'][0])

    def delete_all_samples(self):
        samples = self._call("get", "/system/samples")
        samples = list(filter(lambda item: 'isTemplate' not in item, samples["items"]))

        for s in samples:
            self._call("delete", f"/system/samples/{s['id']}", payload=s)

    def run_pipeline(self, pipeline: str, sample: str, pack: str = None):
        payload = {
            "mode": "pipe",
            "pipelineId": pipeline,
            "level": 3,
            "sampleId": sample,
            "dropped": True,
            "cpuProfile": False,
            "timeout": 10000,
            "memory": 2048
        }

        response = self._call("post", "/preview", pack=pack, payload=payload)

        return response['items']

    @staticmethod
    def create_pack_tarball():
        """
        Creates an in-memory gzipped tarball containing the pack contents.

        :return: Byte array of the tarball
        """
        def pack_filter(tarinfo):
            # Filter out junk directories to be excluded from the pack
            if os.path.basename(tarinfo.name) in ['.git', '.github', 'tests', 'venv', '.DS_Store', '.idea', 'test']:
                return None

            # Reset user information
            tarinfo.uid = tarinfo.gid = 0
            tarinfo.uname = tarinfo.gname = "root"

            return tarinfo

        file = io.BytesIO()
        with tarfile.open(fileobj=file, mode="w:gz") as tar:
            parent = Path(__file__).parent.parent
            tar.add(parent, filter=pack_filter, arcname='')

        file.seek(0)
        return file.read()

    def install_pack(self, file: Union[str, bytes]):
        response = None

        # If file is a string, it should be a path on disk to tarball
        if isinstance(file, str):
            qs = {
                'filename': os.path.basename(file),
                'size': os.stat(file).st_size
            }

            with open(file, 'rb') as f:
                response = self._call("put", "/packs", params=qs, data=f.read())

        # If file is a byte array, then generate a random file name, upload, and install
        elif isinstance(file, bytes):
            qs = {
                'filename': f"{str(uuid.uuid4())}.crbl",
                'size': len(file)
            }

            response = self._call("put", "/packs", params=qs, data=file)

        if response:
            self._call("post", "/packs", payload=response)

    def delete_pack(self, name: str):
        response = self._call("get", f"/packs/{name}")

        if response:
            self._call("delete", f"/packs/{name}", payload=response)
