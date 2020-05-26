import pytest

from testandconquer.client import MessageType
from testandconquer.model import Location, Report, Schedule, SuiteItem
from testandconquer.scheduler import Scheduler

from tests.mock.client import MockClient
from tests.mock.settings import MockSettings


@pytest.mark.asyncio()
async def test_reply_to_config_message():
    class MockSerializer:
        @staticmethod
        def serialize_config(settings, worker_id):
            return (settings, worker_id)

    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, client, [], 'my_worker_id', MockSerializer)

    await scheduler.on_server_message(MessageType.Config.value, None)

    assert client.received == [
        (MessageType.Config, (settings, 'my_worker_id')),
    ]

    await scheduler.stop()


@pytest.mark.asyncio()
async def test_reply_to_schedule_message():
    class MockSerializer:
        @staticmethod
        def deserialize_schedule(payload):
            return payload

    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, client, [], 'my_worker_id', MockSerializer)

    await scheduler.on_server_message(MessageType.Schedule.value, '<batches>')

    assert await scheduler.next() == Schedule(batches='<batches>')

    await scheduler.stop()


@pytest.mark.asyncio()
async def test_reply_to_suite_message():
    class MockSerializer:
        @staticmethod
        def serialize_suite(suite_items):
            return suite_items

    settings = MockSettings({})
    client = MockClient(settings)
    suite_items = [SuiteItem('test', Location('tests/IT/stub/stub_A.py', 'stub_A', 'TestClass', 'test_A', 1))]
    scheduler = Scheduler(settings, client, suite_items, 'my_worker_id', MockSerializer)

    await scheduler.on_server_message(MessageType.Suite.value, None)

    assert client.received == [
        (MessageType.Suite, suite_items),
    ]

    await scheduler.stop()


@pytest.mark.asyncio()
async def test_reply_to_exit_message():
    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, client, [], 'my_worker_id')
    assert scheduler.more is True

    await scheduler.on_server_message(MessageType.Done.value, None)

    assert scheduler.more is False

    await scheduler.stop()


@pytest.mark.asyncio()
async def test_report():
    class MockSerializer:
        @staticmethod
        def serialize_report(report):
            return report

    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, client, [], 'my_worker_id', MockSerializer)

    report = Report('<items>', None, None, None)
    await scheduler.report(report)

    await scheduler.stop()  # flushes reports

    assert client.received == [
        (MessageType.Report, report),
    ]