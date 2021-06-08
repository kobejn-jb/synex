# pylint: disable-all
from couriers.http import CourierHttp
import requests_mock
import shutil
import os


def test_create_courier():
    courier = CourierHttp("http://test.com")
    assert courier.receiver == "http://test.com"


def test_delivery(requests_mock):
    outdir = "/tmp/test"
    os.mkdir(outdir)
    test_file = "test1"
    with open(os.path.join(outdir, test_file), 'a'):
        pass

    courier = CourierHttp("http://test.com")
    requests_mock.post('http://test.com')
    assert courier.delivery(test_file, outdir)
    assert len(os.listdir(outdir)) == 0

    os.rmdir(outdir)


def test_deliver_packages(requests_mock):
    outdir = "/tmp/test"
    os.mkdir(outdir)
    test_files = ["test1.json", "test2.json", "test3.json"]
    for test_file in test_files:
        with open(os.path.join(outdir, test_file), 'a'):
            pass

    courier = CourierHttp("http://test.com")
    requests_mock.post('http://test.com')
    processes = courier.deliver_packages(test_files, outdir)
    for process in processes:
        process.join()
    assert len(os.listdir(outdir)) == 0
    
    os.rmdir(outdir)
