import asyncio
import threading
import concurrent

import streamlit
from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from streamlit.runtime.runtime import Runtime, RuntimeConfig, SessionClient

import time

SCRIPT_PATH = "runtime_example_script.py"


class ExampleClient(SessionClient):
    """Example SessionClient implementation. The Snowflake implementation
    should write each ForwardMsg to the session's websocket.
    """

    def write_forward_msg(self, msg: ForwardMsg) -> None:
        print(f"ExampleClient got ForwardMsg: {msg.WhichOneof('type')}")


def create_rerun_msg() -> BackMsg:
    msg = BackMsg()
    msg.rerun_script.query_string = ""
    return msg


# async def main():
#     print(f"Starting Runtime Example")

#     streamlit._is_running_with_streamlit = True

#     config = RuntimeConfig(SCRIPT_PATH, "")
#     runtime = Runtime(config)

#     # Create a Future that will be resolved when the Runtime is ready
#     # to receive new sessions.
#     runtime_started = asyncio.get_running_loop().create_future()

#     def on_runtime_started():
#         runtime_started.set_result(None)

#     async def example_app():
#         # Wait for the Runtime to be ready for new sessions
#         await runtime_started

#         # Add a session
#         session_id = runtime.create_session(ExampleClient(), {})

#         # Send a BackMsg (these will arrive from the frontend - you shouldn't
#         # need to construct them manually, just pass them on to the appropriate
#         # session)
#         runtime.handle_backmsg(session_id, create_rerun_msg())

#         print("Sleeping for a few seconds...")
#         await asyncio.sleep(3)

#         # Close the session
#         runtime.close_session(session_id)

#         print("stopping...")
#         runtime.stop()

#     # Run two coroutines in parallel: the first task runs the Runtime,
#     # and the second creates a session, waits a few seconds, and then shuts
#     # down the Runtime. This demonstrates how to we run and communicate with
#     # the Streamlit Runtime without needing to create an additional thread.
#     await asyncio.wait(
#         [
#             asyncio.create_task(runtime.run(on_runtime_started)),
#             asyncio.create_task(example_app()),
#         ],
#         return_when=asyncio.FIRST_EXCEPTION,
#     )


# asyncio.run(main())


class StreamlitInSnowflake:
  def run(self):
    config = RuntimeConfig(SCRIPT_PATH, "")
    self._runtime = Runtime(config)
    self._eventloop = asyncio.get_event_loop()
    # asyncio.set_event_loop(self._eventloop)
    # self._eventloop.run_in_executor
    self._runtime_started = self._eventloop.create_future()

    def on_runtime_started():
        self._runtime_started.set_result(None)
    
    def start(loop):
        # asyncio.set_event_loop(loop)
        print("start")
        loop.run_until_complete(self._runtime.run(on_runtime_started))
        # asyncio.run_coroutine_threadsafe(self._runtime.run(on_runtime_started), loop)
        # loop.run_forever()

    t = threading.Thread(target=start, args=(self._eventloop,), name="Sis.RunThread", daemon=True)
    t.start()
    return self._runtime
    # time.sleep(1)
    # # Create a limited thread pool.
    # executor = concurrent.futures.ThreadPoolExecutor(
    #     max_workers=2,
    # )
    # self._eventloop.run_in_executor(executor, start)


  def create_session(self):
    # self._eventloop.run_until_complete(self._runtime_started)
    while self._runtime_started.done() is False:
        time.sleep(1)
    self.session_id = self._runtime.create_session(ExampleClient(), {})

  def handle_backmsg(self):
    self._eventloop.call_soon_threadsafe(self._runtime.handle_backmsg, self.session_id, create_rerun_msg())
    # self._runtime.handle_backmsg(self.session_id, create_rerun_msg())

  def close_session(self):
    self._runtime.close_session(self.session_id)

sis = StreamlitInSnowflake()
runtime = sis.run()
sis.create_session()
time.sleep(1)
sis.handle_backmsg()
time.sleep(3)
sis.close_session()
runtime.stop()

