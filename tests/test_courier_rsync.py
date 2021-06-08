# pylint: disable-all
from couriers.rsync import CourierRsync
import os
import shutil


def test_create_courier():
    courier = CourierRsync("/tmp/test_receiver")
    assert courier.receiver == "/tmp/test_receiver"


def test_delivery():
    outdir = "/tmp/test"
    receiver_dir = "/tmp/test_receiver"

    os.mkdir(outdir)
    os.mkdir(receiver_dir)

    test_file = "test1"
    with open(os.path.join(outdir, test_file), 'a'):
        pass
    courier = CourierRsync(receiver_dir)
    assert courier.delivery(test_file, outdir)
    assert len(os.listdir(outdir)) == 0
    
    os.rmdir(outdir)
    shutil.rmtree(receiver_dir)


def test_deliver_packages():
    outdir = "/tmp/test"
    receiver_dir = "/tmp/test_receiver"

    os.mkdir(outdir)
    os.mkdir(receiver_dir)

    test_files = ["test1", "test2", "test3"]
    for test_file in test_files:
        with open(os.path.join(outdir, test_file), 'a'):
            pass
    courier = CourierRsync(receiver_dir)
    processes = courier.deliver_packages(test_files, outdir)
    for process in processes:
        process.join()
    assert len(os.listdir(outdir)) == 0

    os.rmdir(outdir)
    shutil.rmtree(receiver_dir)
