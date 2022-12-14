import unittest
from typing import Union

from cribl_stream import CriblStream
from syslog import Syslog
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

PACK = 'cribl-palo-alto-networks'
ls = CriblStream('localhost', 'admin', 'admin')
sys = Syslog('localhost', 9514)
loop = asyncio.new_event_loop()


def setUpModule():
    ls.enable_syslog_input()
    tarball = ls.create_pack_tarball()
    ls.install_pack(tarball)
    asyncio.set_event_loop(loop)


def tearDownModule():
    loop.close()
    sys.close()
    ls.delete_pack(PACK)


class SyslogTest(unittest.TestCase):
    async def capture_sample(self):
        return await loop.run_in_executor(None, ls.capture_sample, 1)

    async def run_test(self, pipeline, message, pack=None):
        t = asyncio.create_task(self.capture_sample())
        await asyncio.sleep(.25)
        sys.send(message)
        sample_data = await t
        sample_id = ls.save_sample("test.log", sample_data)
        result = ls.run_pipeline(pipeline, sample_id, pack)

        return result

    def tearDown(self) -> None:
        ls.delete_all_samples()

    def go(self, pipeline, message, pack: Union[str, None] = PACK):
        result = loop.run_until_complete(self.run_test(pipeline, message, pack))
        return result


class PanTraffic(SyslogTest):
    PIPELINE = 'pan_traffic'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", "Jan 28 01:28:35 10.23.45.67 1,2014/01/28 01:28:35,007200001056,TRAFFIC,end,1,2014/01/28 01:28:34,192.168.41.30,192.168.41.255,10.193.16.193,192.168.41.255,allow-all,,,netbios-ns,vsys1,Trust,Untrust,ethernet1/1,ethernet1/2,To-Panorama,2014/01/28 01:28:34,8720,1,137,137,11637,137,0x400000,udp,allow,276,276,0,3,2014/01/28 01:28:02,2,any,0,2076326,0x0,192.168.0.0-192.168.255.255,192.168.0.0-192.168.255.255,0,3,0", None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:traffic'})
        self.assertNotIn("Jan 28 01:28:35 10.23.45.67", result[0]['_raw'])


class PanThreat(SyslogTest):
    PIPELINE = 'pan_threat'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", "1 2022-10-11T17:19:35.782Z stream-logfwd20-718e7c5f--10111016-3fbk-harness-xb0d logforwarder - panwlogs - 2022-10-11T17:14:30.000000Z,no-serial,THREAT,vulnerability,10.0,2022-10-11T17:14:09.000000Z,10.50.123.2,10.240.120.16,,,Mobile Users to PNA-SNA Trust,xy\\alf,,ldap,vsys1,trust,inter-fw,tunnel.1,tunnel.4006,Cortex Logging,844334,1,53498,389,0,0,tcp,alert,,Microsoft Windows NTLMSSP Detection(92322),Informational,client to server,50288852,10.0.0.0-10.255.255.255,10.0.0.0-10.255.255.255,0,,,0,,,,,0,131,0,0,0,,GP cloud service,,,0,,0,1970-01-01T00:00:00.000000Z,N/A,info-leak,565386699,0x0,fd02920c-3450-4e49-b3dd-01b02f9f9cdb,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0,2022-10-11T17:14:10.583000Z,", None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:threat'})


class PanSystem(SyslogTest):
    PIPELINE = 'pan_system'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", "1,2021/07/20 23:59:02,1234567890,SYSTEM,routing,0,2021/07/20 23:59:02,,routed-config-p1-success,,0,0,general,informational,Route daemon configuration load phase-1 succeeded.,0,0x0", None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:system'})


class PanConfig(SyslogTest):
    PIPELINE = 'pan_config'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", "1,2021/07/20 23:59:02,1234567890,CONFIG,0,0,2021/07/20 00:53:40,192.168.0.1,,commit,admin,Web,Submitted,,0,0x0", None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:config'})


class PanHipMatch(SyslogTest):
    PIPELINE = 'pan_hipmatch'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", "1,2021/07/20 23:59:02,1234567890,HIPMATCH,0,2049,2021/07/20 23:59:02,xx.xx,vsys1,xx-xxxxx-MB,Mac,10.252.31.187,GP-HIP,1,profile,0,0,1052623,0x0,17,11,12,0,,xxxxx,1,0.0.0.0,", None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:hipmatch'})


class PanUserId(SyslogTest):
    PIPELINE = 'pan_userid'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", '1,2020-10-13T01:23:50.000000Z,007051000113358,USERID,login,10.0,2020-10-13T01:23:34.000000Z,vsys1,::c28:7141:ffff:0,"xxxxx\\xxxxx o"xxxxxxxxxx"\'"xxxxxxxxxx"test",fake-data-source-95,1694498816,16777216,-1694302208,63502,60246,server_session_monitor,exchange_server,551324,-9223372036854775808,0,0,0,0,,PA-VM,1,xxxxx,2050-04-13T10:41:35.000000Z,1,64,xxxxxxxxxxxxxx,,2020-10-13T01:23:35.350000Z', None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:userid'})


class PanGlobalProtect(SyslogTest):
    PIPELINE = 'pan_globalprotect'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", '1,2020-10-13T01:22:32.000000Z,007051000113358,GLOBALPROTECT,globalprotect,10.0,2020-10-13T01:22:06.000000Z,vsys1,gateway-switch-to-ssl,before-login,SAML,ipsec,xxxxx\\xxxxx xxxxx,FI,machine_name3,xxx.xx.x.xx,::c307:39c8:ffff:0,xxx.xx.x.xx,::f32b:d251:ffff:0,67:11:5a:e2:d2:32,serialno_list-1,66567,Intel Mac OS,9.3.5,16777216,Admin,,opaque_list-0,success,San Francisco,1,connect_method_list-2,0,portal_list-2,557533,-9223372036854775808,2020-10-13T01:22:07.388000Z,select_type-0,50055,medium,"gateway-5,925,1;gateway-4,196,2;gateway-5,583,1;gateway-4,996,5;gateway-1,442,2;gateway-6,121,4;gateway-0,16,1;gateway-6,173,0;gateway-2,753,0;gateway-6,651,0;gateway-3,602,3;gateway-1,55,0;gateway-1,384,2;gateway-4,871,3;gateway-3,546,5;",', None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:globalprotect'})


class PanDecryption(SyslogTest):
    PIPELINE = 'pan_decryption'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", '1,2020-10-13T01:11:23.000000Z,007051000113358,,DECRYPTION,10.0,2020-10-13T01:11:05.000000Z,xxx.xx.x.xx,xxx.xx.x.xx,xxx.xx.x.xx,xxx.xx.x.xx,deny-attackers,00000000000000000000ffff05050505,paloaltonetwork\\xxxxx,mcafee-endpoint-encryption,vsys1,ethernet4Zone-test3,datacenter,,,rs-logging,2020-10-13T01:11:05.000000Z,999250,1,28790,18368,31621,27853,3072,tcp,allow,GRE,,,,,85c1488d-5bbd-42e7-8f28-a19256972c32,unknown,unknown,TLS1.3,ECDHE,AES_128_GCM,SHA256,,sect409k1,None,Untrusted,Uninspected,Broker,14ff0117d825393ebcad2bbfb94bc282da926a7a,6263d82e0ec3d57c209151526dc1240cc19ec2e685fbae4c81f394e9819a7699,1602551466,1605143466,V2,192,23,32,32,21,64,CN = MGMT-GROUP-MGMT-CA,CN = Thawte Premium Server CA1,CN = Thawte Premium Server CA1,devop-host.panw.local,,1873cc5c-0d31,pns_default,pan-dp-77754f4,,,,,2020-10-13T01:11:06.359000Z,H-Phone,h-profile,Pro,Huawei,Mate 10,Android v6.1,pan-411,264754728121,H-Phone,h-profile,ANE-LX3,Huawei,P20 Lite,Android v7.1,pan-431,496310767571,111291,-9223372036854775808', None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:decryption'})


class PanCorrelation(SyslogTest):
    PIPELINE = 'pan_correlation'

    def test_assert_sourcetype(self):
        result = self.go(f"pack:{PACK}", '1,2021/07/20 23:59:02,012345678902,CORRELATION,,,2021/07/20 23:59:02,1.2.3.4,username,,compromised-host,medium,0,0,0,0,,us2,,beacon-heuristics,6005,"Host visited known malware URL (100 times)."', None)
        self.assertEqual(result[0], result[0] | {'index': "pan_logs", 'sourcetype': 'pan:correlation'})
