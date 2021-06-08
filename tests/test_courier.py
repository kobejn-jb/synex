# pylint: disable-all
from couriers.courier import Courier


def test_create_courier():
    courier = Courier("http://127.0.0.1")
    assert courier.receiver == "http://127.0.0.1"


def test_delivery():
    outdir = "/test"
    test_file = "test1"
    courier = Courier("http://127.0.0.1")
    assert courier.delivery(test_file, outdir)


def test_deliver_packages():
    outdir = "/test"
    test_files = ["test1", "test2", "test3"]
    courier = Courier("http://127.0.0.1")
    courier.deliver_packages(test_files, outdir)
    # assert courier.deliver_packages(test_files, outdir)
